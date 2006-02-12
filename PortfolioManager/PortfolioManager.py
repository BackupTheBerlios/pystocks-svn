#!/usr/bin/python
#

import os
import time

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
    symbol = StringCol   (length=12, notNone=True)
    amount = IntCol      (notNone=True) # amount of share
    date   = StringCol   (notNone=True) # time.time() # date added
    price  = FloatCol    (notNone=True) # paid price

class PortfolioManager:
    """
    """
    def __init__(self, name, feed=YahooQuoteFinder):
        """
        Initialize a portfolio object.
        
        name: portfolio name
        feed: pystocks callable interface
              (default: YahooQuoteFinder)
        """
        self.name = name
        self.feed = feed
        self.db_installdir = os.path.expanduser("~/.pystocks")
        self.db_filename = os.path.join(self.db_installdir,
                                        name + '.db')

        if not os.path.exists(self.db_installdir):
            os.mkdir(self.db_installdir)

        if self.exists():
            conn_string = "sqlite://%s" % self.db_filename
            conn = connectionForURI(conn_string)
            sqlhub.processConnection = conn

    def create(self):
        """
        Create portfolio.
        """
        if os.path.isfile(self.db_filename):
            raise ValueError("Portfolio %s exists in %s" %
                             (self.name, self.db_filename))
        else:
            conn_string = "sqlite://%s" % self.db_filename
            conn = connectionForURI(conn_string)
            sqlhub.processConnection = conn
            StockOwned.createTable()

    def add(self, symbol, amount, price=None):
        """
        Add stocks to portfolio.

        symbol: stock's symbol
        amount: amount of shares
        price:  paid price
                (default: current price)
        """
        self._exist_or_die()
        price = price or YahooQuoteFinder(symbol).last_price
        time_str = time.asctime(time.localtime(time.time()))
        StockOwned(symbol=symbol, amount=amount,
                   date=time_str, price=float(price))

    def show(self):
        print StockOwned.get(1)

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
        if os.path.isfile(self.db_filename):
            return True

    def _exist_or_die(self):
        if not self.exists():
            raise ValueError("Portfolio '%s' does not exist." %
                             self.name)


