# Mod from WikiTeam's uploader.py
# <!-- original uploader.py license
# Copyright (C) 2011-2016 WikiTeam
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
# -->

import argparse
import hashlib
import sys
import time

from internetarchive import get_item

# <!-- Hardcoded configuration
lang = "zh"
keywords = ["中小学教育资源平台电子书", "国家基础教育资源网", "国家智慧教育公共服务平台", "国家教育资源公共服务平台", "EBook", "Book", "Textbook", "教科书"]
originalurl = 'https://www.zxx.edu.cn'
identifier = 'cbern.com.cn-textbook'
collection = 'opensource'
title = '中小学教育资源平台电子书'
description = '中小学教育资源平台电子书, 国家基础教育资源网, 国家智慧教育公共服务平台, 国家教育资源公共服务平台'
filelist = ['books_links.txt']
filesdir = 'download'

def getFiles(dir):
    import os
    files = []
    for root, dirs, fs in os.walk(dir):
        for f in fs:
            files.append(os.path.join(root, f))
    return files
def getUserAgent():
    return 'STWP/1.0 (save-web.org)'
# -->

# Nothing to change below
convertlang = {
    "ar": "Arabic",
    "de": "German",
    "en": "English",
    "es": "Spanish",
    "fr": "French",
    "it": "Italian",
    "ja": "Japanese",
    "nl": "Dutch",
    "pl": "Polish",
    "pt": "Portuguese",
    "ru": "Russian",
}

def read_ia_keys(keyfile):
    with open(keyfile) as f:
        key_lines = f.readlines()

        accesskey = key_lines[0].strip()
        secretkey = key_lines[1].strip()

        return {
            "access": accesskey,
            "secret": secretkey
        }

# We have to use md5 because the internet archive API doesn't provide
# sha1 for all files.
def file_md5(path):
    buffer = bytearray(65536)
    view = memoryview(buffer)
    digest = hashlib.md5()

    with open(path, mode="rb") as f:
        while True:
            n = f.readinto(buffer)

            if not n:
                break

            digest.update(view[:n])

    return digest.hexdigest()

def file_sha1(path):
    buffer = bytearray(65536)
    view = memoryview(buffer)
    digest = hashlib.sha1()

    with open(path, mode="rb") as f:
        while True:
            n = f.readinto(buffer)

            if not n:
                break

            digest.update(view[:n])

    return digest.hexdigest()

def upload(filelist, config={}):
    ia_keys = read_ia_keys(config.keysfile)

    headers = {"User-Agent": getUserAgent()}

    # Item metadata
    md = {
        "mediatype": "web",
        "collection": collection,
        "title": title,
        "description": description,
        "language": lang,
        "last-updated-date": time.strftime("%Y-%m-%d"),
        "subject": "; ".join(
            keywords
        ),  # Keywords should be separated by ; but it doesn't matter much; the alternative is to set one per field with subject[0], subject[1], ...
        "originalurl": originalurl,
    }

    # Upload files and update metadata
    try:
        item = get_item(identifier)
        dupCount = 0
        print("Files in item: %s" % len(item.files))
        print("Files to upload: %s" % len(filelist))
        progress = 0
        for fileInItem in item.files:
            progress += 1
            print(progress, fileInItem['name'], end='       \r')
            if (fileInItem['name'] in filelist
                and (fileInItem.get('sha1') == file_sha1(fileInItem['name']))
                ):
                filelist.remove(fileInItem['name'])
                dupCount += 1
        print("Found %d duplicate files" % dupCount)
        print("Files to upload: %s" % len(filelist))
        r = item.upload(
            files=filelist,
            metadata=md,
            access_key=ia_keys["access"],
            secret_key=ia_keys["secret"],
            verbose=True,
            queue_derive=False,
        )

        item.modify_metadata(md)  # update
        print(
            "You can find it in https://archive.org/details/%s"
            % (identifier)
        )
    except Exception as e:
        print(e)


def main(params=[]):
    parser = argparse.ArgumentParser(
        """uploader.py"""
    )
    parser.add_argument("-kf", "--keysfile", default="keys.txt")
    config = parser.parse_args()

    files = getFiles(filesdir)
    filelist.extend(files)
    upload(filelist, config)


if __name__ == "__main__":
    main()
