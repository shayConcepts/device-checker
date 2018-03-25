"""
Device Checker Main
"""

import argparse
import threading
import webbrowser

import wx
import wx.html2

from device_checker import about
from device_checker import categories
from device_checker import data_gen
from device_checker import logger
from device_checker import report_gen
from device_checker import settings
from device_checker import toast
from device_checker.__info__ import APP_NAME, APP_VERSION, APP_NAME_NO_SPACE


class ReportViewer(wx.Panel):
    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)

        sizer = wx.BoxSizer(wx.VERTICAL)
        self.browser = wx.html2.WebView.New(self)

        font = self.GetFont()
        color = wx.SystemSettings.GetColour(wx.SYS_COLOUR_3DFACE)
        css = "background-color: rgb({},{},{});".format(color.red, color.blue, color.green)
        css += "font: {}px {};".format(font.PixelSize.Height, font.FaceName)
        css += "line-height: 16px;"
        html = '<!DOCTYPE html><html><body style="{}">{}</body></html>'.format(css, about.get_welcome_page())
        self.browser.SetPage(html, "")

        sizer.Add(self.browser, 1, wx.EXPAND, 10)
        self.SetSizer(sizer)
        self.SetSize((700, 700))


class ChangedData(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent.side_panel)

        self.parent = parent

        name = "View Changed Data"
        box = wx.StaticBox(self, -1, name)

        self.choice = wx.Choice(self, id=-1)
        self.set_choices()
        self.choice.Bind(wx.EVT_CHOICE, self.onChoice)

        sizer = wx.StaticBoxSizer(box, wx.VERTICAL)

        sizer.Add(self.choice)
        self.SetSizer(sizer)

    def set_choices(self):
        choices = [value['name'] for _, value in categories.CATEGORIES.items() if value['diff']]
        self.choice.SetItems(choices)

    def onChoice(self, event):
        selection = self.choice.GetStringSelection()
        html = report_gen.get_changed_data(selection)
        self.parent.data_panel.browser.SetPage(html, "")


class Data(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent.side_panel)

        self.parent = parent

        name = "View Last Data"
        box = wx.StaticBox(self, -1, name)
        choices = []
        for key in sorted(categories.CATEGORIES.keys()):
            value = categories.CATEGORIES[key]
            choices.append(value['name'])
        self.choice = wx.Choice(self, id=-1, choices=choices)
        self.choice.Bind(wx.EVT_CHOICE, self.onChoice)

        sizer = wx.StaticBoxSizer(box, wx.VERTICAL)

        sizer.Add(self.choice)
        self.SetSizer(sizer)

    def onChoice(self, event):
        selection = self.choice.GetStringSelection()
        html = report_gen.get_data(selection)
        self.parent.data_panel.browser.SetPage(html, "")


EVT_RESULT_ID = wx.NewId()


def connect_result(win, func):
    win.Connect(-1, -1, EVT_RESULT_ID, func)


class CloseEvent(wx.PyEvent):
    def __init__(self):
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_RESULT_ID)


class DataGenDialog(wx.Dialog):
    def __init__(self, parent, title):
        """
        :param MainWindow parent:
        :param title:
        """
        wx.Dialog.__init__(self, parent, title=title)

        self.parent = parent
        self.cancel_clicked = False
        self.data_finished = False

        # Widgets
        self.txt = wx.StaticText(self, label="")
        self.cancel = wx.Button(self, wx.ID_CANCEL)
        wx.EVT_BUTTON(self, wx.ID_CANCEL, self.onCancel)

        # Layout
        self.Sizer = wx.BoxSizer(wx.VERTICAL)  # using the Sizer property
        self.Sizer.Add(self.txt, 0, wx.ALL, 10)
        self.Sizer.Add(wx.StaticLine(self), 0, wx.EXPAND)

        # make a new sizer to hold the buttons
        row = wx.BoxSizer(wx.HORIZONTAL)
        row.Add((1, 1), 200)  # a spacer that gets a portion of the free space
        row.Add(self.cancel)
        row.Add((1, 1), 1)

        # add that sizer to the main sizer
        self.Sizer.Add(row, 0, wx.EXPAND | wx.ALL, 10)

        # size the dialog to fit the content managed by the sizer
        self.Fit()

        connect_result(self, self.onCancel)

        self.GetData(self).start()

    def onCancel(self, event):
        if not self.data_finished:
            self.cancel_clicked = True
            self.cancel.SetLabelText('Stopping....')
        elif not self.cancel_clicked:
            return self.Destroy()

    class GetData(threading.Thread):
        def __init__(self, dialog):
            threading.Thread.__init__(self)
            self.dialog = dialog  # type: DataGenDialog

        def run(self):
            total = len(categories.CATEGORIES) - 1
            index = 0
            for key in sorted(categories.CATEGORIES.keys()):
                value = categories.CATEGORIES[key]
                if self.dialog.cancel_clicked:
                    break
                msg = "{} {}/{}".format(value['name'], index, total)
                self.dialog.txt.SetLabelText(msg)
                index += 1
                if not value['settings']['collect']:
                    continue
                data_gen.process_item(value)

            self.dialog.txt.SetLabelText("Reloading data")
            categories.load_categories()
            self.dialog.parent.panel_changed.set_choices()

            self.dialog.data_finished = True
            self.dialog.txt.SetLabelText('Finished')
            self.dialog.cancel.SetLabelText('Close')

            if self.dialog.cancel_clicked:
                self.dialog.cancel_clicked = False
                # destroy event
                wx.PostEvent(self.dialog, CloseEvent())


