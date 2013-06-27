# -*- coding: utf-8 -*-
import cmd
import sys

import gevent
import gevent.server
from gevent import sleep
from telnetsrv.green import TelnetHandler, command


class WOPRHandler(TelnetHandler):
    PROMPT = "LOGON:  "
    WELCOME = ""

    def _swrite(self, c, character=0.01, line=0.01):
        self.write(c)
        sleep(line if c == "\n" else character)

    def swrite(self, phrase, character=0.01, line=0.01, endln=True):
        for c in phrase:
            self._swrite(c, character=character, line=line)
        if endln:
            self._swrite("\n", line=0)

    @command('help')
    def help(self, params):
        self.writeline("Yo: %s" % (params,))

    @command('joshua')
    def joshua(self, params):
        self.swrite("GREETINGS PROFESSOR FALKEN.")

if __name__ == "__main__":
    handler = WOPRHandler.streamserver_handle
    server = gevent.server.StreamServer(("", 8023), handler)
    server.serve_forever()
    #swrite("GREETINGS PROFESSOR FALKEN.")
    #swrite("HOW ARE YOU FEELING TODAY?")
