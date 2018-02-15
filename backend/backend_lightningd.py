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



class Backend:
    class Error(Exception):
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
                command arguments (JSON-encoded)
        Returns: Any structure of list, dict, str, int, float
            The output of the command
        Exceptions:
            Backend.Error: the command failed
            TBD (e.g. not connected?)
        '''

        args = list(args)
        for i in range(len(args)):
            try:
                args[i] = json.loads(args[i])
            except json.JSONDecodeError:
                #In case it isn't JSON, keep it as a string
                pass

        try:
            return self.rpc._call(cmd, args)
        except ValueError as e:
            raise Backend.Error(str(e))


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
        Returns: list(tuple(str, int, int, str))
            The invoices.
            Each element consists of:
                label
                expiration date (UNIX timestamp)
                amount (mSatoshi)
                status
        Exceptions:
            TBD (e.g. not connected?)
        '''
        invoices = self.rpc.listinvoices()['invoices']
        return \
        [
        (x['label'], x['expires_at'], x['msatoshi'], x['status'])
        for x in invoices
        ]


logging.info('Loaded Lightningd back-end module')