class MainWindow(wx.Frame):

    def __init__(self):
        wx.Frame.__init__(self, None, title=APP_NAME)

        self.set_report_styles()

        self.set_icon()

        self.data_panel = ReportViewer(self)
        self.side_panel = wx.Panel(self)

        self.cmd_panel = wx.Panel(self.side_panel, -1)
        box = wx.StaticBox(self.cmd_panel, -1, 'Report')
        self.sub_panel = wx.Panel(self.cmd_panel, -1)
        sizer = wx.GridSizer(rows=1, cols=2, vgap=4, hgap=4)
        border = 'wxMac' in wx.PlatformInfo and 3 or 1
        for name, handler in (
            ('Generate New', self.generate),
            ('Delete Changed Data', self.mark_read)
        ):
            button = wx.Button(self.sub_panel, -1, name)
            button.Bind(wx.EVT_BUTTON, handler)
            sizer.Add(button, 0, wx.EXPAND | wx.ALL, border)
        self.sub_panel.SetSizer(sizer)

        sizer = wx.StaticBoxSizer(box, wx.VERTICAL)
        sizer.Add(self.sub_panel)
        self.cmd_panel.SetSizer(sizer)

        self.option_panel = wx.Panel(self.side_panel, -1)
        option_box = wx.StaticBox(self.option_panel, -1, 'Data to Collect')
        self.option_sub_panel = wx.Panel(self.option_panel, -1)
        option_sizer = wx.GridSizer(rows=9, cols=3, vgap=4, hgap=4)

        self.setting_boxes = {}
        for key in sorted(categories.CATEGORIES.keys()):
            value = categories.CATEGORIES[key]
            name = value['name']
            setting = value['settings']
            is_checked = setting['collect']
            setting_box = wx.CheckBox(self.option_sub_panel, label=name)
            setting_box.SetValue(is_checked)
            option_sizer.Add(setting_box, 0, wx.EXPAND | wx.ALL, border)
            self.setting_boxes[key] = setting_box

        self.option_sub_panel.SetSizer(option_sizer)

        ###
        self.option_save_panel = wx.Panel(self.option_panel, -1)
        option_save_sizer = wx.GridSizer(rows=1, cols=3, vgap=1, hgap=1)

        button = wx.Button(self.option_save_panel, -1, "Save")
        button.Bind(wx.EVT_BUTTON, self.save_settings)
        option_save_sizer.Add(button, 0, wx.EXPAND | wx.ALL, border)

        button = wx.Button(self.option_save_panel, -1, "Check All")
        button.Bind(wx.EVT_BUTTON, self.check_all)
        option_save_sizer.Add(button, 0, wx.EXPAND | wx.ALL, border)

        button = wx.Button(self.option_save_panel, -1, "Uncheck All")
        button.Bind(wx.EVT_BUTTON, self.uncheck_all)
        option_save_sizer.Add(button, 0, wx.EXPAND | wx.ALL, border)

        self.option_save_panel.SetSizer(option_save_sizer)
        ###

        option_sizer = wx.StaticBoxSizer(option_box, wx.VERTICAL)
        option_sizer.Add(self.option_sub_panel)
        option_sizer.Add(self.option_save_panel)

        self.option_panel.SetSizer(option_sizer)

        self.panel_changed = ChangedData(self)
        self.panel_all_data = Data(self)

        # -- About
        self.about_panel = wx.Panel(self.side_panel, -1)
        about_box = wx.StaticBox(self.about_panel, -1, 'About')
        self.about_sub_panel = wx.Panel(self.about_panel, -1)
        about_sizer = wx.GridSizer(rows=3, cols=1, vgap=4, hgap=4)

        program_title = wx.StaticText(self.about_sub_panel, id=-1, label="{} beta - v{}".format(APP_NAME, APP_VERSION))
        about_sizer.Add(program_title, 0, wx.EXPAND | wx.ALL, border)

        website_link = wx.StaticText(self.about_sub_panel, id=-1, label="shayConcepts.com")

        font = self.GetFont()
        font = wx.Font(
            program_title.GetFont().GetPointSize(),
            wx.FONTFAMILY_DEFAULT,
            wx.FONTSTYLE_NORMAL,
            wx.NORMAL,
            underline=True,
            faceName=font.FaceName
        )
        website_link.SetForegroundColour(wx.BLUE)
        website_link.SetFont(font)
        wx.EVT_LEFT_DOWN(website_link, self.launch_website)
        about_sizer.Add(website_link, 0, wx.EXPAND | wx.ALL, border)

        update_text = wx.StaticText(self.about_sub_panel, id=-1, label="Checking for updates...                     ")
        about_sizer.Add(update_text, 0, wx.EXPAND | wx.ALL, border)

        self.about_sub_panel.SetSizer(about_sizer)

        about_sizer = wx.StaticBoxSizer(about_box, wx.VERTICAL)
        about_sizer.Add(self.about_sub_panel)

        self.about_panel.SetSizer(about_sizer)
        # --

        # -- Attach all to side panel
        panel_sizer = wx.BoxSizer(wx.VERTICAL)
        panel_sizer.Add(self.cmd_panel, 0, wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, 5)
        panel_sizer.Add(self.panel_changed, 0, wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, 5)
        panel_sizer.Add(self.panel_all_data, 0, wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, 5)
        panel_sizer.Add(self.option_panel, 0, wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, 5)
        panel_sizer.Add(self.about_panel, 0, wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, 5)
        self.side_panel.SetSizer(panel_sizer)
        # --

        # -- Setup main panels
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        main_sizer.Add(self.side_panel, 0, wx.EXPAND)
        main_sizer.Add(self.data_panel, 1, wx.EXPAND)
        self.SetSizer(main_sizer)
        # --

        main_sizer.Fit(self)
        rw, rh = self.data_panel.GetSize()
        fw, fh = self.GetSize()
        h = max(600, fh)
        w = h + fw - rw
        self.SetSize((w, h))
        self.Show()
        settings.CheckUpdates(update_text, font, self.launch_website).start()

    def set_report_styles(self):
        """
        Set styles for HTML reports
        """

        font = self.GetFont()
        report_gen.FONT_SIZE = font.PixelSize.Height
        report_gen.FONT_FACE_NAME = font.FaceName

    @staticmethod
    def launch_website(event):
        webbrowser.open("https://shayconcepts.com")

    def generate(self, event):
        dlg = DataGenDialog(self, "Generating Data")
        dlg.ShowModal()
        dlg.Destroy()

    def mark_read(self, event):
        data_gen.delete_diffs()
        self.panel_changed.choice.SetItems([])

    def set_icon(self):
        ib = wx.IconBundle()
        ib.AddIcon(settings.ICON_PATH, wx.BITMAP_TYPE_ANY)
        self.SetIcons(ib)

    def save_settings(self, event):
        settings_boxes = self.setting_boxes

        for key, box in settings_boxes.items():
            collect = box.GetValue()
            categories.CATEGORIES[key]['settings']['collect'] = collect

        settings.save_settings()

    def check_all(self, event):

        for key, box in self.setting_boxes.items():
            box.SetValue(True)

    def uncheck_all(self, event):
        for key, box in self.setting_boxes.items():
            box.SetValue(False)


