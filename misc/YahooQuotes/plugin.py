###
# Copyright (c) 2004, Jeremiah Fincher
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
###

"""
Add the module docstring here.  This will be used by the setup.py script.
"""

import supybot

__revision__ = "$Id$"
__author__ = "Nicolas Couture - supybot-plugin@stormvault.net"
__contributors__ = {}


import supybot.conf as conf
import supybot.utils as utils
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.privmsgs as privmsgs
import supybot.registry as registry
import supybot.callbacks as callbacks

from supybot.commands import *

import os
import time
import urllib2
import csv
import re

def configure(advanced):
    from supybot.questions import expect, anything, something, yn
    conf.registerPlugin('YahooQuotes', True)


conf.registerPlugin('YahooQuotes')
# This is where your configuration variables (if any) should go.

class FeedError(Exception):
    pass

class SymbolError(Exception):
    pass
        
class YahooQuoteFinder:
    """
    Find stocks quotes from over 50 worldwide exanges.
    """

    def __init__(self, symbol):
        """
        Download stock's attributes and attribute them to this object.
        
        * Basic attributes:

            symbol:       symbol
            company:      company name
            last_price:   price per share

            last_trade: (dict)
                date:     Last trade date
                time:     Last trade time
        
            change: (dict)
                cash:     Change in cash
                percent:  Change in percentage

            volume: (dict)
                daily:    Volume of shares traded
                average:  Average daily volume (3 months)

            value: (dict)
                bid:      Bid
                ask:      Ask
                p_close:  Previous close price per share
                l_close:  Last close price per share

            range: (dict)
                day (dict): Day's Hi and Low
                    hi: highest price
                    low: lowest price
                year (dict): 52-Week Hi and Low
                    hi: highest price
                    low: lowest price

            EPS:          Earning Per Share
            PE:           Price-Earnings Ratio

            dividend: (dict)
                pay_date:   Dividend pay date
                per_share:  Dividend per share
                yield:    Dividend yield
                previous: Previous dividend date
        
            capital:      Market cap (volume * price)
            exchange:     Exchange name

        * Extended attributes:

            short_ratio:  Short Interest Ratio
            target_52w:   Targetted price in 52 weeks

            EPS_est: (dict)
                current_year: Estimated EPS this year
                next_year:    Estimated EPS next year
                next_quarter: Estimated EPS next quarter

            price_EPS_est: (dict)
                current_year: Estimated Price/EPS this year
                next_year:    Estimated Price/EPS next year
                next_quarter: Estimated Price/EPS next quarter

            PEG:          Price/Earnings to Growth
            book_value:   Book value
            price_book:   Price/Book
            EBITDA:       EBITDA

            average_move: (dict)
                d50:      50 days moving average
                d200:     200 days moving average

        * Real-Time attributes:

            realtime: (dict)
                ask:      Ask (real-time)
                bid:      Bid (real-time)

                change: (dict)
                    percent: Change percentage (real-time)
                    cash:    Change in money (real-time)

                last_trade: (dict)
                    date:    Last trade date (real-time)
                    price:   Last trade price (real-time)
                day_range:   Day range (real-time)
                capital:     Market cap (volume * price) (real-time)

        * Fundamental attributes:

            outstanding: amount of outstanding shares
            float: amount of shares on the market

        Example:

            >>> YHOO = YahooQuoteFinder('YHOO')
            >>> YHOO.symbol
            'YHOO'
            >>> YHOO.realtime['last_trade']['date']
            'Dec 23'
            >>>
        """
        self.symbol = symbol
        
        # request of 44 stock & quotation attributes
        self.url = ("http://quote.yahoo.com/d?f=snl1d1t1c1p2va2bapomwerr1dyj"
                    "1xs7t8e7e8e9r6r7r5b4p6p5j4m3m4b2b3k2k1c6m2j3q&s=%s" %
                    symbol)

        try:
            f = urllib2.urlopen(self.url)
        except urllib2.URLError, e:
            raise FeedError("Could not fetch stocks attributes")


        # read the csv file, create the list of our attributes
        # and remove unwanted sgml tags
        reader = csv.reader(f)
        for l in reader: self.data = l
        for (pos, item) in enumerate(self.data):
            self.data[pos] = re.sub ('<[^>]*>', '', self.data[pos])

        # If the volume of shares is not available,
        # it is an invalid symbol
        if self.data[7] == 'N/A':
            raise SymbolError("Invalid symbol: %s" % symbol)

        
        """
        Basic Attributes
        """

        (self.symbol, self.company, self.last_price) = self.data[:3]

        # date, time
        self.last_trade = {
            'date': self.data[3],
            'time': self.data[4]
        }

        # money change, percent change
        self.change = {
            'cash': self.data[5],
            'percent': self.data[6]
        }

        # total volume, average daily volume
        self.volume = {
            'daily': self.data[7],
            'average': self.data[8]
        }

        # company value, share bid, share ask,
        #  previous close, last close
        self.value = {
            'bid': self.data[9],
            'ask': self.data[10],
            'p_close': self.data[11],
            'l_close': self.data[12]
        }

        # day range, 52weeks range
        self.range = {
            'day': {'hi': self.data[13].split(' - ')[1],
                    'low': self.data[13].split(' - ')[0],
            },
            'year': {'hi': self.data[14].split(' - ')[1],
                     'low': self.data[14].split(' - ')[0]
            }
        }
        
        (self.EPS, self.PE) = (self.data[15], self.data[16])

        # div pay date, div per share, div yield
        self.dividend = {
            'pay_date': self.data[17],
            'per_share': self.data[18],
            'yield': self.data[19],
            'previous': self.data[43]
        }

        (self.capital, self.exchange) = (self.data[20], self.data[21])

        
        """
        Extended Attributes
        """

        (self.short_ratio,
         self.target_52w) = self.data[22:24]
        
        # estimate EPS - current year, next year, next quarter
        self.EPS_est = {
            'current_year': self.data[24],
            'next_year': self.data[25],
            'next_quarter': self.data[26]
        }
        
        # estimate price and EPS
        self.price_EPS_est = {
            'current_year': self.data[27],
            'next_year': self.data[28],
            'next_quarter': self.data[29]
        }

        (self.PEG,
         self.book_value,
         self.price_book,
         self.price_sales,
         self.EBITDA) = self.data[29:34]

        self.average_move = {
            'd50': self.data[34],
            'd200': self.data[35]
        }


        """
        Real-Time Attributes
        """

        self.realtime = {
            'ask': self.data[36],
            'bid': self.data[37],
            'change': {'percent': self.data[38].split(" - ")[1],
                       'cash': self.data[40]
                       },
            'last_trade': {'date': self.data[39].split(" - ")[0],
                           'price': self.data[39].split(" - ")[1]
                           },
            'day_range': {'low': self.data[41].split(" - ")[0],
                          'high': self.data[41].split(" - ")[1]
                          },
            'capital': self.data[42]
        }

        """
        Fundamental Attributes
        """

        # Obtaining these separately because they require
        # special parsing and cannot be added to a list
        # (they each become multiple items if they go through
        #  cvsreader).

        outstand = 'http://quote.yahoo.com/d?f=j2&s=%s' % self.symbol
        f = urllib2.urlopen(outstand)
        self.outstanding = int("".join(f.read().split(",")))

        freefloat = 'http://quote.yahoo.com/d?f=f6&s=%s' % self.symbol
        f = urllib2.urlopen(freefloat)
        self.float = int("".join(f.read().split(",")))

