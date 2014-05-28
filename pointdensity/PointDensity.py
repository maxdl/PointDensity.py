#!/usr/bin/env python

import wx
import wxFrame

class App(wx.App):
    def OnInit(self):
        self.main = wxFrame.wxFrame(None)
        self.main.Show(True)
        self.SetTopWindow(self.main)
        return True

def main():
    application = App(0)
    application.MainLoop()

if __name__ == '__main__':
    main()