def launch_gui(is_running, running_msg):
    app = wx.App(False)
    if is_running:
        logger.critical(running_msg)
        wx.MessageBox(running_msg, APP_NAME,
                      wx.OK | wx.ICON_ERROR)
    else:
        MainWindow()
        app.MainLoop()


def generate():
    total = len(categories.CATEGORIES) - 1
    index = 0
    data_changed = False
    for key in sorted(categories.CATEGORIES.keys()):
        value = categories.CATEGORIES[key]
        msg = "{} {}/{}".format(value['name'], index, total)
        logger.info(msg)
        index += 1
        if not value['settings']['collect']:
            continue
        change_occurred = data_gen.process_item(value)
        if change_occurred:
            data_changed = True

    logger.info('Finished')
    if data_changed:
        msg = "Data has changed"
        logger.info(msg)
        toast.balloon_tip(msg)


if __name__ == '__main__':

    id_name = "{}-{}".format(APP_NAME_NO_SPACE, wx.GetUserId())
    checker = wx.SingleInstanceChecker(id_name)
    run_msg = "This program is already running. Stop the other instance or wait for it to finish running."

    parser = argparse.ArgumentParser()
    parser.add_argument('--generate', help='Generate Data only', action='store_true')
    parser.add_argument('--log', help="Set logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL")
    args = vars(parser.parse_args())

    if args['log']:
        logger.debug("Changing log level: '{}'".format(args['log']))
        logger.setLevel(args['log'])

    if args['generate']:
        if checker.IsAnotherRunning():
            logger.critical(run_msg)
        else:
            generate()
    else:
        launch_gui(checker.IsAnotherRunning(), run_msg)
