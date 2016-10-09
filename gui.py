# -*- coding: utf-8 -*-
import wx
import sys
#和退出键绑定的事件
def exit(event):
    sys.exit(3)
#抄的一个系统托盘代码自己试不出来所以就这个是用对象写的
class TaskBarIcon(wx.TaskBarIcon):
    ID_ex = wx.NewId()

    def __init__(self, frame):
        wx.TaskBarIcon.__init__(self)
        self.frame = frame
        self.SetIcon(icon,"jlucon")
        self.Bind(wx.EVT_MENU, self.OnEXIT, id=self.ID_ex)

    def OnEXIT(self, event):
        sys.exit(1)
    def CreatePopupMenu(self):
        menu = wx.Menu()
        menu.Append(self.ID_ex, '\xcd\xcb\xb3\xf6')
        return menu
#框架和面板设置
app = wx.App()
initWin = wx.Frame(None, title='jlucon', size=(300, 200))
initWin.Center()
initPanel = wx.Panel(initWin)
#图标设置
icon=wx.EmptyIcon()
icon.LoadFile("py.ico",wx.BITMAP_TYPE_ICO)
initWin.SetIcon(icon)
initWin.tbicon=TaskBarIcon(initWin)
initWin.Bind(wx.EVT_CLOSE,exit)
#调整界面和按钮
def editPn():
    editWin = wx.Frame(initWin, title='@', size=(200, 160))
    editWin.Center()
    editPanel = wx.Panel(editWin)
    editWin.SetIcon(icon)
    userLbl = wx.StaticText(editPanel, -1, '\xd5\xcb\xba\xc5: ', pos=(10, 20))
    passwLbl = wx.StaticText(editPanel, -1, '\xc3\xdc\xc2\xeb: ', pos=(10, 50))
    vtfBtn = wx.Button(editPanel, label='\xc8\xb7\xc8\xcf',
                       pos=(70, 80), size=(80, 30))
    def getData(event):
        if userText.GetValue() and passText.GetValue():
            f = open("D:\drcon.txt","w")
            f.write(userText.GetValue() + '\n' + passText.GetValue())
            initWin.Show()
            editWin.Hide()
            f.close()
    def rew(event):
        editWin.Hide()
        initWin.Show()
    vtfBtn.Bind(wx.EVT_BUTTON, getData)
    editWin.Bind(wx.EVT_CLOSE, rew)
    userText = wx.TextCtrl(editPanel, -1, pos=(50, 15))
    passText = wx.TextCtrl(editPanel, -1, pos=(50, 45), style=wx.TE_PASSWORD)
    editWin.Show()
    initWin.Hide()
    editWin.Show()
def edit(event):
    editPn()
#弹出框设成函数
def alert(msg, cap):
    errormess = wx.MessageDialog(initPanel, message = msg,
                                 caption = cap,
                                 style = wx.OK | wx.ICON_INFORMATION)
    errormess.ShowModal()
#第三个按钮设成事件
def info(event):
alert('\xc3\xe2\xd4\xf0\xc9\xf9\xc3\xf7\xa3\xba\xb4\xcb\xc8\xed\xbc\xfe\xd4\xec\xb3\xc9\xb5\xc4\xc8\xce\xba\xce\xce\xa5\xb1\xb3\xbc\xaa\xc1\xd6\xb4\xf3\xd1\xa7\xd0\xa3\xd4\xb0\xbc\xc6\xcb\xe3\xbb\xfa\xcd\xf8\xc2\xe7\xd3\xc3\xbb\xa7\xca\xd8\xd4\xf2\xb5\xc4\xba\xf3\xb9\xfb\xa3\xac\xd3\xc9\xca\xb9\xd3\xc3\xd5\xdf\xd7\xd4\xd0\xd0\xb3\xd0\xb5\xa3\n')
#设置按钮位置
(posx, posy) = (100, 25)

loginButton = wx.Button(initPanel, label='\xd2\xbb\xbc\xfc\xb5\xc7\xc2\xbc',#一键登录
                        pos=(posx, posy), size=(80, 30))
editButton = wx.Button(initPanel, label='\xd0\xde\xb8\xc4\xd5\xcb\xba\xc5',#修改账号
                       pos=(posx, posy + 40), size=(80, 30))
infoButton = wx.Button(initPanel, label='\xcf\xe0\xb9\xd8\xd0\xc5\xcf\xa2',#相关信息
                       pos=(posx, posy + 80), size=(80, 30))
#给按钮绑定事件
editButton.Bind(wx.EVT_BUTTON, edit)
infoButton.Bind(wx.EVT_BUTTON, info)


