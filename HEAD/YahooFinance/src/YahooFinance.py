#!/usr/bin/env python
#

import urllib2
import csv
import re
import time

__revision__ = "$Id: YahooFinance.py 7 2005-12-31 00:09:06Z nicolascouture $"

class FeedError(Exception):
    """
    Feed unavailable error.

    raised when obtaining data from a feed fails.
    """
    
    def __init__(self, msg=''):
        self.message = msg
        Exception.__init__(self, msg)

    def __repr__(self):
        return self.message

    __str__ = __repr__

class SymbolError(Exception):
    """
    Symbol invalid error.
    

    raised when a symbol is invalid.
    """
    def __init__(self, msg=''):
        self.message = msg
        Exception.__init__(self, msg)

    def __repr__(self):
        return self.message

    ___str__ = __repr__

def format_number(n):
    """
    Convert a number to a string by adding a coma every 3 characters.
    """
    if int(n) < 0:
        raise ValueError("positive integer expected")
    n = str(n)
    return ','.join([n[::-1][x:x+3]
              for x in range(0,len(n),3)])[::-1]

class YahooChartFinder:
    """
    Find charts of stocks, mutual funds, and market indices.
    """
    def __init__(self,
                 symbol,
                 range,
                 type,
                 size,
                 scale,
                 *symbols,
                 **attrs):
        """
        Find a chart location.

        symbol: stock symbol

        range: Chart time range 
            1d: 1 day chart
            5d: 5 days chart
            3m: 3 months chart
            6m: 6 months chart
            1y: 1 year chart
            2y: 2 years chart
            5y: 5 years chart
            max: longest chart avaiable
        
        type: Chart type
            bar:     bar chart
            line:    line chart
            candle:  candle chart

        scale: Chart type of y-axis
            log:    logarithmic y-axis
            linear: linear y-axis
    
        size: Chart size
            small:  Small sized chart
            medium: Medium sized chart
            large:  Large sized type

        symbols: List of simbols to compare with our symbol.

        attrs: Chart technical Indicators & Overlays

          Indicators:
            macd:   Moving Average Convergence/Divergence
            mfi:    Money Flow Index
            roc:    Rate Of Change
            rsi:    Relative Strength Index
            avol:   Number of shares
            mavol:  Number of shares transacted every day
            stoch_s:  Stochastic indicator (slow)
            stoch_f:  Stochastic indicator (fast)
            will:   William indicator

            The previous indicators are all documented at
            http://help.yahoo.com/help/us/fin/chart/chart-12.html.

          Overlays:
            boll:  Bollinger Band
            para:  Parabolic SAR
            split: Stock splits
            ovol:  Volume
            m5:    Moving average (5 days)
            m10:   Moving average (10 days)
            m20:   Moving average (20 days)
            m50:   Moving average (50 days)
            m100:  Moving average (100 days)
            m200:  Moving average (200 days)
            e5:    Exponential moving average (5 days)
            e10:   Exponential moving average (10 days)
            e20:   Exponential moving average (20 days)
            e50:   Exponential moving average (50 days)
            e100:  Exponential moving average (100 days)
            e200:  Exponential moving average (200 days)

        Example:

            >>> chart = YahooChartFinder('YHOO', '1d',
            ... 'candle', 'large', 'log')
            >>> chart
            http://ichart.finance.yahoo.com/z?s=YHOO&t=1d&q=c&l=on&z=l&a=&c=&p=
        """
        self.symbol  = symbol
        self.range   = range; del range
        self.type    = type; del type
        self.size    = size
        self.scale   = scale
        self.symbols = symbols
        self.attrs   = attrs

        self._times =  ('1d', '5d', '3m',
                        '6m', '1y', '2y',
                        '5y', 'max')
        self._types =  ('bar', 'line', 'candle')
        self._sizes =  ('small', 'medium', 'large')
        self._scales = ('log', 'linear')
        self._indicators = {
            'macd':    'm',
            'mfi':     'f',
            'roc':     'p',
            'rsi':     'r',
            'avol':    'v',
            'stoch_s': 'ss',
            'stoch_f': 'fs',
            'will':    'w'
        }
        self._overlays = {
            'boll':    'b',
            'para':    'p',
            'split':   's',
            'ovol':    'v',
            'm5':      'm5',
            'm10':     'm10',
            'm20':     'm20',
            'm50':     'm50',
            'm100':    'm100',
            'm200':    'm200',
            'e5':      'e5',
            'e10':     'e10',
            'e20':     'e20',
            'e50':     'e50',
            'e100':    'e100',
            'e200':    'e200',
        }

        self._validate_args()
        
    def _build_url(self):
        overlays = []
        indicators = []
        for key in self.attrs:
            if key in self._overlays:
                overlays.append(self._overlays[key])
            elif key in self._indicators:
                indicators.append(self._indicators[key])
            else:
                raise ValueError("Invalid attribute: %s" % key)

        if len(overlays) > 4:
            raise ValueError("Maximum amount of image overlays is four.")
        elif len(indicators) > 4:
            raise ValueError("Maximum amount of indicators is four.")

        service = "http://ichart.finance.yahoo.com/z?"
        parameters = ("s=%s"      # symbol
                      "&t=%s"     # range
                      "&q=%s"     # type
                      "&l=on"     #?
                      "&z=%s"     # size
                      "&a=%s"     # indicators
                      "&c=%s"     # symbol list to compare
                      "&p=%s" % ( # overlays
            self.symbol,
            self.range,
            self.type[0],
            self.size[0],
            ",".join(indicators),
            ",".join(self.symbols),
            ",".join(overlays)))

        return service + parameters # url

    def _validate_args(self):
        if self.range not in self._times:
            raise ValueError("Invalid range: %s" % self.range)
        if self.type not in self._types:
            raise ValueError("Invalid type: %s" % self.type)
        if self.size not in self._sizes:
            raise ValueError("Invalid size: %s" % self.size)
        if self.scale not in self._scales:
            raise ValueError("Invalid scale: %s" % self.scale)

        # attributes must be indicators or overlays
        for key in self.attrs:
            if (key not in self._indicators) and (
                key not in self._overlays):
               raise ValueError("Invalid attribute: %s" % key)
        
    def __repr__(self):
        return self._build_url()

    __str__ = __repr__
        
