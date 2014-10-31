#!/usr/bin/env python
# coding: utf-8

import wx

class TestFrame(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, wx.ID_ANY, title=title)
        text = wx.StaticText(self, label="Hallo Welt!")

app = wx.PySimpleApp(0)
frame = TestFrame(None, "Ein kleines Beispiel")
frame.Show()
app.MainLoop()

