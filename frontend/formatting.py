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

import datetime
import decimal

from utils.currencies import currencyInfo



def formatTimestamp(timestamp):
    #TODO: make the formatting and time zone configurable
    #TODO: maybe somehow store historic timezone information?
    #  e.g. one transaction might be made in Hong Kong, another in New York.

    #Naive datetime objects without timezone info:
    dt_local = datetime.datetime.fromtimestamp(timestamp, tz=None)
    dt_utc   = datetime.datetime.utcfromtimestamp(timestamp)

    #Determine UTC offset that was apparently used:
    #Note: this might be different from the current local UTC offset,
    #  because of DST changes and other time zone changes.
    utc_offset = dt_local - dt_utc
    timezone = datetime.timezone(utc_offset)

    #Aware datetime object with timezone info:
    dt = datetime.datetime.fromtimestamp(timestamp, timezone)

    return dt.strftime('%c (%Z)')


def formatAmount(amount, currency, unit=None):
    '''
    Arguments:
        amount: int
            amount in mSatoshi
        currency: str
            BIP-173 currency code
        unit: None or str
            str:  Use the given unit
            None: Use the default unit for the currency
    Returns: str
        the formatted amount
    Exceptions:
        none
    '''

    info = currencyInfo[currency]
    if unit is None:
        unit = info.defaultUnit

    return '%s %s' % (formatAmountWithoutUnit(amount, currency, unit), unit)


def formatAmountWithoutUnit(amount, currency, unit=None):
    '''
    Arguments:
        amount: int
            amount in mSatoshi
        currency: str
            BIP-173 currency code
        unit: None or str
            str:  Use the given unit
            None: Use the default unit for the currency
    Returns: str
        the formatted amount
    Exceptions:
        none
    '''
    #Maybe also pass the precision as argument?

    info = currencyInfo[currency]
    if unit is None:
        unit = info.defaultUnit
    multiplier = info.multipliers[unit]

    sign = '-' if amount < 0 else ''
    amount = abs(amount)

    ret = ''

    if multiplier == 1:
        #No decimal separator
        return '%s%d' % (sign, amount)
    elif multiplier > 1000:
        #Sub-satoshi part after a space, if we we use a more-than-satoshi unit
        ret = ' %03d' % (amount % 1000)
        amount //= 1000
        multiplier //= 1000

    while multiplier >= 10:
        ret = str(amount % 10) + ret
        amount //= 10
        multiplier //= 10

    assert(multiplier == 1)

    return '%s%d.%s' % (sign, amount, ret)


def unformatAmount(text, currency):
    '''
    Arguments:
        text: str
            the formatted amount. Should be:
            [x][.y]U
            where x and y consist of decimal characters, and U is a recognized
            unit. Whitespace is ignored.
        currency: str
            BIP-173 currency code
    Returns: int
        amount in mSatoshi
    Exceptions:
        Exception: syntax error
    '''

    info = currencyInfo[currency]

    #Remove whitespace:
    for c in ' \t\r\n':
        text = text.replace(c, '')

    #Find and extract unit
    lastDecimalPos = -1
    while text[lastDecimalPos].isalpha():
        lastDecimalPos -= 1
    unit = text[lastDecimalPos+1:]
    text = text[:lastDecimalPos+1]

    multiplier = info.multipliers[unit]
    amount = multiplier * decimal.Decimal(text)
    return int(amount)


def unformatAmountWithoutUnit(text, currency, unit):
    '''
    Arguments:
        text: str
            the formatted amount. Should be:
            [x][.y]
            where x and y consist of decimal characters
            Whitespace is ignored.
        currency: str
            BIP-173 currency code
        unit: str
            A recognized unit.
    Returns: int
        amount in mSatoshi
    Exceptions:
        Exception: syntax error
    '''
    return unformatAmount(text+unit, currency)

