#    Copyright (C) 2018 by Bitonic B.V.
#
#    This file is part of Fireworks.
#
#    Fireworks is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Fireworks is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Fireworks. If not, see <http://www.gnu.org/licenses/>.

import os.path
import logging
import json

from utils.struct import Struct

from .backend_base import Invoice, InvoiceData, Payment, Channel, Peer
from .backend_base import Backend as Backend_Base
from .lightningd.lightning import LightningRpc



def translateRPCExceptions(method):
    def newMethod(self, *args, **kwargs):
        try:
            return method(self, *args, **kwargs)
        except (ConnectionRefusedError, ConnectionResetError) as e:
            raise self.NotConnected(str(e))
    return newMethod



class Backend(Backend_Base):
    class ChannelID(Struct):
        peerID = None #str


    def __init__(self, config):
        logging.info('Using Lightningd back-end')
        self.config = config


    def setFrontend(self, frontend):
        pass #unused


    def startup(self):
        lightningDir = self.config.getValue('lightningd', 'dir')
        lightningDir = os.path.expanduser(lightningDir)
        lightningDir = os.path.abspath(lightningDir)
        socketFile = os.path.join(lightningDir, 'lightning-rpc')
        self.rpc = LightningRpc(socketFile)
        self.initNodeInfo()


    def getBackendName(self):
        '''
        Arguments:
        Returns: str
        Exceptions:
            Backend.NotConnected: not connected to the backend
        '''
        if self.nodeInfo is None and not self.initNodeInfo():
            raise Backend.NotConnected()
        return 'Lightningd ' + self.nodeInfo['version']


    def initNodeInfo(self):
        #Cached:
        try:
            self.nodeInfo = self.rpc.getinfo()
        except (ConnectionRefusedError, ConnectionResetError):
            self.nodeInfo = None
            return False

        return True


    def isConnected(self):
        return self.initNodeInfo()


    @translateRPCExceptions
    def runCommand(self, cmd, *args):
        '''
        Arguments:
            cmd: str
                command to be executed
            *args: [str, [...]]
                command arguments (backend-specific format)
        Returns: Any structure of list, dict, str, int, float
            The output of the command
        Exceptions:
            Backend.CommandFailed: the command failed
            Backend.NotConnected: not connected to the backend
        '''

        #In this back-end, the format is "<name>=<JSON>" or "<name>=<str>"
        kwargs = {}
        for a in args:
            try:
                isPos = a.index('=')
            except ValueError:
                raise Backend.CommandFailed(
                    'Argument \"%s\" does not conform to the name=value format' % \
                    a)
            name = a[:isPos]
            value = a[isPos+1:]
            try:
                value = json.loads(value)
            except json.JSONDecodeError:
                #In case it isn't JSON, keep it as a string
                pass
            kwargs[name] = value

        try:
            return getattr(self.rpc, cmd)(**kwargs)
        except (ValueError, TypeError) as e:
            raise Backend.CommandFailed(str(e))


    def getNativeCurrency(self):
        '''
        Arguments:
        Returns: str
            BIP-173 currency code
        Exceptions:
            Backend.NotConnected: not connected to the backend
        '''
        if self.nodeInfo is None and not self.initNodeInfo():
            raise self.NotConnected()

        network = self.nodeInfo['network']
        return \
        {
        'bitcoin': 'bc',
        'regtest': 'bcrt',
        'testnet': 'tb',

        'litecoin': 'ltc',
        'litecoin-testnet': 'ltct',
        }[network]


    @translateRPCExceptions
    def getNodeLinks(self):
        '''
        Arguments:
        Returns: list(str)
        Exceptions:
            Backend.NotConnected: not connected to the backend
        '''
        if self.nodeInfo is None and not self.initNodeInfo():
            raise self.NotConnected()

        node_id = self.nodeInfo['id']

        ret = []
        if self.nodeInfo['address']:
            for a in self.nodeInfo['address']:
                ret.append(
                    '%s@%s:%s' % \
                    (node_id, a['address'], a['port'])
                    )

        if not ret:
            ret = [
                '%s@%s:%s' % \
                (node_id, '(unknown hostname)', self.nodeInfo['port'])
                ]

        return ret


    @translateRPCExceptions
    def getNonChannelFunds(self):
        '''
        Arguments:
        Returns: dict(tuple(str,int)->tuple(int, bool))
            The non-channel funds.
            Each key consists of:
                txid
                output index
            Each value consists of:
                value (in mSatoshi)
                is confirmed?
        Exceptions:
            Backend.NotConnected: not connected to the backend
        '''
        outputs = self.rpc.listfunds()['outputs']
        ret = {}
        for tx in outputs:
            ret[(tx['txid'], tx['output'])] = \
                (1000*tx['value'], True) #TODO: real confirmation
        return ret


    @translateRPCExceptions
    def getChannelFunds(self):
        '''
        Arguments:
        Returns: list(Channel)
            The channel funds.
        Exceptions:
            Backend.NotConnected: not connected to the backend
        '''
        channels = self.rpc.listfunds()['channels']
        ret = []
        for c in channels:
            ours =  1000*c['channel_sat']       #TODO: actual resolution
            total = 1000*c['channel_total_sat'] #TODO: actual resolution
            lockedIn = 0 #TODO
            lockedOut = 0 #TODO
            theirs = total - ours - lockedIn - lockedOut
            ret.append(Channel(
                channelID = Backend.ChannelID(
                    peerID = c['peer_id']
                    ),
                ownFunds = ours,
                lockedIncoming = lockedIn,
                lockedOutgoing = lockedOut,
                peerFunds = theirs
                ))
        return ret


    @translateRPCExceptions
    def getPeers(self):
        '''
        Arguments:
        Returns: list(Peer)
            The peer information.
        Exceptions:
            Backend.NotConnected: not connected to the backend
        '''

        peers = self.rpc.listpeers()['peers']

        ret = []
        for p in peers:
            channels = []
            if 'channels' in p:
                for c in p['channels']:
                    try:
                        state = \
                        {
                        'OPENINGD'                : 'opening',
                        'CHANNELD_AWAITING_LOCKIN': 'opened; waiting for confirmations',
                        'CHANNELD_NORMAL'         : 'normal',
                        'CHANNELD_SHUTTING_DOWN'  : 'mutual closing; waiting for transactions',
                        'CLOSINGD_SIGEXCHANGE'    : 'mutual closing; negotiating tx fee',
                        'CLOSINGD_COMPLETE'       : 'closed; waiting for confirmations',
                        'FUNDING_SPEND_SEEN'      : 'Spend of funding tx was seen',
                        'ONCHAIN'                 : 'tracking on-chain closing'
                        }[c['state']]
                    except KeyError:
                        state = c['state']
                    operational = c['state'] == 'CHANNELD_NORMAL'

                    ours = c['msatoshi_to_us']
                    total = c['msatoshi_total']
                    lockedIn = 0 #TODO
                    lockedOut = 0 #TODO
                    theirs = total - ours - lockedIn - lockedOut

                    channels.append(Channel(
                        channelID=Backend.ChannelID(peerID=p['id']),
                        state=state,
                        operational=operational,
                        ownFunds=ours,
                        lockedIncoming=lockedIn,
                        lockedOutgoing=lockedOut,
                        peerFunds=theirs
                        ))
            alias = p['alias'] if 'alias' in p else '(unknown)'
            color = p['color'] if 'color' in p else 'ffffff'
            ret.append(Peer(
                peerID=p['id'],
                alias=alias,
                color=color,
                connected=p['connected'],
                channels=channels
                ))
        return ret


    @translateRPCExceptions
    def getInvoices(self):
        '''
        Arguments:
        Returns: list(Invoice)
            The invoices.
        Exceptions:
            Backend.NotConnected: not connected to the backend
        '''
        invoices = self.rpc.listinvoices()['invoices']

        ret = []
        for inv in invoices:
            try:
                data = self.decodeInvoiceData(inv['bolt11'])
            except Backend.CommandFailed:
                data = InvoiceData(
                    expirationTime = inv['expires_at'],
                    amount = inv['msatoshi'],
                    currency = self.getNativeCurrency()
                    )

            ret.append(Invoice(
                label=inv['label'],
                status=inv['status'],
                bolt11=inv['bolt11'],
                data=data
                ))
        return ret


    @translateRPCExceptions
    def getPayments(self):
        '''
        Arguments:
        Returns: list(Payment)
            The payments.
        Exceptions:
            Backend.NotConnected: not connected to the backend
        '''
        payments = self.rpc.listpayments()['payments']
        currency = self.getNativeCurrency()
        return \
        [
        Payment(
            label=str(x['id']),
            timestamp=x['timestamp'],
            amount=x['msatoshi'],
            currency=currency,
            status=x['status'],
            destination=x['destination'],
            paymentHash=x['payment_hash'],
            paymentPreimage=x['payment_preimage']
            )
        for x in payments
        ]


    @translateRPCExceptions
    def makeNewInvoice(self, label, description, amount, expiry):
        '''
        Arguments:
            label: str
            description: str
            amount: int
                mSatoshi
            expiry: int
                Seconds from now
        Returns: str
            The bolt11 payment code
        Exceptions:
            Backend.CommandFailed: the command failed (e.g. label already exists)
            Backend.NotConnected: not connected to the backend
        '''
        try:
            data = self.rpc.invoice(
                msatoshi=amount,
                label=label,
                description=description,
                expiry=expiry
                )
        except ValueError as e:
            raise Backend.CommandFailed(str(e))

        return data['bolt11']


    @translateRPCExceptions
    def decodeInvoiceData(self, bolt11):
        '''
        Arguments:
            bolt11: str
        Returns: InvoiceData
        Exceptions:
            Backend.CommandFailed: the command failed (e.g. invalid bolt11 code)
            Backend.NotConnected: not connected to the backend
        '''
        try:
            result = self.rpc.decodepay(bolt11=bolt11)
        except ValueError as e:
            raise Backend.CommandFailed(str(e))

		#TODO: support for bolt11 data that doesn't contain all fields
        creationTime = result['created_at']
        expirationTime = creationTime + result['expiry']
        return InvoiceData(
            creationTime=creationTime,
            expirationTime=expirationTime,
            min_final_cltv_expiry=result['min_final_cltv_expiry'],
            amount=result['msatoshi'],
            currency=result['currency'],
            description=result['description'],
            payee=result['payee'],
            paymentHash=result['payment_hash'],
            signature=result['signature']
            )


    @translateRPCExceptions
    def pay(self, bolt11):
        '''
        Arguments:
            bolt11: str
        Returns: None
        Exceptions:
            Backend.CommandFailed: the command failed (e.g. invalid bolt11 code)
            Backend.NotConnected: not connected to the backend
        '''
        try:
            #TODO: support for the other arguments of pay
            self.rpc.pay(bolt11=bolt11)
        except ValueError as e:
            raise Backend.CommandFailed(str(e))


    @translateRPCExceptions
    def connect(self, link):
        '''
        Arguments:
            link: str
                id@host[:port]
        Returns: None
        Exceptions:
            Backend.CommandFailed: the command failed (e.g. invalid link, or connection failure)
            Backend.NotConnected: not connected to the backend
        '''
        try:
            self.rpc.connect(link)
        except ValueError as e:
            raise Backend.CommandFailed(str(e))


    @translateRPCExceptions
    def makeChannel(self, peerID, amount):
        '''
        Arguments:
            peerID: str
            amount: int
                mSatoshi
        Returns: None
        Exceptions:
            Backend.CommandFailed: the command failed
            Backend.NotConnected: not connected to the backend
        '''
        try:
            self.rpc.fundchannel(peerID, amount // 1000)
        except ValueError as e:
            raise Backend.CommandFailed(str(e))


    @translateRPCExceptions
    def closeChannel(self, channelID):
        '''
        Arguments:
            channelID: ChannelID
        Returns: None
        Exceptions:
            Backend.CommandFailed: the command failed
            Backend.NotConnected: not connected to the backend
        '''
        try:
            self.rpc.close(channelID.peerID)
        except ValueError as e:
            raise Backend.CommandFailed(str(e))



logging.info('Loaded Lightningd back-end module')

