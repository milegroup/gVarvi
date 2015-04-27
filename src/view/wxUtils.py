# coding=utf-8
__author__ = 'nico'
import wx


class InfoDialog(wx.MessageDialog):
    """
    Dialog that shows an info message
    :param msg:  Specific message that dialog shows
    """

    def __init__(self, msg):
        wx.MessageDialog.__init__(self, None, msg, "Info", wx.OK | wx.ICON_INFORMATION)

    def show(self):
        """
        Shows the dialog
        """
        self.ShowModal()
        self.Destroy()


class ErrorDialog(wx.MessageDialog):
    """
    Dialog that shows an error message
    :param msg:  Specific message that dialog shows
    """

    def __init__(self, msg):
        wx.MessageDialog.__init__(self, None, msg, "Error", wx.OK | wx.ICON_ERROR)

    def show(self):
        """
        Shows the dialog
        """
        self.ShowModal()
        self.Destroy()


class ConfirmDialog(wx.MessageDialog):
    """
    Dialog that ask for user confirmation
    :param msg: Message of the dialog
    :param title: Title of the dialog
    """

    def __init__(self, msg, title):
        wx.MessageDialog.__init__(self, None, msg, title,
                                  wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)

    def get_result(self):
        """
        Gets the button pressed by the user
        :return: The pressed button id
        """
        result = self.ShowModal()
        self.Destroy()
        return result
