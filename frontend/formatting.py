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


def formatAmount(amount):
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

