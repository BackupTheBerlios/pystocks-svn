#!/usr/bin/python
#

import os
import cPickle

from pystocks.YahooFinance import (YahooQuoteFinder,
                                   SymbolError,
                                   FeedError,
                                   format_number)

class PortfolioManager:
    def __init__(self, name, feed):
        """
        Initialize a portfolio object.
        
        name: portfolio name
        feed: pystocks feed callable
        """
        pass

    def create(self):
        """
        Create portfolio.
        """
        # if portfolio exists:
        #     raise error.
        # otherwise:
        #     create it.
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

    def _exist_or_die(self):
        # if portfolio doesn't exist:
        #     raise error
        pass
