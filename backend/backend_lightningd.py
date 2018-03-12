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

from .lightningd.lightning import LightningRpc
from utils.struct import Struct



class Invoice(Struct):
    amount = None         #int, mSatoshi
    currency = None       #str, BIP-173
    label = None          #str
    expirationTime = None #int, UNIX timestamp
    status = None         #str


class InvoiceData(Struct):
    creationTime = None          #int, UNIX timestamp
    expirationTime = None        #int, UNIX timestamp
    min_final_cltv_expiry = None #int
    amount = None                #int, mSatoshi
    currency = None              #str, BIP-173
    description = None           #str
    payee = None                 #str
    paymentHash = None           #str
    signature = None             #str


class Payment(Struct):
    amount = None          #int, mSatoshi
    currency = None        #str, BIP-173
    label = None           #str
    timestamp = None       #int, UNIX timestamp
    status = None          #str
    destination = None     #str
    paymentHash = None     #str
    paymentPreimage = None #str


class Peer(Struct):
    peerID = None    #str
    alias = None     #str
    color = None     #str
    connected = None #bool
    channels = []    #list of (int,int,int,int)



def translateRPCExceptions(method):
    def newMethod(self, *args, **kwargs):
        try:
            return method(self, *args, **kwargs)
        except (ConnectionRefusedError, ConnectionResetError) as e:
            raise self.NotConnected(str(e))
    return newMethod

class Backend:
    class CommandFailed(Exception):
        pass

    class NotConnected(Exception):
        pass


    def __init__(self, config):
        logging.info('Using Lightningd back-end')
        lightningDir = config.getValue('lightningd', 'dir')
        lightningDir = os.path.expanduser(lightningDir)
        lightningDir = os.path.abspath(lightningDir)
        socketFile = os.path.join(lightningDir, 'lightning-rpc')
        self.rpc = LightningRpc(socketFile)
        self.initNodeInfo()


    def getBackendName(self):
        if self.nodeInfo is None and not self.initNodeInfo():
            raise self.NotConnected()
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
        Returns: dict(str->tuple(str,int,int,int,int))
            The channel funds.
            Each key consists of:
                funding txID
            Each value consists of:
                peer nodeID
                our funds (mSatoshi)
                locked funds, incoming (mSatoshi)
                locked funds, outgoing (mSatoshi)
                peer's funds (mSatoshi)
        Exceptions:
            Backend.NotConnected: not connected to the backend
        '''
        channels = self.rpc.listfunds()['channels']
        ret = {}
        for c in channels:
            peerID = c['peer_id']
            txID = c['funding_txid']
            ours =  1000*c['channel_sat']       #TODO: actual resolution
            total = 1000*c['channel_total_sat'] #TODO: actual resolution
            lockedIn = 0 #TODO
            lockedOut = 0 #TODO
            theirs = total - ours - lockedIn - lockedOut
            ret[txID] = (peerID, ours, lockedIn, lockedOut, theirs)
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
                    ours = c['msatoshi_to_us']
                    total = c['msatoshi_total']
                    lockedIn = 0 #TODO
                    lockedOut = 0 #TODO
                    theirs = total - ours - lockedIn - lockedOut
                    channels.append((ours, lockedIn, lockedOut, theirs))
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
        currency = self.getNativeCurrency()
        return \
        [
        Invoice(
            label=x['label'],
            expirationTime=x['expires_at'],
            amount=x['msatoshi'],
            currency=currency,
            status=x['status']
            )
        for x in invoices
        ]


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
        Returns: tuple(str, int)
            The bolt11 payment code
            The expiration time (UNIX timestamp)
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

        return (data['bolt11'], data['expires_at'])


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



logging.info('Loaded Lightningd back-end module')

