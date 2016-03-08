import wx
class MainWindow(wx.Frame):
    def __init__(self, *args, **kwargs):
        wx.Frame.__init__(self, *args, **kwargs)

        self.panel = wx.Panel(self)
        self.label = wx.StaticText(self.panel, label="Test", style=wx.ALIGN_CENTRE)
        self.button = wx.Button(self.panel, label="Change")

        self.sizer = wx.BoxSizer()
        self.sizer.Add(self.label, 1)
        self.sizer.Add(self.button)

        self.button.Bind(wx.EVT_BUTTON, self.OnButton)

        self.panel.SetSizerAndFit(self.sizer)  
        self.Show()

    def OnButton(self, e):
        self.label.SetLabel("Oh, this is very looooong!")
        self.sizer.Layout()
        # self.panel.Layout()  #Either works

app = wx.App(False)
win = MainWindow(None)
app.MainLoop()