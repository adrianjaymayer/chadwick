#
# $Source$
# $Date$
# $Revision$
#
# DESCRIPTION:
# Panel for viewing and editing players
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

from wxPython.wx import *
from wxPython.grid import *
import string

from wxutils import FormattedStaticText

class NameValidator(wxPyValidator):
    """
    This validates a text control as a valid name.  We permit
    letters, whitespace, and apostrophes.
    """
    def __init__(self, pyVar=None):
        wxPyValidator.__init__(self)
        EVT_CHAR(self, self.OnChar)

    def TransferToWindow(self):     return True
    def TransferFromWindow(self):   return True 
    def Clone(self):                return NameValidator()

    def Validate(self, win):
        textCtrl = self.GetWindow()
        val = str(textCtrl.GetValue())
        
        for x in val:
            if x not in string.letters and x not in [ " ", "'" ]:
                return false

        return true

    def OnChar(self, event):
        key = event.KeyCode()

        if key < wx.WXK_SPACE or key == wx.WXK_DELETE or key > 255:
            event.Skip()
            return

        if chr(key) in string.letters or chr(key) in [ " ", "'" ]:
            event.Skip()
            return

        if not wx.Validator_IsSilent():
            wxBell()

        # Returning without calling even.Skip eats the event before it
        # gets to the text control
        return


class AddPlayerDialog(wxDialog):
    def __init__(self, parent, book):
        wxDialog.__init__(self, parent, -1, "Add player")
        self.book = book

        self.SetFont(wxFont(10, wxSWISS, wxNORMAL, wxNORMAL))

        sizer = wxFlexGridSizer(6)

        sizer.Add(FormattedStaticText(self, "First name"),
                  0, wxALL | wxALIGN_CENTER, 5)
        self.firstName = wxTextCtrl(self, -1, "",
                                    wxDefaultPosition, wxSize(150, -1))
        self.firstName.SetValidator(NameValidator())
        sizer.Add(self.firstName, 0, wxALL | wxALIGN_CENTER, 5)

        sizer.Add(FormattedStaticText(self, "Last name"),
                  0, wxALL | wxALIGN_CENTER, 5)
        self.lastName = wxTextCtrl(self, -1, "",
                                   wxDefaultPosition, wxSize(150, -1))
        self.lastName.SetValidator(NameValidator())
        sizer.Add(self.lastName, 0, wxALL | wxALIGN_CENTER, 5)

        sizer.Add(FormattedStaticText(self, "Bats"),
                  0, wxALL | wxALIGN_CENTER, 5)
        self.bats = wxChoice(self, -1, wxDefaultPosition, wxSize(150, -1),
                             [ "Unknown", "Right", "Left", "Both" ])
        self.bats.SetSelection(1)
        sizer.Add(self.bats, 0, wxALL | wxALIGN_CENTER, 5)

        sizer.Add(FormattedStaticText(self, "Throws"),
                  0, wxALL | wxALIGN_CENTER, 5)
        self.throws = wxChoice(self, -1, wxDefaultPosition, wxSize(150, -1),
                               [ "Unknown", "Right", "Left" ])
        self.throws.SetSelection(1)
        sizer.Add(self.throws, 0, wxALL | wxALIGN_CENTER, 5)

        sizer.Add(FormattedStaticText(self, "Team"),
                  0, wxALL | wxALIGN_CENTER, 5)
        teamList = [ team.GetName() for team in book.Teams() ]
        self.team = wxChoice(self, -1, wxDefaultPosition, wxSize(150, -1),
                             teamList)
        self.team.SetSelection(0)
        sizer.Add(self.team, 0, wxALL | wxALIGN_CENTER, 5)

        sizer.Add(FormattedStaticText(self, "Player ID"),
                  0, wxALL | wxALIGN_CENTER, 5)
        self.playerID = wxTextCtrl(self, -1, "", wxDefaultPosition,
                                   wxSize(150, -1))
        # The player ID starts out blank, which is invalid
        self.playerID.SetBackgroundColour(wxNamedColour("pink"))
        sizer.Add(self.playerID, 0, wxALL | wxALIGN_CENTER, 5)

        generateButton = wxButton(self, -1, "Generate unique ID")
        generateButton.SetFont(wxFont(10, wxSWISS, wxNORMAL, wxBOLD))
        
        buttonSizer = wxBoxSizer(wxHORIZONTAL)
        buttonSizer.Add(wxButton(self, wxID_CANCEL, "Cancel"),
                                 0, wxALL | wxALIGN_CENTER, 5)
        buttonSizer.Add(wxButton(self, wxID_OK, "OK"), 0,
                        wxALL | wxALIGN_CENTER, 5)
        self.FindWindowById(wxID_OK).Enable(false)
        self.FindWindowById(wxID_OK).SetDefault()

        topSizer = wxBoxSizer(wxVERTICAL)

        topSizer.Add(sizer, 0, wxALL, 5)
        topSizer.Add(generateButton, 0, wxALL | wxALIGN_CENTER, 5)
        topSizer.Add(buttonSizer, 0, wxALIGN_RIGHT, 5)

        self.SetSizer(topSizer)
        self.Layout()
        topSizer.SetSizeHints(self)

        EVT_TEXT(self, self.playerID.GetId(), self.OnIDChange)
        EVT_BUTTON(self, generateButton.GetId(), self.OnGenerateID)

    def OnGenerateID(self, event):
        self.playerID.SetValue(self.book.UniquePlayerID(self.GetFirstName(),
                                                        self.GetLastName()))
        self.playerID.SetBackgroundColour(wxSystemSettings_GetColour(wxSYS_COLOUR_WINDOW))
        self.FindWindowById(wxID_OK).Enable(true)

    def OnIDChange(self, event):
        playerID = self.GetPlayerID()
        if (playerID == "" or
            playerID in [ p.player_id for p in self.book.Players() ]):
            self.FindWindowById(wxID_OK).Enable(false)
            self.playerID.SetBackgroundColour(wxNamedColour("pink"))
        else:
            self.FindWindowById(wxID_OK).Enable(true)
            self.playerID.SetBackgroundColour(wxSystemSettings_GetColour(wxSYS_COLOUR_WINDOW))
        
    def GetPlayerID(self):   return str(self.playerID.GetValue()).strip()
    def GetFirstName(self):  return str(self.firstName.GetValue()).strip()
    def GetLastName(self):   return str(self.lastName.GetValue()).strip()
    def GetBats(self):
        return [ "?", "R", "L", "B" ][self.bats.GetSelection()]
    def GetThrows(self):
        return [ "?", "R", "L" ][self.throws.GetSelection()]
    def GetTeam(self):
        return [ t for t in self.book.Teams() ][self.team.GetSelection()].GetID()
    

