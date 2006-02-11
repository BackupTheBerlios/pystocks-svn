#!/usr/bin/python
#

import os
import cPickle

from sqlobject import *
from pystocks.YahooFinance import (YahooQuoteFinder,
                                   SymbolError,
                                   FeedError,
                                   format_number)

class StockOwned(SQLObject):
    """
    Represents a stock owned.

    symbol: stock's symbol
    amount: amount of shares owned
    
    """
    symbol = StringCol(length=12, notNone=True)
    amount = IntCol()   # amount of share
    date   = FloatCol() # time.time() # date added
    price  = FloatCol() # paid price

class PortfolioManager:
    def __init__(self, name, feed=YahooQuoteFinder):
        """
        Initialize a portfolio object.
        
        name: portfolio name
        feed: pystocks callable interface
              (default: YahooQuoteFinder)
        """
        self.name = name
        self.feed = feed
        self.db_installdir = "~/.pystocks"
        self.db_filename = os.path.expanduser("%s/%s.portfolio" %
                                              self.db_installdir, name)
        if not os.path.exist(self.db_installdir):
            os.path.mkdir(self.db_installdir)

        if self.exists()
            conn_string = "sqlite://%s" % self.db_filename
            conn = connectionForURI(connection_string)
            sqlhub.processConnection = conn

    def create(self):
        """
        Create portfolio.
        """
        if os.path.isfile(self.db_filename):
            raise ValueError("Portfolio %s exists in %s" %
                             self.name, self.db_filename)
        else:
            # create portfolio
            pass
        
    def add(self, symbol, amount, paid_price):
        """
        Add stocks to portfolio.

        symbol: stock's symbol
        amount: amount of shares
        price:  paid price
        """
        self._exist_or_die()
        pass

    def remove(self, symbol):
        """
        Remove stocks from portfolio.

        symbol: stock's symbol
        """
        self._exist_or_die()
        pass

    def exists(self):
        """
        Bool: portfolio exists or not.
        """
        os.path.isfile(self.db_filename)

    def _exist_or_die(self):
        if not self.exists():
            raise ValueError("Portfolio %s exists in %s" %
                             self.name, self.db_filename)


