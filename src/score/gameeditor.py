#
# $Source$
# $Date$
# $Revision$
#
# DESCRIPTION:
# A container class for the current state of an edited game
# 
# This file is part of Chadwick, a library for baseball play-by-play and stats
# Copyright (C) 2005, Ted Turocy (turocy@econ.tamu.edu)
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
#

import time    # used for setting inputtime in info field
from libchadwick import *
from boxscore import Boxscore

def CreateGame(gameId, vis, home):
    """
    Creates a new Chadwick game object, filling in
    informational fields as appropriate.  Assumes that
    'gameId' is in Retrosheet standard format, and 'vis' and
    'home' are the team IDs
    """
    game = cw_game_create(gameId)
    
    cw_game_set_version(game, "1")
    cw_game_info_append(game, "inputprogvers", "Chadwick version 0.3.1")
    cw_game_info_append(game, "visteam", vis)
    cw_game_info_append(game, "hometeam", home)
    cw_game_info_append(game, "date",
                        "%s/%s/%s" % (gameId[3:7],
                                      gameId[7:9],
                                      gameId[9:11]))
    cw_game_info_append(game, "number", gameId[-1])

    # Fill in dummy values for other info fields
    # These generally correspond to standards for 'data unknown'
    cw_game_info_append(game, "starttime", "0:00")
    cw_game_info_append(game, "daynight", "unknown")
    cw_game_info_append(game, "usedh", "false")
    cw_game_info_append(game, "umphome", "")
    cw_game_info_append(game, "ump1b", "")
    cw_game_info_append(game, "ump2b", "")
    cw_game_info_append(game, "ump3b", "")
    cw_game_info_append(game, "scorer", "")
    cw_game_info_append(game, "translator", "")
    cw_game_info_append(game, "inputter", "")
    cw_game_info_append(game, "inputtime",
                        time.strftime("%Y/%m/%d %I:%M%p"))
    cw_game_info_append(game, "howscored", "unknown")
    cw_game_info_append(game, "pitches", "none")
    cw_game_info_append(game, "temp", "0")
    cw_game_info_append(game, "winddir", "unknown")
    cw_game_info_append(game, "windspeed", "-1")
    cw_game_info_append(game, "fieldcond", "unknown")
    cw_game_info_append(game, "precip", "unknown")
    cw_game_info_append(game, "sky", "unknown")
    cw_game_info_append(game, "timeofgame", "0")
    cw_game_info_append(game, "attendance", "0")
    cw_game_info_append(game, "wp", "")
    cw_game_info_append(game, "lp", "")
    cw_game_info_append(game, "save", "")

    return game

class GameEditor:
    def __init__(self, game, visRoster, homeRoster):
        self.game = game
        self.visRoster = visRoster
        self.homeRoster = homeRoster

        self.gameiter = CWGameIterator(self.game)
        if self.game.first_event != None:  self.gameiter.ToEnd()

        self.boxscore = Boxscore(self.game)

    def GetGame(self):     return self.game
    
    def GetBoxscore(self):   return self.boxscore
    def BuildBoxscore(self):  self.boxscore.Build()
    
    def AddPlay(self, text):
        cw_game_event_append(self.game,
                             self.GetInning(),
                             self.GetHalfInning(),
                             self.GetCurrentBatter(),
                             "??", "", text)
        self.gameiter.ToEnd()
        self.boxscore.Build()

    def DeletePlay(self):
        """
        Delete the last play from the game.  This call
        deletes the last actual play (exclusing 'NP'
        placeholder records), to ensure the resulting
        defensive configuration is OK.
        """
        x = self.game.last_event
        while x != None and x.event_text == "NP":
            x = x.prev

        # Now we should be at the last true event.
        # If there isn't one, just complete silently;
        # otherwise, truncate and update everything
        if x != None:
            cw_game_truncate(self.game, x)
            self.gameiter.ToEnd()
            self.boxscore.Build()

    def AddSubstitute(self, player, team, slot, pos):
        cw_game_event_append(self.game,
                             self.GetInning(),
                             self.GetHalfInning(),
                             self.GetCurrentBatter(),
                             "??", "", "NP")
        cw_game_substitute_append(self.game,
                                  player.player_id,
                                  player.first_name + " " + player.last_name,
                                  team, slot, pos)
        self.gameiter.ToEnd()
        self.boxscore.Build()

    def AddComment(self, text):
        cw_game_comment_append(self.game, text)

    def GetRoster(self, team):
        if team == 0:  return self.visRoster
        else:          return self.homeRoster
                            
    def SetStarter(self, player, name, team, slot, pos):
        cw_game_starter_append(self.game, player, name, team, slot, pos)
        cw_gameiter_reset(self.gameiter)

    def GetState(self):   return self.gameiter
    
    def GetCurrentBatter(self):
        halfInning = self.GetHalfInning()

        return self.gameiter.GetPlayer(halfInning,
                                       self.gameiter.NumBatters(halfInning) % 9 + 1)

    def GetCurrentRunner(self, base):
        return self.gameiter.GetRunner(base)

    def GetCurrentPlayer(self, team, slot):
        return self.gameiter.GetPlayer(team, slot)

    def GetCurrentPosition(self, team, slot):
        playerId = self.gameiter.GetPlayer(team, slot)
        return cw_gameiter_player_position(self.gameiter, team, playerId)

    def GetInning(self):        return self.gameiter.GetInning()
    def GetHalfInning(self):    return self.gameiter.GetHalfInning()

    def GetScore(self, team):   return self.gameiter.GetTeamScore(team)
    def GetHits(self, team):    return self.gameiter.GetTeamHits(team)
    def GetErrors(self, team):  return self.gameiter.GetTeamErrors(team)
        
    def GetDoublePlays(self, team):
        return self.boxscore.GetDPs(team)
        
    def GetLOB(self, team):
        """
        Returns the number of runners left on base by 'team'.
        Note that the 'official' definition of this also
        includes any players who have come to bat and are
        still on base.
        """
        return cw_gameiter_left_on_base(self.gameiter, team)

    def IsLeadoff(self):
        return self.game.first_event == None or self.gameiter.outs == 3

    def IsGameOver(self):
        event = self.game.last_event
        if event == None:  return False

        if (self.GetInning() >= 9 and self.GetHalfInning() == 1 and
            self.GetScore(1) > self.GetScore(0)):
            return True

        if (self.GetInning() >= 10 and self.GetHalfInning() == 0 and
            event.inning < self.GetInning() and
            self.GetScore(0) > self.GetScore(1)):
            return True
            
        return False
        
    def GetOuts(self):
        if self.gameiter.outs == 3:
            return 0
        else:
            return self.gameiter.outs


