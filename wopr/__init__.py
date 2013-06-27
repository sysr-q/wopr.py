# -*- coding: utf-8 -*-
import cmd
import sys
import socket

import gevent
import gevent.server
from gevent import sleep
from telnetsrv.green import TelnetHandler, command

import junk


class Phases(object):
    LOGON = 0
    GAMES = 1
    JOSHUA = 2
    GLOBAL = 3


class WOPRHandler(TelnetHandler):
    PROMPT = "LOGON:  "
    WELCOME = ""
    session_start = lambda s: s.swrite(junk.CONNECTION, endln=False)

    _phase = Phases.LOGON

    def _swrite(self, c, character=0.01, line=0.01):
        self.write(c)
        sleep(line if c == "\n" else character)

    def swrite(self, phrase, character=0.01, line=0.01, endln=True):
        for c in phrase:
            self._swrite(c, character=character, line=line)
        if endln:
            self._swrite("\n", line=0)

    @command(["exit", "quit", "bye"])
    def _dont_leave(self, params):
        pass

    @command("logout")
    def dont_leave_me(self, params):
        self.swrite("--CONNECTION TERMINATED--")
        self.RUNSHELL = False

    # ---- PHASE 0 ----
    @command(["000001", "falkens-maze", "Falkens-Maze", "armageddon"])
    def terminate(self, params=None):
        if self._phase != Phases.LOGON and self._phase != Phases.GAMES:
            print self._phase, params, self.history[-1]
            return

        self.swrite(junk.CONNECTION_TERMINATED)
        self.RUNSHELL = False

    @command("help")
    def help(self, params):
        if self._phase != Phases.LOGON:
            return

        if len(params) == 0:
            return self.terminate()
        if params[0].lower() != "games":
            return self.swrite(junk.HELP_LOGON)
        self._phase = Phases.GAMES
        return self.swrite(junk.HELP_GAMES)

    # ---- PHASE 1 ----
    @command("list")
    def list(self, params):
        if self._phase != Phases.GAMES:
            return
        if len(params) == 0:
            return self.terminate()
        if params[0].lower() == "games":
            return self.swrite(junk.LIST_GAMES)

    # ---- PHASE 2 ----
    @command("joshua")
    def joshua(self, params):
        if self._phase not in (Phases.LOGON, Phases.GAMES):
            return

        self._phase = Phases.JOSHUA
        self.PROMPT = ""
        self.swrite(junk.JOSHUA_LOGON_GARBAGE, character=0.002)
        self.swrite(junk.JOSHUA_HELLO)

    @command(["hello.", "im", "people", "love", "later."])
    def phase2(self, params):
        """ This sort of covers most of phase 2.
            Not particularly clean, but hey, it works.
        """
        if self._phase != Phases.JOSHUA:
            return

        if self.history[-1].split()[0].lower() == "hello.":
            self.swrite(junk.JOSHUA_HOW_ARE_YOU)
        elif self.history[-1].split()[0].lower() == "im":
            self.swrite(junk.JOSHUA_EXCELLENT)
        elif self.history[-1].split()[0].lower() == "people":
            self.swrite(junk.JOSHUA_YES_THEY_DO)
        elif self.history[-1].split()[0].lower() == "love":
            self.swrite(junk.JOSHUA_WOULDNT_YOU)
        elif self.history[-1].split()[0].lower() == "later.":
            self._phase = Phases.GLOBAL
            self.swrite(junk.JOSHUA_FINE)

    # ---- PHASE 3 ----
    def phase3(self, params):
        pass

if __name__ == "__main__":
    handler = WOPRHandler.streamserver_handle
    server = gevent.server.StreamServer(("", 8023), handler)
    server.serve_forever()
