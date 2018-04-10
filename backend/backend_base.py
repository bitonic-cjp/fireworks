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


class Channel(Struct):
    channelID      = None #Backend.ChannelID
    state          = None #str
    operational    = None #bool
    ownFunds       = None #int, mSatoshi
    lockedIncoming = None #int, mSatoshi
    lockedOutgoing = None #int, mSatoshi
    peerFunds      = None #int, mSatoshi


class Peer(Struct):
    peerID = None    #str
    alias = None     #str
    color = None     #str
    connected = None #bool
    channels = []    #list of Channel



class Backend:
    class CommandFailed(Exception):
        pass

    class NotConnected(Exception):
        pass