class EditPlayerDialog(wxDialog):
    def __init__(self, parent, player):
        wxDialog.__init__(self, parent, -1, "Edit player")

        self.SetFont(wxFont(10, wxSWISS, wxNORMAL, wxNORMAL))
        
        sizer = wxFlexGridSizer(5)

        sizer.Add(FormattedStaticText(self, "First name"),
                  0, wxALL | wxALIGN_CENTER, 5)
        self.firstName = wxTextCtrl(self, -1, player.GetFirstName(),
                                    wxDefaultPosition, wxSize(150, -1))
        self.firstName.SetValidator(NameValidator())
        sizer.Add(self.firstName, 0, wxALL | wxALIGN_CENTER, 5)

        sizer.Add(FormattedStaticText(self, "Last name"),
                  0, wxALL | wxALIGN_CENTER, 5)
        self.lastName = wxTextCtrl(self, -1, player.GetLastName(),
                                   wxDefaultPosition, wxSize(150, -1))
        self.lastName.SetValidator(NameValidator())
        sizer.Add(self.lastName, 0, wxALL | wxALIGN_CENTER, 5)

        sizer.Add(FormattedStaticText(self, "Bats"),
                  0, wxALL | wxALIGN_CENTER, 5)
        self.bats = wxChoice(self, -1, wxDefaultPosition, wxSize(150, -1),
                             [ "Unknown", "Right", "Left", "Both" ])
        self.bats.SetSelection({ "?": 0, "R": 1, "L": 2, "B": 3}[player.bats])
        sizer.Add(self.bats, 0, wxALL | wxALIGN_CENTER, 5)

        sizer.Add(FormattedStaticText(self, "Throws"),
                  0, wxALL | wxALIGN_CENTER, 5)
        self.throws = wxChoice(self, -1, wxDefaultPosition, wxSize(150, -1),
                               [ "Unknown", "Right", "Left" ])
        self.throws.SetSelection({ "?": 0, "R": 1, "L": 2}[player.throws])
        sizer.Add(self.throws, 0, wxALL | wxALIGN_CENTER, 5)

        #sizer.Add(FormattedStaticText(self, "Team"),
        #          0, wxALL | wxALIGN_CENTER, 5)
        #teamList = [ team.GetName() for team in book.Teams() ]
        #self.team = wxChoice(self, -1, wxDefaultPosition, wxSize(150, -1),
        #                     teamList)
        #self.team.SetSelection(0)
        #sizer.Add(self.team, 0, wxALL | wxALIGN_CENTER, 5)

        sizer.Add(FormattedStaticText(self, "Player ID"),
                  0, wxALL | wxALIGN_CENTER, 5)
        self.playerID = wxTextCtrl(self, -1, player.player_id,
                                   wxDefaultPosition,
                                   wxSize(150, -1))
        self.playerID.Enable(False)
        sizer.Add(self.playerID, 0, wxALL | wxALIGN_CENTER, 5)

        buttonSizer = wxBoxSizer(wxHORIZONTAL)
        buttonSizer.Add(wxButton(self, wxID_CANCEL, "Cancel"),
                                 0, wxALL | wxALIGN_CENTER, 5)
        buttonSizer.Add(wxButton(self, wxID_OK, "OK"), 0,
                        wxALL | wxALIGN_CENTER, 5)
        self.FindWindowById(wxID_OK).SetDefault()

        topSizer = wxBoxSizer(wxVERTICAL)

        topSizer.Add(sizer, 0, wxALL, 5)
        topSizer.Add(buttonSizer, 0, wxALIGN_RIGHT, 5)

        self.SetSizer(topSizer)
        self.Layout()
        topSizer.SetSizeHints(self)

    def GetFirstName(self):  return str(self.firstName.GetValue()).strip()
    def GetLastName(self):   return str(self.lastName.GetValue()).strip()
    def GetBats(self):
        return [ "?", "R", "L", "B" ][self.bats.GetSelection()]
    def GetThrows(self):
        return [ "?", "R", "L" ][self.throws.GetSelection()]
    

