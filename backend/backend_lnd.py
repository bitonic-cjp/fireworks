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


    def tryToConnect(self):
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
            request = ln.UnlockWalletRequest(
                wallet_password='Invalid passphrase'.encode()
                )
            unlocker.UnlockWallet(request)
        except grpc.RpcError as e:
            state = e._state
            if state.code == grpc.StatusCode.UNKNOWN:
                pass #already unlocked
            elif state.code == grpc.StatusCode.UNIMPLEMENTED:
                needsUnlock = False
            elif state.code == grpc.StatusCode.UNAVAILABLE:
                return False #tryToConnect fails
            else:
                raise #unexpected

        if needsUnlock:
            password = self.frontend.getPassword('Wallet passphrase:')

            if password is not None:
                request = ln.UnlockWalletRequest(wallet_password=password)
                unlocker.UnlockWallet(request)

        #Re-open channel after unlock attempt:
        self.channel = grpc.secure_channel(
            '%s:%d' % (self.RPCHost, self.RPCPort),
            self.creds)

        self.rpc = lnrpc.LightningStub(self.channel)
        return True


    def getBackendName(self):
        raise Backend.NotConnected()


    def isConnected(self):
        return False


    @manageConnection
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

        try:
            method = getattr(self.rpc, cmd)
            requestType = getattr(ln, cmd + 'Request')
        except AttributeError:
            raise Backend.CommandFailed('Command does not exist')

        request = requestType(*args)

        try:
            if self.macaroon is None:
                response = method(request)
            else:
                response = method(request, metadata=[('macaroon', self.macaroon)])
        except grpc.RpcError as e:
            try:
                state = e._state
            except AttributeError:
                raise Backend.CommandFailed('Command failed: ' + str(e))

            if state.code == grpc.StatusCode.UNIMPLEMENTED:
                raise Backend.CommandFailed(
                    'Command failed: wallet seems to be locked')
            else:
                raise Backend.CommandFailed('Command failed: ' + str(e))


        return response


    @manageConnection
    def getNativeCurrency(self):
        '''
        Arguments:
        Returns: str
            BIP-173 currency code
        Exceptions:
            Backend.NotConnected: not connected to the backend
        '''
        raise Backend.NotConnected()


    @manageConnection
    def getNodeLinks(self):
        '''
        Arguments:
        Returns: list(str)
        Exceptions:
            Backend.NotConnected: not connected to the backend
        '''
        raise Backend.NotConnected()


    @manageConnection
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
        raise Backend.NotConnected()


    @manageConnection
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
        raise Backend.NotConnected()


    @manageConnection
    def getPeers(self):
        '''
        Arguments:
        Returns: list(Peer)
            The peer information.
        Exceptions:
            Backend.NotConnected: not connected to the backend
        '''
        raise Backend.NotConnected()


    @manageConnection
    def getInvoices(self):
        '''
        Arguments:
        Returns: list(Invoice)
            The invoices.
        Exceptions:
            Backend.NotConnected: not connected to the backend
        '''
        raise Backend.NotConnected()


    @manageConnection
    def getPayments(self):
        '''
        Arguments:
        Returns: list(Payment)
            The payments.
        Exceptions:
            Backend.NotConnected: not connected to the backend
        '''
        raise Backend.NotConnected()


    @manageConnection
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


    @manageConnection
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


    @manageConnection
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


    @manageConnection
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
        raise Backend.NotConnected()


    @manageConnection
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
        raise Backend.NotConnected()


    @manageConnection
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

