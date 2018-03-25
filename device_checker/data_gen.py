"""
Generates data
"""

import json
import locale
import os
import subprocess
from typing import List

from device_checker import logger, get_write_path
from device_checker.categories import CATEGORIES

_ENCODING = locale.getdefaultlocale()[1]


def execute(command: str) -> tuple:
    """
    Execute command

    :param command: Command to execute
    :return: Code, stdout, stderr
    """

    p = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    out = p.stdout.decode(_ENCODING)
    err = p.stderr.decode(_ENCODING)
    code = p.returncode
    out = out.strip()

    return code, out, err


def keep_object(item_name: str, obj: dict) -> bool:
    """
    Determine if obj should be filtered out

    :param item_name: Name of item
    :param obj: Object to check
    :return: If obj should be kept
    """

    if item_name == 'Services':
        path_name = obj.get('PathName', '')
        if path_name.lower().startswith(r'C:\WINDOWS\System32\svchost.exe -k'.lower()):
            return False

    return True


def parse_out(item_name: str, text: str) -> List[dict]:
    """
    Parse the output of WMIC command

    :param item_name:
    :param text:
    :return: List of objects from output
    """

    objects = []
    obj = {}
    blank_line_counter = 0
    lines = text.splitlines()
    for line in lines:
        line = line.strip()

        if line == '':
            blank_line_counter += 1
            continue

        if blank_line_counter == 5:
            # blank_line_counter = 0
            if keep_object(item_name, obj):  # TODO only use keep_object on diff?
                objects.append(obj)
            obj = {}
            # continue

        blank_line_counter = 0
        split = line.split('=')

        key = split[0]
        value = '='.join(split[1:])
        obj[key] = value.strip()

    if keep_object(item_name, obj):  # TODO only use keep_object on diff?
        objects.append(obj)

    return objects


def get_diff(item, old_objects, new_objects):
    hash_keys = item['hash_key']
    if not isinstance(hash_keys, list):
        hash_keys = [hash_keys]
    compare_keys = item['compare_keys']
    new = []
    removed = []
    changed = []

    for old_obj in old_objects:

        obj_found = False
        new_obj = None
        for new_obj in new_objects:
            obj_found = True
            for k in hash_keys:
                if new_obj[k] != old_obj[k]:
                    obj_found = False
                    break
            if obj_found:
                break

        # Check if and keys changed
        if obj_found:
            changed_keys = []
            for k in compare_keys:
                if old_obj[k] != new_obj[k]:
                    changed_keys.append(k)
            if changed_keys:
                changed.append((old_obj, new_obj, changed_keys))

        # objects removed
        else:
            removed.append(old_obj)

    # new objects
    for new_obj in new_objects:
        is_new = True
        for old_obj in old_objects:
            for k in hash_keys:
                if new_obj[k] != old_obj[k]:
                    break
            else:  # nobreak
                is_new = False
                break

        if is_new:
            new.append(new_obj)

    return changed, new, removed


def report(item, changed, new, removed):
    logger.debug('\n\n')
    if changed:
        logger.debug("The following {} have CHANGED - BEFORE -> AFTER".format(item['name']))
        for o, n, keys in changed:
            logger.debug("\t" + item['title'].format(*[o[k] for k in item['title_keys']]))
            for k in keys:
                logger.debug("\t\t{}: {} -> {}".format(k, o[k], n[k]))
                logger.debug('\n')
    if new:
        logger.debug("The following {} have been ADDED".format(item['name']))
        for n in new:
            logger.debug(json.dumps(n, indent=4, sort_keys=True))

    if removed:
        logger.debug("The following {} have been REMOVED".format(item['name']))
        for r in removed:
            logger.debug(json.dumps(r, indent=4, sort_keys=True))


def delete_diffs():
    """
    Delete diff files
    """

    for c, value in CATEGORIES.items():
        file_name = "diff_{}".format(value['file'])
        path = get_write_path(file_name)
        if os.path.exists(path):
            os.remove(path)


def load_existing_diff(file_name: str) -> tuple:
    """
    Load existing diffs

    :param file_name:
    :return: Tuple of changed items, new items and removed items
    """

    path = get_write_path(file_name)
    if os.path.exists(path):
        with open(path, encoding='utf-8') as f:
            diff = f.read()
        diff = json.loads(diff)

        changed = diff['changed']
        new = diff['new']
        removed = diff['removed']
    else:
        changed, new, removed = [], [], []

    return changed, new, removed


def write_diff(item, changed, new, removed):
    """
    Write diff files
    """

    diff = {
        'changed': changed,
        'new': new,
        'removed': removed,
    }

    file_name = "diff_{}".format(item['file'])
    existing_changed, existing_new, existing_removed = load_existing_diff(file_name)
    changed.extend(existing_changed)
    new.extend(existing_new)
    removed.extend(existing_removed)

    path = get_write_path(file_name)
    if changed or new or removed:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(json.dumps(diff, indent=4, sort_keys=True))
    else:
        if os.path.exists(path):
            os.remove(path)


def process_item(item):
    """
    Process an item
    """

    cmd = "{} {}".format(item['command'], item['command_postfix'])
    code, out, err = execute(cmd)

    if code != 0 or out == '':
        if err.strip() == 'No Instance(s) Available.':
            objects = []
        else:
            raise Exception(cmd)
    else:
        objects = parse_out(item['name'], out)

    file_name = "raw_{}".format(item['file'])
    path = get_write_path(file_name)
    # Get old objects
    if os.path.isfile(path):
        with open(path, 'r', encoding='utf-8') as f:
            old_objects = json.loads(f.read())
    else:
        old_objects = []

    # Write new objects
    with open(path, 'w', encoding='utf-8') as f:
        f.write(json.dumps(objects, indent=4, sort_keys=True))

    changed, new, removed = get_diff(item, old_objects, objects)
    write_diff(item, changed, new, removed)
    report(item, changed, new, removed)

    return changed or new or removed


def main():
    for c in CATEGORIES:
        logger.info("{}".format(c['name']))
        process_item(c)