class YahooQuoteFinder:
    """
    Find stocks quotes from over 50 worldwide exanges.
    """

    def __init__(self, symbol, date=None, end_date=None):
        """
        Download stock quotation data and organize it in this object.

        symbol:           stock symbol/ticker
        
        date, end_date: (optional)
            These variables are used to obtain historical quotes;
            If only `date' is specified, we will obtain the historical
            quote for the date provided. If both `date' and `end_date'
            are specified, we will obtain all historical quotes for
            the time frame they create.
        
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
                day:      Day's Hi and Low
                year:     52-Week Hi and Low

            EPS:          Earning Per Share
            PE:           Price-Earnings Ratio

            dividend: (dict)
                l_date:   Dividend pay date
                p_share:  Dividend per share
                yeild:    Dividend yeild
        
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

        * Historical attributes

            date: (dict)
                ~value: (dict)
                 In format YYYYMMDD, this key will contain
                 a stock's historical quote attributes if the
                 date provided in `~value' was requested using
                 `date' and/or 'end_date' when initializing the object.
                 
                    open:      Historical open price
                    high:      Historical high price
                    low:       Historical low price
                    close:     Historical close price
                    volume:    Historical volume
                    adj_close: Historical close price adjusted
                                for dividends and splits

        Example:
            >>> YHOO = YahooQuoteFinder('YHOO')
            >>> YHOO.symbol
            'YHOO'
            >>> YHOO.realtime['last_trade']['date']
            'Dec 23'
            >>>
        """
        self.symbol = symbol
        
        # url: 43 attributes in a csv file
        self.url = "http://quote.yahoo.com/d?f=snl1d1t1c1p2va2bapomwerr1dyj"
        self.url += "1xs7t8e7e8e9r6r7r5b4p6p5j4m3m4b2b3k2k1c6m2j3&s=%s" % symbol

        # obtain stocks attributes
        try:
            f = urllib2.urlopen(self.url)
        except urllib2.URLError, e:
            raise FeedError("Could not obtain stock information")


        # read the csv file, create the list of our attributes
        # and remove unwanted sgml tags
        reader = csv.reader(f)
        for l in reader:  #? 
            self.data = l #?

        for (pos, item) in enumerate(self.data):
            self.data[pos] = re.sub('<[^>]*>', '', self.data[pos])

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
            'day': self.data[13],
            'year': self.data[14]
        }

        (self.EPS, self.PE) = (self.data[15], self.data[16])

        # div pay date, div per share, div yeild
        self.dividend = {
            'pay_date': self.data[17],
            'per_share': self.data[18],
            'yeild': self.data[19]
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
            'day_range': self.data[41],
            'capital': self.data[42]
        }

        # Historical quote container
        self.date = {}

        #==> We start processing historical quote requests
        # Historical quote requested dates containers
        start_date = None
        final_date = None        

        # Yahoo! Finance's historical quotation service location
        service = "http://ichart.finance.yahoo.com/table.csv?"

        # Final URL from which to obtain our historical quotes
        url = None

        # Validate and initialize data for historical quotes
        if date or end_date:
            # Verify the date and/or end_date validity
            if date and end_date:                    
                # Verify the validity of the time frame requested
                if int(date) > int(end_date):
                    raise ValueError("The start date provided must be"
                                     " smaller than the end date")
            elif date:
                if len(date) != 8:
                    raise ValueError("The date provided must be"
                                     " in format YYYMMDD.")
            elif end_date:
                if not date:
                    raise ValueError("You must provide a date with an end date")
                if len(end_date) != 8:
                    raise ValueError("The end date provided must be"
                                     " in format YYYMMDD.")


            # Create "3" tuples (month, day, year) to feed yahoo with
            
            # We need to substract 1 to the month because yahoo requires
            # the month provided to the table.csv service to be a value
            # from 0 to 11.
            if date:
                start_date = (int(date[4::2]) - 1, date[6:], date[:4])
            if end_date:
                final_date = (int(end_date[4::2]) - 1, end_date[6:],
                              end_date[:4])

        # For a time frame
        if start_date and final_date:
            parameters = ("a=%s&b=%s&c=%s"   # start date (m, d, y)
                          "&d=%s&e=%s&f=%s"  # first date (m, d, y)
                          "&s=%s" % (        # symbol
                          #"&y=0"             # ?
                          #"&g=d"             # ?
                          #"&ignore=.csv" % ( # ?
                          start_date[0], start_date[1], start_date[2],
                          final_date[0], final_date[1], final_date[2],
                          symbol))

            url = service + parameters

        # For a specific date
        elif start_date:
            parameters = ("a=%s&b=%s&c=%s"   # first date (m, d, y)
                          "&d=%s&e=%s&f=%s"  # final date (m, d, y)
                          "&s=%s" % (        # symbol
                          #"&y=0"             # ?
                          #"&g=d"             # ?
                          #"&ignore=.csv" % ( # ?
                          start_date[0], start_date[1], start_date[2],
                          start_date[0], start_date[1], start_date[2],
                          symbol))

            url = service + parameters

        if url:
            # Obtain and parse data
            historical_data = urllib2.urlopen(url)
            reader = csv.reader(historical_data)
            for (pos, l) in enumerate(reader):
                # If this is the first line, it is the csv description
                if pos == 0:
                    continue

                strtm = time.strptime(l[0], '%d-%b-%y')
                epoch = time.mktime(strtm)
                local = time.localtime(epoch)
                l_date = time.strftime('%Y%m%d', local)
                self.date[l_date] = {}
                self.date[l_date]['open']   = l[1:][0]
                self.date[l_date]['high']   = l[1:][1]
                self.date[l_date]['low']    = l[1:][2]
                self.date[l_date]['close']  = l[1:][3]
                self.date[l_date]['volume'] = l[1:][4]
                self.date[l_date]['adj_close'] = l[1:][5]


