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
__author__ = supybot.authors.unknown
__contributors__ = {}

import supybot.conf as conf
import supybot.utils as utils
import supybot.ircdb as ircdb
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.privmsgs as privmsgs
import supybot.registry as registry
import supybot.callbacks as callbacks

from PortfolioManager import PortfolioManager, PortfolioError

def configure(advanced):
    # This will be called by setup.py to configure this module.  Advanced is
    # a bool that specifies whether the user identified himself as an advanced
    # user or not.  You should effect your configuration by manipulating the
    # registry as appropriate.
    from supybot.questions import expect, anything, something, yn
    conf.registerPlugin('Portfolio', True)


conf.registerPlugin('Portfolio')
# This is where your configuration variables (if any) should go.

class Portfolio(callbacks.Privmsg):
    threaded = True

    def add(self, irc, msg, args, amount, symbol):
        """<amount> <symbol>

        Add <amount> of shares of <symbol> to your portfolio.
        """
        user = self._check_auth(irc, msg)
        if user:
            p = PortfolioManager(user.name)
            try:
                (symbol, amount, price) = p.add(symbol, amount)
                irc.reply("Added %s shares of '%s' at %s" % (amount, symbol, price))
            except PortfolioError, e:
                irc.reply(e)
    add = wrap(add, ['positiveInt', 'something'])
    ###

    def remove(self, irc, msg, args, symbol, amount, price=None):
        """<symbol> [amount]

        Remove shares from your portfolio.
        If [amount] is unspecified, we erase all shares under <symbol>
        """
        user = self._check_auth(irc, msg)
        if user:
            p = PortfolioManager(user.name)
            try:
                removed = p.remove(symbol, amount, price)
            except PortfolioError, e:
                irc.reply(e)
                return False
            irc.reply("Removed %s shares of '%s'" % (removed, symbol))
    remove = wrap(remove, ['something', optional('int', 0)])

    def show(self, irc, msg, args):
        user = self._check_auth(irc, msg)
        if user:
            p = PortfolioManager(user.name)
            current_value = 0
            initial_value = 0
            for stock in p:
                for batch in p[stock]:
                    paid = batch.getInitialValue()
                    worth = batch.getCurrentValue()
                    gains = batch.getTotalGains()

                    current_value += worth
                    initial_value += paid

                    # TODO
                    
    show = wrap(show)

    def _check_auth(self, irc, msg):
        hostmask = irc.state.nickToHostmask(msg.nick)
        try:
            user = ircdb.users.getUser(hostmask)
            return user
        except KeyError:
            irc.reply("You must be authentified before"
                      " you can use a portfolio.")
            return None

Class = Portfolio

# vim:set shiftwidth=4 tabstop=8 expandtab textwidth=78:
