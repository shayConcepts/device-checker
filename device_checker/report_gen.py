"""
Generate reports to display
"""

import json
import os

from device_checker import categories, get_write_path

BACKGROUND_COLOR = 'white'
FONT_SIZE = None
FONT_FACE_NAME = None
LINE_HEIGHT = '150%'
TAB = "&nbsp;" * 4


def _add_html_tags(body: str) -> str:
    """
    Add HTML and CSS tags to body of HTML

    :param body: Body of HTML
    :return: New HTML
    """

    css = "background-color: white;"
    css += "font: {}px {};".format(FONT_SIZE, FONT_FACE_NAME)
    css += "line-height: {};".format(LINE_HEIGHT)
    html = '<html><body style="{}">{}</body></html>'.format(css, body)

    return html


def _get_category(category: str) -> dict:
    """
    Get category dict by string name

    :param category: Name of category
    :return: Category dict
    """

    return [value for _, value in categories.CATEGORIES.items() if value['name'] == category][0]


def _load_json(file_path: str):
    """
    Load JSON from file

    :param file_path: Path to JSON
    :return: Loaded JSON
    """

    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    return data


def get_data(category: str) -> str:
    """
    Generate HTML for Data

    :param category: Item to generate report for
    :return: HTML for Data
    """

    category = _get_category(category)
    file_name = "raw_{}".format(category['file'])

    path = get_write_path(file_name)
    if not os.path.exists(path):
        html = "Data has not been generated. Cannot find '{}'".format(file_name)
    else:
        data = _load_json(path)

        html = ''
        for item in data:
            title = category['title']
            title = title.format(*[item[k] for k in category['title_keys']])
            header = "<strong>{}</strong><br>".format(title)
            html += header

            for key, value in item.items():
                line = "{}{}: &nbsp;&nbsp;&nbsp;{}<br>".format(TAB, key, value)
                html += line

            html += "<br>"

        if html == '':
            html = "Your system did not report any data for {}".format(category['name'])

    html = _add_html_tags(html)
    return html


def get_changed_data(category: str) -> str:
    """
    Generate HTML for Changed Data

    :param category: Item to generate report for
    :return: HTML for Data
    """

    category = _get_category(category)
    data = category['diff']

    changed = data['changed']
    removed = data['removed']
    new = data['new']

    html = ''
    if new:
        html += "<h2><u>New</u></h2>"

        for item in new:
            title = category['title']
            title = title.format(*[item[k] for k in category['title_keys']])
            header = "<strong>{}</strong><br>".format(title)
            html += header

            for key, value in item.items():
                line = "{}{}: &nbsp;&nbsp;&nbsp;{}<br>".format(TAB, key, value)
                html += line

            html += "<br>"

    if changed:
        html += "<h2><u>Changed - BEFORE &rarr; AFTER</u></h2>"

        for original_item, new_item, keys in changed:
            cat_title = category['title'].format(*[original_item[k] for k in category['title_keys']])
            html += "<br>{}".format(TAB) + "<b>{}</b>".format(cat_title)
            for k in keys:
                html += "<br>{}{}{}: {} <b>&rarr;</b> {}".format(TAB, TAB, k, original_item[k], new_item[k])
            html += "<br>"

    if removed:
        html += "<h2><u>Removed</u></h2>"

        for item in removed:
            title = category['title']
            title = title.format(*[item[k] for k in category['title_keys']])
            header = "<strong>{}</strong><br>".format(title)
            html += header

            for key, value in item.items():
                line = "{}{}: &nbsp;&nbsp;&nbsp;{}<br>".format(TAB, key, value)
                html += line

            html += "<br>"

    html = _add_html_tags(html)
    return html