class PlayerListCtrl(wxListCtrl):
    def __init__(self, parent):
        wxListCtrl.__init__(self, parent, -1,
                            style = wxLC_VIRTUAL | wxLC_REPORT | wxLC_SINGLE_SEL)
        self.firstMenuID = 4000

        self.InsertColumn(0, "Player")
        self.InsertColumn(1, "Bats")
        self.InsertColumn(2, "Throws")
        self.InsertColumn(3, "ID")
        self.InsertColumn(4, "Teams")

        self.SetColumnWidth(0, 250)
        self.SetColumnWidth(1, 75)
        self.SetColumnWidth(2, 75)
        self.SetColumnWidth(3, 100)
        self.SetColumnWidth(4, 150)
        
        EVT_LIST_ITEM_ACTIVATED(self, self.GetId(), self.OnItemActivated)
        EVT_LIST_ITEM_RIGHT_CLICK(self, self.GetId(), self.OnRightClick)
        EVT_MENU_RANGE(self, self.firstMenuID, self.firstMenuID + 100,
                       self.OnMenu)
        
    def OnUpdate(self, book):
        self.book = book
        self.SetItemCount(book.NumPlayers())

    def OnGetItemText(self, item, col):
        player = [x for x in self.book.Players()][item]
        if col == 0:
            return player.GetSortName()
        elif col == 1:
            return { "R": "Right", "L": "Left",
                     "B": "Both", "?": "Unknown" }[player.GetBats()]
        elif col == 2:
            return { "R": "Right", "L": "Left",
                     "B": "Both", "?": "Unknown" }[player.GetThrows()]
        elif col == 3:
            return player.GetID()
        else:
            return string.join(player.GetTeams(), ", ")
        

    def OnItemActivated(self, event):
        player = [x for x in self.book.Players()][event.GetIndex()]
        dialog = EditPlayerDialog(self, player)
        if dialog.ShowModal() == wxID_OK:
            self.book.ModifyPlayer(player.player_id,
                                   dialog.GetFirstName(),
                                   dialog.GetLastName(),
                                   dialog.GetBats(),
                                   dialog.GetThrows())
            self.GetParent().GetGrandParent().OnUpdate()
            return

    def OnRightClick(self, event):
        player = [x for x in self.book.Players()][event.GetIndex()]
        self.menuPlayer = player
        menu = wxMenu("Add %s to roster of" % player.GetName())

        menuID = self.firstMenuID
        for t in self.book.Teams():
            if t.GetID() not in player.GetTeams():
                menu.Append(menuID, t.GetName(),
                            "Add to %s" % t.GetName())
                menuID += 1
                
        self.PopupMenu(menu)

    def OnMenu(self, event):
        menuID = self.firstMenuID

        for t in self.book.Teams():
            if t.GetID() not in self.menuPlayer.GetTeams():
                if menuID == event.GetId():
                    self.book.AddToTeam(self.menuPlayer.player_id,
                                        self.menuPlayer.GetFirstName(),
                                        self.menuPlayer.GetLastName(),
                                        self.menuPlayer.bats,
                                        self.menuPlayer.throws,
                                        t.GetID())
                    self.GetParent().GetGrandParent().OnUpdate()
                    return
                menuID += 1

class PlayerListPanel(wxPanel):
    def __init__(self, parent):
        wxPanel.__init__(self, parent, -1)

        newPlayerButton = wxButton(self, -1, "Add player")
        newPlayerButton.SetFont(wxFont(10, wxSWISS, wxNORMAL, wxBOLD))
        self.playerList = PlayerListCtrl(self)

        sizer = wxBoxSizer(wxVERTICAL)
        sizer.Add(newPlayerButton, 0, wxALL | wxALIGN_CENTER, 5)
        sizer.Add(self.playerList, 1, wxEXPAND, 0)
        self.SetSizer(sizer)
        self.Layout()

        EVT_BUTTON(self, newPlayerButton.GetId(), self.OnNewPlayer)

    def OnNewPlayer(self, event):
        dialog = AddPlayerDialog(self, self.book)

        if dialog.ShowModal() == wxID_OK:
            self.book.AddPlayer(dialog.GetPlayerID(),
                                dialog.GetFirstName(),
                                dialog.GetLastName(),
                                dialog.GetBats(),
                                dialog.GetThrows(),
                                dialog.GetTeam())
            self.GetGrandParent().OnUpdate()

    def OnUpdate(self, book):
        self.book = book
        self.playerList.OnUpdate(book)