class YahooQuotes(callbacks.Privmsg):
    threaded = True

    def quote(self, irc, msg, args, symbol):
        """<symbol>

        Find basic quotes from over 50 worldwide exanges.
        """
        q = self._get_quote(irc, symbol)
        if q:
            irc.reply("%s (%s) Last: $%s [Change: $%s (%s)] [Vol: "
                      "%s, 3 months avg.: %s] [Day range: %s ~ %s]" % (
                q.symbol, q.company, q.last_price, q.change["cash"],
                q.change["percent"], q.volume["daily"], q.volume["average"],
                q.range["day"]["low"], q.range["day"]["hi"]))

    quote = wrap(quote, ['somethingWithoutSpaces'])
    ###

    def real_time(self, irc, msg, args, symbol):
        """<symbol>

        Find real-time quotes for 'symbol' (used for after-hours statistics)
        """
        q = self._get_quote(irc, symbol)
        if q:
            rt = q.realtime
            irc.reply("%s (%s) Last trade: $%s, Date: %s "
                      "[Ask: $%s, Bid: $%s] [Change: $%s (%s)] "
                      "[Day range: %s] Market Capital: %s" % (
                q.symbol, q.company, rt["last_trade"]["price"],
                rt["last_trade"]["date"], rt["ask"], rt["bid"],
                rt["change"]["cash"], rt["change"]["percent"],
                rt["day_range"], rt["capital"]))
    realtime = wrap(real_time, ['somethingWithoutSpaces'])
    ###

    def fundamental(self, irc, msg, args, symbol):
        """<symbol>

        Find global security information
        """
        q = self._get_quote(irc, symbol)
        if q:
            # format output data
            q.outstanding = format_number(q.outstanding)
            q.float = format_number(q.float)

            irc.reply("%s (%s) Outstanding Shares: %s "
                      "Floating Shares: %s" % (
                q.symbol, q.company, q.outstanding, q.float))

    fundamental = wrap(fundamental, ['somethingWithoutSpaces'])
    ###

    def dividend(self, irc, msg, args, symbol):
        """<symbol>

        Obtain last dividend yielded by a security (<symbol>)
        """
        q = self._get_quote(irc, symbol)
        if q:
            div = q.dividend
            try:
                value = (float(div["per_share"]) * 100 /
                         float(div["yield"]))
            except TypeError:
                value = 'N/A'
            except ValueError:
                value = 'N/A'

            # if we have a float, convert to decimal
            if type(value) is float:
                (i, f) = str(value).split(".")
                value = float(".".join([i, f[:2]]))
                
            irc.reply("%s (%s) Last: $%s "
                      "Dividend: $%s Yield: %s Previous dividend: %s" % (
                q.symbol, q.company, q.last_price, div["per_share"],
                div["yield"] + '%', div["previous"]))

    dividend = wrap(dividend, ['somethingWithoutSpaces'])
    ###
        
    # Private functions
    def _get_quote(self, irc, symbol):
        # returns a quote object or send error to 'irc'
        try:
            quote = YahooQuoteFinder(symbol)
            return quote
        except FeedError:
            irc.reply("Could not obtain quote for '%s' from Yahoo! Finance." %
                      symbol)
        except SymbolError:
            irc.reply("Invalid symbol '%s'." % symbol)

    def _colorize(self, s, bold=True, color=None):
        if not (color or bold):
            raise ValueError("bold or color must be set")
        elif (color and bold):
            return ircutils.bold(
                ircutils.mircColor(s, color))
        elif bold:
            return ircutils.bold(s)
        elif color:
            return ircutils.mircColor(s, color)

    def _aspect(self, i):
        # red if negative
        # green if positive
        # yellow if zero
        if float(i.strip('%s')) < 0:
            return ircutils.mircColor(str(i), 'red')
        elif float(i.strip('%s')) > 0:
            return ircutils.mircColor(str(i), 'light green')
        else:
            return ircutils.mircColor(str(i), 'yellow')


def format_number(n):
    """
    Convert a number to a string by adding a coma every 3 characters
    """
    if int(n) < 0:
        raise ValueError("positive integer expected")
    n = str(n)
    return ','.join([n[::-1][x:x+3]
              for x in range(0,len(n),3)])[::-1]

Class = YahooQuotes

# vim:set shiftwidth=4 tabstop=8 expandtab textwidth=78:
