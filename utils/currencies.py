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



class CurrencyInfo(Struct):
    defaultUnit = None #str
    multipliers = {}   #dict of str->int: multiplier in mSatoshi


currencyInfo = \
{
'bc': CurrencyInfo( #Bitcoin
    defaultUnit='BTC',
    multipliers={
    'mSatoshi':            1,
    'Satoshi' :         1000,
    'uBTC'    :       100000,
    'mBTC'    :    100000000,
    'BTC'     : 100000000000,
    }),
'tb': CurrencyInfo( #Bitcoin-testnet
    defaultUnit='tBTC',
    multipliers={
    'mSatoshi':            1,
    'Satoshi' :         1000,
    'utBTC'   :       100000,
    'mtBTC'   :    100000000,
    'tBTC'    : 100000000000,
    }),
'bcrt': CurrencyInfo( #Bitcoin-regtest
    defaultUnit='rBTC',
    multipliers={
    'mSatoshi':            1,
    'Satoshi' :         1000,
    'urBTC'   :       100000,
    'mrBTC'   :    100000000,
    'rBTC'    : 100000000000,
    }),


'ltc': CurrencyInfo( #Litecoin
    defaultUnit='LTC',
    multipliers={
    'mlitoshi':            1,
    'litoshi' :         1000,
    'uLTC'    :       100000,
    'mLTC'    :    100000000,
    'LTC'     : 100000000000,
    }),
'ltct': CurrencyInfo( #Litecoin-testnet
    defaultUnit='tLTC',
    multipliers={
    'mlitoshi':            1,
    'litoshi' :         1000,
    'utLTC'   :       100000,
    'mtLTC'   :    100000000,
    'tLTC'    : 100000000000,
    }),
}

