#!/usr/bin/env python

# python-gphoto2 - Python interface to libgphoto2
# http://github.com/jim-easterbrook/python-gphoto2
# Copyright (C) 2014-19  Jim Easterbrook  jim@jim-easterbrook.me.uk
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import print_function

from datetime import datetime, date
import logging
import os
import sys
import time

import gphoto2 as gp

def get_target_dir(timestamp):
    return os.path.join(PHOTO_DIR, timestamp.strftime('%Y/%Y_%m_%d/'))

def list_computer_files():
    result = []
    for root, dirs, files in os.walk(os.path.expanduser(PHOTO_DIR)):
        for name in files:
            if '.thumbs' in dirs:
                dirs.remove('.thumbs')
            if name in ('.directory',):
                continue
            ext = os.path.splitext(name)[1].lower()
            if ext in ('.db',):
                continue
            result.append(os.path.join(root, name))
    return result

def list_camera_files(camera, path='/'):
    result = []
    # get files
    gp_list = gp.check_result(
        gp.gp_camera_folder_list_files(camera, path))
    for name, value in gp_list:
        result.append(os.path.join(path, name))
    # read folders
    folders = []
    gp_list = gp.check_result(
        gp.gp_camera_folder_list_folders(camera, path))
    for name, value in gp_list:
        folders.append(name)
    # recurse over subfolders
    for name in folders:
        result.extend(list_camera_files(camera, os.path.join(path, name)))
    return result

def get_camera_file_info(camera, path):
    folder, name = os.path.split(path)
    return gp.check_result(
        gp.gp_camera_file_get_info(camera, folder, name))

# takes a date (yyyy-MM-dd) as input
# returns 1 when files are copied correctly
# returns 0 when no device was found
# raises an error when something unexpected happend
def copy_files(date_string):
    input_date = date.fromisoformat(date_string)
    camera = gp.check_result(gp.gp_camera_new())

    error = gp.gp_camera_init(camera)
    if error == gp.GP_ERROR_MODEL_NOT_FOUND:
        return 0
    if error != gp.GP_ERROR_MODEL_NOT_FOUND:
        # some other error we can't handle here
        raise gp.GPhoto2Error(error)

    computer_files = list_computer_files()
    camera_files = list_camera_files(camera)
    if not camera_files:
        # no files were found
        return 0

    for path in camera_files:
        info = get_camera_file_info(camera, path)
        timestamp = datetime.fromtimestamp(info.file.mtime)
        if intput_date != timestamp.date:
            continue
        folder, name = os.path.split(path)
        dest_dir = get_target_dir(timestamp)
        dest = os.path.join(dest_dir, name)
        if dest in computer_files:
            continue
        print('%s -> %s' % (path, dest_dir))
        if not os.path.isdir(dest_dir):
            os.makedirs(dest_dir)
        camera_file = gp.check_result(gp.gp_camera_file_get(
            camera, folder, name, gp.GP_FILE_TYPE_NORMAL))
        gp.check_result(gp.gp_file_save(camera_file, dest))
    gp.check_result(gp.gp_camera_exit(camera))
    return 1

def main():
    logging.basicConfig(
        format='%(levelname)s: %(name)s: %(message)s', level=logging.WARNING)
    callback_obj = gp.check_result(gp.use_python_logging())
    computer_files = list_computer_files()
    camera = gp.check_result(gp.gp_camera_new())

    print('Please connect and switch on your camera')
    while True:
        error = gp.gp_camera_init(camera)
        if error >= gp.GP_OK:
            # operation completed successfully so exit loop
            break
        if error != gp.GP_ERROR_MODEL_NOT_FOUND:
            # some other error we can't handle here
            raise gp.GPhoto2Error(error)
        time.sleep(2)

    print('Getting list of files from camera...')
    camera_files = list_camera_files(camera)
    if not camera_files:
        print('No files found')
        return 1
    for path in camera_files:
        print(path)
    
    print('Copying files...')
    for path in camera_files:
        info = get_camera_file_info(camera, path)
        timestamp = datetime.fromtimestamp(info.file.mtime)
        folder, name = os.path.split(path)
        dest_dir = get_target_dir(timestamp)
        dest = os.path.join(dest_dir, name)
        if dest in computer_files:
            continue
        print('%s -> %s' % (path, dest_dir))
        if not os.path.isdir(dest_dir):
            os.makedirs(dest_dir)
        camera_file = gp.check_result(gp.gp_camera_file_get(
            camera, folder, name, gp.GP_FILE_TYPE_NORMAL))
        gp.check_result(gp.gp_file_save(camera_file, dest))
    gp.check_result(gp.gp_camera_exit(camera))
    return 0

if __name__ == "__main__":
    sys.exit(main())
