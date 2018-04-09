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

import logging
import os
import codecs
import json
import time

import grpc

from .lnd import rpc_pb2 as ln
from .lnd import rpc_pb2_grpc as lnrpc

from .backend_base import Invoice, InvoiceData, Payment, Channel, Peer
from .backend_base import Backend as Backend_Base



#See https://github.com/lightningnetwork/lnd/blob/master/docs/grpc/python.md



def manageConnection(method):
    def newMethod(self, *args, **kwargs):
        if self.rpc is None and not self.tryToConnect():
            raise self.NotConnected('Back-end is not connected')
        return method(self, *args, **kwargs)

    return newMethod



class Backend(Backend_Base):
    def __init__(self, config):
        logging.info('Using LND back-end')
        self.config = config


    def setFrontend(self, frontend):
        self.frontend = frontend


    def startup(self):
        certFile = self.config.getValue('lnd', 'certfile')
        certFile = os.path.expanduser(certFile)
        certFile = os.path.abspath(certFile)
        with open(certFile, 'rb') as f:
            cert = f.read()
        self.creds = grpc.ssl_channel_credentials(cert)

        macaroonFile = self.config.getValue('lnd', 'macaroonfile')
        if macaroonFile.strip() == '':
            self.macaroon = None
        else:
            macaroonFile = os.path.expanduser(macaroonFile)
            macaroonFile = os.path.abspath(macaroonFile)
            with open(macaroonFile, 'rb') as f:
                macaroon_bytes = f.read()
                self.macaroon = codecs.encode(macaroon_bytes, 'hex')

        self.RPCHost = self.config.getValue('lnd', 'rpchost')
        self.RPCPort = int(self.config.getValue('lnd', 'rpcport'))

        self.channel = None
        self.rpc = None
        self.nativeCurrency = None
        self.connectInProgress = False


    def tryToConnect(self):
        #Enforce non-reentrant behavior.
        #With a connect-in-progress, assume connecting failed.
        if self.connectInProgress:
            return False

        try:
            self.connectInProgress = True

            self.channel = grpc.secure_channel(
                '%s:%d' % (self.RPCHost, self.RPCPort),
                self.creds)

            unlocker = lnrpc.WalletUnlockerStub(self.channel)

            #First try to unlock with an invalid passphrase.
            #This will fail with StatusCode.UNIMPLEMENTED if already unlocked
            #This will fail with StatusCode.UNAVAILABLE if the connection fails
            #This will fail with StatusCode.UNKNOWN otherwise
            needsUnlock = True
            try:
                logging.debug('> LND RPC UnlockWallet (invalid)')
                request = ln.UnlockWalletRequest(
                    wallet_password='Invalid passphrase'.encode()
                    )
                unlocker.UnlockWallet(request)
                logging.debug('< LND RPC UnlockWallet (invalid)')
            except grpc.RpcError as e:
                logging.debug('< LND RPC UnlockWallet (invalid): ' + str(e))
                state = e._state
                if state.code == grpc.StatusCode.UNKNOWN:
                    pass #locked, passphrase is incorrect (expected)
                elif state.code == grpc.StatusCode.UNIMPLEMENTED:
                    needsUnlock = False #already unlocked
                elif state.code == grpc.StatusCode.UNAVAILABLE:
                    return False #no connection
                else:
                    raise #unexpected

            if needsUnlock:
                #Repeat until the user enters a valid passphrase:
                while True:
                    password = self.frontend.getPassword('Wallet passphrase:')
                    if password is None: #cancel - try without a passphrase
                        break

                    try:
                        logging.debug('> LND RPC UnlockWallet')
                        request = ln.UnlockWalletRequest(wallet_password=password)
                        unlocker.UnlockWallet(request)
                        logging.debug('< LND RPC UnlockWallet')
                    except grpc.RpcError as e:
                        logging.debug('< LND RPC UnlockWallet: ' + str(e))
                        state = e._state
                        if state.code == grpc.StatusCode.UNKNOWN:
                            #passphrase is incorrect
                            self.frontend.showError(e.details())
                            continue
                        else:
                            raise #unexpected

                    #No exception - quit the loop
                    break

            #Re-open channel after unlock attempt:
            self.channel = grpc.secure_channel(
                '%s:%d' % (self.RPCHost, self.RPCPort),
                self.creds)

            self.rpc = lnrpc.LightningStub(self.channel)

            try:
                self.updateNativeCurrencyCache()
            except Backend.NotConnected:
                #For now, the RPC fails for us.
                #In practice, it turns out it will become available in a few
                #seconds.
                #This is OK: Fireworks will automatically retry to connect,
                #so this method will be called again until it succeeds.
                #For now, consider ourselves 'not connected':
                self.rpc = None
                self.channel = None
                return False

            return True
        finally:
            self.connectInProgress = False


    def getBackendName(self):
        '''
        Arguments:
        Returns: str
        Exceptions:
            Backend.NotConnected: not connected to the backend
        '''
        return 'LND'


    def isConnected(self):
        return self.rpc is not None or self.tryToConnect()


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

        return self.runCommandLowLevel(cmd, **kwargs)


    @manageConnection
    def runCommandLowLevel(self, cmd, **kwargs):
        try:
            method = getattr(self.rpc, cmd)
            try:
                #These are the exceptions. The general rule is in the
                #exception handler. :-S
                requestTypeName = \
                {
                'GetNodeInfo': 'NodeInfoRequest',
                }[cmd]
            except KeyError:
                requestTypeName = cmd + 'Request'
            requestType = getattr(ln, requestTypeName)
        except AttributeError:
            raise Backend.CommandFailed('Command does not exist')

        request = requestType(**kwargs)

        try:
            logging.debug('> LND RPC ' + cmd)
            if self.macaroon is None:
                response = method(request)
            else:
                response = method(request, metadata=[('macaroon', self.macaroon)])
            logging.debug('< LND RPC ' + cmd)
        except grpc.RpcError as e:
            logging.debug('< LND RPC %s: %s' % (cmd, str(e)))
            try:
                state = e._state
            except AttributeError:
                raise Backend.CommandFailed('Command failed: ' + str(e))

            if state.code == grpc.StatusCode.UNIMPLEMENTED:
                raise Backend.NotConnected(
                    'The wallet seems to be locked')
            elif state.code == grpc.StatusCode.UNAVAILABLE:
                raise Backend.NotConnected(
                    'The command is unavailable')
            else:
                raise Backend.CommandFailed('Command failed: ' + str(e))


        return response


    def updateNativeCurrencyCache(self):
        info = self.runCommandLowLevel('GetInfo')
        self.nativeCurrency = \
        {
        ('bitcoin', False): 'bc',
        ('bitcoin', True): 'tb',
        ('litecoin', False): 'ltc',
        ('litecoin', True): 'ltct',
        }[(info.chains[0], info.testnet)]


    @manageConnection
    def getNativeCurrency(self):
        '''
        Arguments:
        Returns: str
            BIP-173 currency code
        Exceptions:
            Backend.NotConnected: not connected to the backend
        '''
        return self.nativeCurrency


    def getNodeLinks(self):
        '''
        Arguments:
        Returns: list(str)
        Exceptions:
            Backend.NotConnected: not connected to the backend
        '''
        info = self.runCommandLowLevel('GetInfo')
        return list(info.uris)


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

        #For now, we can not determine individual on-chain transactions.
        #Construct some fake transactions based on the reported totals:
        balance = self.runCommandLowLevel('WalletBalance')
        confirmed = balance.confirmed_balance
        unconfirmed = balance.total_balance - balance.confirmed_balance
        return \
        {
        ('unconfirmed', 0): (1000*unconfirmed, False),
        ('confirmed', 0)  : (1000*confirmed  , True)
        }


    def getChannelFunds(self):
        '''
        Arguments:
        Returns: dict(str->Channel)
            The channel funds.
            Each key consists of:
                funding txID
        Exceptions:
            Backend.NotConnected: not connected to the backend
        '''

        ret = {}

        pendingChannels = self.runCommandLowLevel('PendingChannels')
        for (cList, state) in \
            [
            (pendingChannels.pending_open_channels, 'opening'),
            (pendingChannels.pending_closing_channels, 'closing'),
            (pendingChannels.pending_force_closing_channels, 'force-closing'),
            ]:
            for chn in cList:
                chn = chn.channel
                ret[chn.channel_point] = Channel(
                    state          = state,
                    operational    = True, #TODO
                    fundingTxID    = chn.channel_point,
                    ownFunds       = 1000 * chn.local_balance,
                    lockedIncoming = 0, #TODO
                    lockedOutgoing = 0, #TODO
                    peerFunds      = 1000 * chn.remote_balance,
                    )

        openChannels = self.runCommandLowLevel('ListChannels')
        openChannels = openChannels.channels
        for chn in openChannels:
            ret[chn.channel_point] = Channel(
                state          = 'active' if chn.active else 'inactive',
                operational    = chn.active,
                fundingTxID    = chn.channel_point,
                ownFunds       = 1000 * chn.local_balance,
                lockedIncoming = 0, #TODO
                lockedOutgoing = 0, #TODO
                peerFunds      = 1000 * chn.remote_balance,
                )

        return ret


    def getPeers(self):
        '''
        Arguments:
        Returns: list(Peer)
            The peer information.
        Exceptions:
            Backend.NotConnected: not connected to the backend
        '''
        peerDict = {}

        #Pending channels
        pendingChannels = self.runCommandLowLevel('PendingChannels')
        for (cList, state) in \
            [
            (pendingChannels.pending_open_channels, 'opening'),
            (pendingChannels.pending_closing_channels, 'closing'),
            (pendingChannels.pending_force_closing_channels, 'force-closing'),
            ]:
            for chn in cList:
                chn = chn.channel
                peerID = chn.remote_node_pub
                channel = Channel(
                    state          = state,
                    operational    = True, #TODO
                    fundingTxID    = chn.channel_point,
                    ownFunds       = 1000 * chn.local_balance,
                    lockedIncoming = 0, #TODO
                    lockedOutgoing = 0, #TODO
                    peerFunds      = 1000 * chn.remote_balance,
                    )
                if peerID in peerDict:
                    peerDict[peerID].channels.append(channel)
                else:
                    peerDict[peerID] = Peer(
                        peerID = peerID,
                        connected = False, #to be overwritten later if True
                        channels = [channel]
                        )


        #Open channels
        openChannels = self.runCommandLowLevel('ListChannels')
        openChannels = openChannels.channels
        for chn in openChannels:
            peerID = chn.remote_pubkey
            channel = Channel(
                state          = 'open',
                operational    = chn.active,
                fundingTxID    = chn.channel_point,
                ownFunds       = 1000 * chn.local_balance,
                lockedIncoming = 0, #TODO
                lockedOutgoing = 0, #TODO
                peerFunds      = 1000 * chn.remote_balance,
                )
            if peerID in peerDict:
                peerDict[peerID].channels.append(channel)
            else:
                peerDict[peerID] = Peer(
                    peerID = peerID,
                    connected = False, #to be overwritten later if True
                    channels = [channel]
                    )

        peers = self.runCommandLowLevel('ListPeers')
        for p in peers.peers:
            peerID = p.pub_key
            if peerID in peerDict:
                #Connected peers have channels
                peerDict[peerID].connected = True
            else:
                #Connected peers that don't have any channels
                peerDict[peerID] = Peer(
                    peerID = peerID,
                    connected = True,
                    channels = []
                    )

        ret = list(peerDict.values())
        for peer in ret:
            try:
                nodeInfo = self.runCommandLowLevel('GetNodeInfo', pub_key=peer.peerID)
                nodeInfo = nodeInfo.node
                peer.alias = nodeInfo.alias
                peer.color = nodeInfo.color[1:] #remove '#'
            except Backend.CommandFailed:
                peer.alias = 'unknown'
                peer.color = '888888'
        return ret


    def getInvoices(self):
        '''
        Arguments:
        Returns: list(Invoice)
            The invoices.
        Exceptions:
            Backend.NotConnected: not connected to the backend
        '''
        raise Backend.NotConnected()


    def getPayments(self):
        '''
        Arguments:
        Returns: list(Payment)
            The payments.
        Exceptions:
            Backend.NotConnected: not connected to the backend
        '''
        raise Backend.NotConnected()


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
        raise Backend.NotConnected()


    def decodeInvoiceData(self, bolt11):
        '''
        Arguments:
            bolt11: str
        Returns: InvoiceData
        Exceptions:
            Backend.CommandFailed: the command failed (e.g. invalid bolt11 code)
            Backend.NotConnected: not connected to the backend
        '''
        raise Backend.NotConnected()


    def pay(self, bolt11):
        '''
        Arguments:
            bolt11: str
        Returns: None
        Exceptions:
            Backend.CommandFailed: the command failed (e.g. invalid bolt11 code)
            Backend.NotConnected: not connected to the backend
        '''
        raise Backend.NotConnected()


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
        peerID, host = link.split('@')
        address = ln.LightningAddress(
	        pubkey = peerID,
	        host = host
            )
        self.runCommandLowLevel('ConnectPeer', addr=address, perm=True)


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
        self.runCommandLowLevel('OpenChannel',
            node_pubkey = peerID.encode(),
            local_funding_amount = amount // 1000
            )


    def closeChannel(self, fundingTxID):
        '''
        Arguments:
            fundingTxID: str
        Returns: None
        Exceptions:
            Backend.CommandFailed: the command failed
            Backend.NotConnected: not connected to the backend
        '''
        raise Backend.NotConnected()


#On loading the module, set the TLS ciphers that are used by LND:
# Default is ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384
# https://github.com/grpc/grpc/blob/master/doc/environment_variables.md
#
# Current LND cipher suites here:
# https://github.com/lightningnetwork/lnd/blob/master/lnd.go#L80
#
# We order the suites by priority, based on the recommendations provided by SSL Labs here:
# https://github.com/ssllabs/research/wiki/SSL-and-TLS-Deployment-Best-Practices#23-use-secure-cipher-suites
os.environ['GRPC_SSL_CIPHER_SUITES'] = ':'.join(
    [
      'ECDHE-ECDSA-AES128-GCM-SHA256',
      'ECDHE-ECDSA-AES256-GCM-SHA384',
      'ECDHE-ECDSA-AES128-CBC-SHA256',
      'ECDHE-ECDSA-CHACHA20-POLY1305'
    ])

logging.info('Loaded LND back-end module')

