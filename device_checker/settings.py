"""
Settings for application
"""

import copy
import json
import os
import threading
from distutils.version import StrictVersion

import requests
import wx

from device_checker import categories, logger, APP_VERSION
from device_checker import get_write_path, get_root_path

_DEFAULT = {
    'collect': True,
}

FILE_NAME = "settings.json"
ICON_PATH = get_root_path('icon.ico')


def load_settings():
    """
    Loads setting for each category
    """

    path = get_write_path(FILE_NAME)
    if os.path.isfile(path):  # settings file exists
        with open(path, 'r', encoding='utf-8') as f:
            settings = json.load(f)

        for key in categories.CATEGORIES:
            s = copy.deepcopy(_DEFAULT)
            setting = settings.get(key, s)
            categories.CATEGORIES[key]['settings'] = setting

    else:
        settings = {}
        for key in categories.CATEGORIES:
            s = copy.deepcopy(_DEFAULT)
            settings[key] = s
            categories.CATEGORIES[key]['settings'] = s

        settings = json.dumps(settings, sort_keys=True, indent=4)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(settings)


def save_settings():
    """
    Write settings file
    """

    write = {}

    for key, value in categories.CATEGORIES.items():
        write[key] = {
            'collect': value['settings']['collect']
        }

    write = json.dumps(write, indent=4, sort_keys=True)

    path = get_write_path(FILE_NAME)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(write)


class CheckUpdates(threading.Thread):
    """
    Check for updates and update static text
    """

    def __init__(self, text: wx.StaticText, font: wx.Font, on_click):
        """
        :param text: StaticText to update
        :param font: Font to set on text if update is found
        :param on_click: Function to launch for user's on click of text
        """

        threading.Thread.__init__(self)
        self.text = text
        self.font = font
        self.on_click = on_click

    def run(self):
        logger.debug("Checking for updates")
        url = "https://shayConcepts.com/software/device_checker/update"
        is_update = False

        try:
            r = requests.get(url)
        except Exception as e:
            logger.error(e)
            msg = "Failed to connect to update server"
        else:
            if r.ok:
                logger.debug("Update connection - {}".format(r.status_code))
                try:
                    update = r.json()
                    logger.debug(update)
                    version = update['version']
                    if StrictVersion(version) > StrictVersion(APP_VERSION):
                        msg = "Update Available - v{}".format(version)
                        logger.info(msg)
                        is_update = True
                    else:
                        msg = "No update available"
                        logger.debug(msg)
                except Exception as e:
                    logger.error(e)
                    msg = "Failed to parse update"
            else:
                err = "Update HTTP failed - {} - {} - {}".format(url, r.status_code, r.text)
                logger.error(err)
                msg = "Failed to get update"
        logger.debug("Finished update check")

        if is_update:
            wx.EVT_LEFT_DOWN(self.text, self.on_click)
            self.text.SetForegroundColour(wx.BLUE)
            self.text.SetFont(self.font)
        self.text.SetLabelText(msg)


load_settings()
