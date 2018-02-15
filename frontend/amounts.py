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

#Amounts, expressed in mSatoshi
mSatoshi = 1
Satoshi  = 1000 * mSatoshi
uBTC     = 100  * Satoshi
mBTC     = 1000 * uBTC
BTC      = 1000 * mBTC



def format(amount):
    '''
    Arguments:
        amount: int
            amount in mSatoshi
    Returns: str
        the formatted amount
    Exceptions:
        none
    '''
    #TODO: make the unit configurable
    #Maybe also pass the precision as argument?

    digits = '%012d' % amount
    BTC  = digits[:-11]
    Sat  = digits[-11:-3]
    mSat = digits[-3:]

    return '%s.%s %s BTC' % (BTC, Sat, mSat)

