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



class Invoice:
    '''
    amount: int
        mSatoshi
    label: str
    expirationTime: int
        UNIX timestamp
    status: str
    '''

    def __init__(self, amount, label, expirationTime, status):
        self.amount = amount
        self.label = label
        self.expirationTime = expirationTime
        self.status = status


    def __eq__(self, invoice):
        return \
            self.amount == invoice.amount and \
            self.label == invoice.label and \
            self.expirationTime == invoice.expirationTime and \
            self.status == invoice.status



class Payment:
    '''
    amount: int
        mSatoshi
    label: str
    timestamp: int
        UNIX timestamp
    status: str
    destination: str
    paymentHash: str
    paymentPreimage: str
    '''

    def __init__(self, amount, label, timestamp, status, destination, paymentHash, paymentPreimage):
        self.amount = amount
        self.label = label
        self.timestamp = timestamp
        self.status = status
        self.destination = destination
        self.paymentHash = paymentHash
        self.paymentPreimage = paymentPreimage


    def __eq__(self, payment):
        return \
            self.amount == payment.amount and \
            self.label == payment.label and \
            self.timestamp == payment.timestamp and \
            self.status == payment.status and \
            self.destination == payment.destination and \
            self.paymentHash == payment.paymentHash and \
            self.paymentPreimage == payment.paymentPreimage



class Backend:
    class CommandFailed(Exception):
        pass

    def __init__(self, config):
        logging.info('Using Lightningd back-end')
        lightningDir = config.getValue('lightningd', 'lightning-dir')
        lightningDir = os.path.expanduser(lightningDir)
        lightningDir = os.path.abspath(lightningDir)
        socketFile = os.path.join(lightningDir, 'lightning-rpc')
        self.rpc = LightningRpc(socketFile)


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
            TBD (e.g. not connected?)
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
            TBD (e.g. not connected?)
        '''
        outputs = self.rpc.listfunds()['outputs']
        ret = {}
        for tx in outputs:
            ret[(tx['txid'], tx['output'])] = \
                (1000*tx['value'], True) #TODO: real confirmation
        return ret


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
            TBD (e.g. not connected?)
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


    def getInvoices(self):
        '''
        Arguments:
        Returns: list(Invoice)
            The invoices.
        Exceptions:
            TBD (e.g. not connected?)
        '''
        invoices = self.rpc.listinvoices()['invoices']
        return \
        [
        Invoice(
            label=x['label'],
            expirationTime=x['expires_at'],
            amount=x['msatoshi'],
            status=x['status']
            )
        for x in invoices
        ]


    def getPayments(self):
        '''
        Arguments:
        Returns: list(Payment)
            The payments.
        Exceptions:
            TBD (e.g. not connected?)
        '''
        payments = self.rpc.listpayments()['payments']
        return \
        [
        Payment(
            label=str(x['id']),
            timestamp=x['timestamp'],
            amount=x['msatoshi'],
            status=x['status'],
            destination=x['destination'],
            paymentHash=x['payment_hash'],
            paymentPreimage=x['payment_preimage']
            )
        for x in payments
        ]


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
            TBD (e.g. not connected?)
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

logging.info('Loaded Lightningd back-end module')

