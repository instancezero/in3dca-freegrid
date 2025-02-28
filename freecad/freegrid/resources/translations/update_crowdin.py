#!/usr/bin/env python3

# SPDX-License-Identifier: LGPL-2.1-or-later
# ***************************************************************************
# *                                                                         *
# *   Copyright (c) 2015 Yorik van Havre <yorik@uncreated.net>              *
# *   Copyright (c) 2021 Benjamin Nauck <benjamin@nauck.se>                 *
# *   Copyright (c) 2021 Mattias Pierre <github@mattiaspierre.com>          *
# *   Copyright (c) 2025 hasecilu <hasecilu@tuta.io>                        *
# *                                                                         *
# *   This file is part of FreeCAD.                                         *
# *                                                                         *
# *   FreeCAD is free software: you can redistribute it and/or modify it    *
# *   under the terms of the GNU Lesser General Public License as           *
# *   published by the Free Software Foundation, either version 2.1 of the  *
# *   License, or (at your option) any later version.                       *
# *                                                                         *
# *   FreeCAD is distributed in the hope that it will be useful, but        *
# *   WITHOUT ANY WARRANTY; without even the implied warranty of            *
# *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU      *
# *   Lesser General Public License for more details.                       *
# *                                                                         *
# *   You should have received a copy of the GNU Lesser General Public      *
# *   License along with FreeCAD. If not, see                               *
# *   <https://www.gnu.org/licenses/>.                                      *
# *                                                                         *
# ***************************************************************************

"""
This utility offers several commands to interact with the FreeCAD project on
crowdin. For it to work, you need a ~/.crowdin-freecad-token file in your
user's folder, that contains the API access token that gives access to the
crowdin FreeCAD project. The API token can also be specified in the
CROWDIN_TOKEN environment variable.

The CROWDIN_PROJECT_ID environment variable can be used to use this script
in other projects.

Usage:

    updatecrowdin.py <command> [<arguments>]

Available commands:

    gather:                       update the locale agnostic file with latest strings from
                                  source code and locales file from arguments entries
    overall-status:               displays the translation status for each locale on all
                                  workbenches available on Crowdin
    wb-status:                    displays the translation status for each locale only
                                  on the current workbench
    update-source:                updates on Crowdin the current version of .ts file
                                  found in the source code
    update-translation [locale]:  updates on Crowdin the current version of locale .ts files
                                  passed to the command
    build:                        builds a new downloadable package on Crowdin with all
                                  translated strings
    build-status:                 shows the status of the current builds available on
                                  Crowdin
    download [build_id]:          downloads build specified by 'build_id' or latest if
                                  build_id is left blank
    apply / install:              applies downloaded translations to source code
                                  (runs updatefromcrowdin.py)

Example:

    ./updatecrowdin.py update

Setting the project name adhoc:

    CROWDIN_PROJECT_ID=some_project ./updatecrowdin.py update
"""

# NOTE:
# This script is a remake of:
#   https://github.com/davesrocketshop/Rocket/blob/master/util/updatecrowdin.py
# which also is a remake of:
#   https://github.com/FreeCAD/FreeCAD/blob/main/src/Tools/updatecrowdin.py
#
# The biggest change is the implementation of `update-translation` flag.

# INFO: See Crowdin API documentation at: https://support.crowdin.com/developer/api/v2/

import concurrent.futures
import glob
import json
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
from collections import namedtuple
from functools import lru_cache
from urllib.parse import quote_plus
from urllib.request import Request, urlopen, urlretrieve

TsFile = namedtuple("TsFile", ["filename", "src_path"])
translation_source = [TsFile("FreeGrid.ts", "FreeGrid.ts")]

# NOTE: location tuple contains:
# - module name, must match files
# - relative path to translation folder
WBLocation = namedtuple("WBLocation", ["module_name", "translations_path"])
wb_location = WBLocation("FreeGrid", ".")

# fmt: off
# "file_suffix": "Crowdin-locale"
supported_locales = {
    "af": "af-ZA",    "ar": "ar-SA",      "eu": "eu-ES",    "be": "be-BY",
    "bg": "bg-BG",    "ca": "ca-ES",      "zh-CN": "zh-CN", "zh-TW": "zh-TW",
    "hr": "hr-HR",    "cs": "cs-CZ",      "da": "da-DK",    "nl": "nl-NL",
    "fil": "fil-PH",  "fi": "fi-FI",      "fr": "fr-FR",    "gl": "gl-ES",
    "ka": "ka-GE",    "de": "de-DE",      "el": "el-GR",    "hu": "hu-HU",
    "id": "id-ID",    "it": "it-IT",      "ja": "ja-JP",    "kab": "kab-KAB",
    "ko": "ko-KR",    "lt": "lt-LT",      "no": "no-NO",    "pl": "pl-PL",
    "pt-PT": "pt-PT", "pt-BR": "pt-BR",   "ro": "ro-RO",    "ru": "ru-RU",
    "sr": "sr-SP",    "sr-CS": "sr-CS",   "sk": "sk-SK",    "sl": "sl-SI",
    "es-ES": "es-ES", "es-AR": "es-AR",   "sv-SE": "sv-SE", "tr": "tr-TR",
    "uk": "uk-UA",    "val-ES": "val-ES", "vi": "vi-VN"  # "en": "en-US"
}
# fmt: on

NC = "\033[0m" if os.name == "posix" else ""  # no color
RED = "\033[;31m" if os.name == "posix" else ""
GREEN = "\033[;32m" if os.name == "posix" else ""
YELLOW = "\033[;33m" if os.name == "posix" else ""
BLUE = "\033[;34m" if os.name == "posix" else ""

THRESHOLD = 25  # 25 is used on main FreeCAD
DEBUG_URL = False


class CrowdinUpdater:
    """Client methods to interact with the Crowdin API."""

    BASE_URL = "https://api.crowdin.com/api/v2"

    def __init__(self, token: str, project_identifier: str, multithread: bool = True):
        """
        Initialize the Crowdin API client.

        :param token: The API token for authentication.
        :param project_identifier: The identifier of the Crowdin project.
        :param multithread: Whether to use multithreading.
        """
        self.token = token
        self.project_identifier = project_identifier
        self.multithread = multithread

    def _make_api_req(
        self, url: str, extra_headers: dict = {}, method: str = "GET", data=None
    ) -> dict:
        """
        Make an API request to the specified URL.

        :param url: The URL for the API request.
        :param extra_headers: Additional headers to include in the request.
        :param method: The HTTP method to use (default is GET).
        :param data: The data to send with the request (default is None).
        :return: The JSON response data.
        """
        headers = {"Authorization": f"Bearer {self.token}", **extra_headers}

        if isinstance(data, dict):
            headers["Content-Type"] = "application/json"
            data = json.dumps(data).encode("utf-8")

        request = Request(url, headers=headers, method=method, data=data)
        if DEBUG_URL:
            print(f"\n-> {url}\n")
        return json.loads(urlopen(request).read())["data"]

    def _make_project_api_req(self, project_path: str, *args, **kwargs) -> dict:
        """Make an API request to a project-specific endpoint."""
        url = f"{self.BASE_URL}/projects/{self._get_project_id()}{project_path}"
        return self._make_api_req(url=url, *args, **kwargs)

    @lru_cache()
    def _get_project_id(self) -> int:
        """Get the ID for the FreeCAD-addons project."""
        url = f"{self.BASE_URL}/projects/"
        response = self._make_api_req(url)

        for project in [p["data"] for p in response]:
            if project["identifier"] == project_identifier:
                return project["id"]

        raise Exception("No project identifier found!")

    def _get_source_files_info(self) -> dict:
        """Get the ID for all workbenches' translation source files."""
        files = self._make_project_api_req("/files?limit=250")
        return {f["data"]["path"].strip("/"): str(f["data"]["id"]) for f in files}

    def _target_language_ids(self):
        """Retrieve the valid language IDs."""
        response = self._make_project_api_req("")
        return response["targetLanguageIds"]

    def _add_storage(self, filename: str, fp):
        """Get a storage ID to upload a file."""
        response = self._make_api_req(
            f"{self.BASE_URL}/storages",
            data=fp,
            method="POST",
            extra_headers={
                "Crowdin-API-FileName": filename,
                "Content-Type": "application/octet-stream",
            },
        )
        return response["id"]

    def _update_source_file(self, ts_file: TsFile, files_info: dict):
        """Update source file on Crowdin platform."""
        filename = quote_plus(ts_file.filename)

        with open(ts_file.src_path, "rb") as fp:
            storage_id = self._add_storage(filename, fp)

        # only uploads the file if already exists
        if filename in files_info:
            file_id = files_info[filename]
            self._make_project_api_req(
                f"/files/{file_id}",
                method="PUT",
                data={
                    "storageId": storage_id,
                    "updateOption": "keep_translations_and_approvals",
                },
            )
            print(f"{filename} updated")
        else:
            self._make_project_api_req("/files", data={"storageId": storage_id, "name": filename})
            print(f"{filename} was not updated because is not on the list")

    def _upload_translation_file(self, locale: str):
        """Update translation file for the specified locale on Crowdin platform."""
        files_info = self._get_source_files_info()

        ts_file = TsFile(f"FreeGrid_{locale}.ts", f"FreeGrid_{locale}.ts")

        translation_filename = quote_plus(ts_file.filename)

        with open(ts_file.src_path, "rb") as fp:
            storage_id = self._add_storage(translation_filename, fp)

        src_filename = translation_source[0].filename

        if src_filename in files_info:
            file_id = int(files_info[src_filename])

            self._make_project_api_req(
                f"/translations/{locale}",
                method="POST",
                data={
                    "storageId": storage_id,
                    "fileId": file_id,
                    "importEqSuggestions": True,
                    "autoApproveImported": False,
                    "translateHidden": False,
                    "addToTm": False,
                },
            )
        else:
            print(f"{translation_filename} was not updated because is not on the list")

    def project_progress(self):
        """Check the translation progress for the whole Freecad-addons project."""
        response = self._make_project_api_req("/languages/progress?limit=100")
        return [item["data"] for item in response]

    def file_progress(self, filename: str):
        """Check the translation progress of a specific file."""
        files_info = self._get_source_files_info()

        if filename in files_info:
            file_id = int(files_info[filename])
            response = self._make_project_api_req(f"/files/{file_id}/languages/progress?limit=100")
            return [item["data"] for item in response]
        return None

    def download(self, build_id: str):
        """Download the translations archive with the specified build ID."""
        filename = f"{self.project_identifier}.zip"
        response = self._make_project_api_req(f"/translations/builds/{build_id}/download")
        urlretrieve(response["url"], filename)
        print("download of " + filename + " complete")

    def build(self):
        """Create a new translations archive with current translations."""
        self._make_project_api_req("/translations/builds", data={}, method="POST")

    def build_status(self):
        """Check completion progress of translations archive."""
        response = self._make_project_api_req("/translations/builds")
        return [item["data"] for item in response]

    def update_source(self, ts_files: list):
        """Prepare source files."""
        files_info = self._get_source_files_info()
        futures = []

        with concurrent.futures.ThreadPoolExecutor() as executor:
            for ts_file in ts_files:
                if self.multithread:
                    future = executor.submit(self._update_source_file, ts_file, files_info)
                    futures.append(future)
                else:
                    self._update_source_file(ts_file, files_info)

        # This blocks until all futures are complete and will also throw any exception
        for future in futures:
            future.result()

    def update_translation(self, locale: str):
        """Prepare translation file."""
        futures = []

        with concurrent.futures.ThreadPoolExecutor() as executor:
            if self.multithread:
                future = executor.submit(self._upload_translation_file, locale)
                futures.append(future)
            else:
                self._upload_translation_file(locale)

        # This blocks until all futures are complete and will also throw any exception
        for future in futures:
            future.result()


def print_response(response: dict):
    """Print pretty version of response dictionary."""
    print(json.dumps(response, indent=2))


def load_token() -> str | None:
    """Load API token stored in ~/.crowdin-freecad-token or ~/.crowdin-freecadaddons files."""
    for filename in [".crowdin-freecad-token", ".crowdin-freecadaddons"]:
        config_file = os.path.expanduser(f"~/{filename}")
        if os.path.exists(config_file):
            with open(config_file) as file:
                return file.read().strip()
    return None


def apply_translations():
    """Extract files from ZIP translation build and copy appropriate workbench TS files."""
    global tempfolder
    currentfolder = os.getcwd()
    tempfolder = tempfile.mkdtemp()
    print(f"Creating temp folder {tempfolder}")
    src = os.path.join(currentfolder, "freecad-addons.zip")
    dst = os.path.join(tempfolder, "freecad-addons.zip")
    if not os.path.exists(src):
        print(
            'freecad-addons.zip file not found! Aborting.\nRun "download" command before this one.'
        )
        sys.exit()
    shutil.copyfile(src, dst)
    os.chdir(tempfolder)
    zfile = zipfile.ZipFile("freecad-addons.zip")
    print("Extracting freecad-addons.zip...")
    zfile.extractall()
    os.chdir(currentfolder)
    if not os.path.exists(os.path.join(tempfolder, wb_location.module_name)):
        print(f"ERROR: Workbench path for {wb_location.module_name} not found!")
    else:
        print(f"Updating files for {GREEN}{wb_location.module_name}{NC}...")
        # Iterate over all locales
        for short_locale, full_locale in supported_locales.items():
            # Copy the translation files to the project directory
            oldname = wb_location.module_name + "_" + full_locale + ".ts"
            newname = wb_location.module_name + "_" + short_locale + ".ts"
            old_file = os.path.join(tempfolder, wb_location.module_name, oldname)
            new_file = os.path.join(wb_location.translations_path, newname)
            shutil.copyfile(old_file, new_file)
        print("Update of translations files has been completed.")


def update_locale(locale: str):
    """Update the TS agnostic file or the file specified by locale."""
    u = "_" if locale else ""
    # files from where strings will be picked up
    FILES = sorted(glob.glob("../../*.py") + glob.glob("../ui/*.ui"))
    filename = f"{wb_location.module_name}{u}{locale}.ts"
    action = "Creating" if not os.path.isfile(filename) else "Updating"
    print(f"{BLUE}\n<<< {action} '{filename}' file >>>{NC}")
    flags = ["-ts", filename, "-no-obsolete"]
    if u:
        flags = [
            "-source-language",
            "en_US",
            "-target-language",
            locale.replace("-", "_"),
        ] + flags

    # print("Executing: ", [LUPDATE] + FILES + flags)
    subprocess.run([LUPDATE] + FILES + flags)


def print_translation_progress(status: list):
    """Print a user friendly list with the translation progress."""
    status = sorted(status, key=lambda item: item["translationProgress"], reverse=True)
    print(
        len([item for item in status if item["translationProgress"] > THRESHOLD]),
        f"languages with status > {str(THRESHOLD)}%:\n",
    )
    sep = False
    for item in status:
        if item["translationProgress"] > 0:
            if (item["translationProgress"] < THRESHOLD) and (not sep):
                print("\nOther languages:\n")
                sep = True
            print(
                f"{GREEN}{item['languageId']}{NC} {str(item['translationProgress'])}% "
                f"({str(item['approvalProgress'])}% approved)"
            )


def print_translation_progress_md_table(status: list):
    """
    Print a Markdown table with the translation progress to use on 'translation/README.md' file.
    """
    status = sorted(status, key=lambda item: item["translationProgress"], reverse=True)

    print("\n\n| language | translated strings | completion |")
    print("|:---------|:------------------:|:----------:|")
    for item in status:
        if item["translationProgress"] > 0:
            print(f"| {item['languageId']:<8} | {item['phrases']['translated']:<18} | ", end="")
            print(f"{item['translationProgress']}%".ljust(11) + "|")


def add_files_above_threshold(status: list):
    """Add files above threshold to git staging area, other files are deleted."""
    status = sorted(status, key=lambda item: item["translationProgress"], reverse=True)
    for item in status:
        filename = f"{wb_location.module_name}_{item['languageId']}.ts"
        if item["translationProgress"] < THRESHOLD:
            if os.path.exists(filename):
                os.remove(filename)
        else:
            subprocess.run(["git", "add", filename])


def check_third_line():
    """Normalize locales on third line of TS files."""
    for file in glob.glob(f"{wb_location.module_name}_*.ts"):
        with open(file, "r") as f:
            lines = f.readlines()
        if len(lines) >= 3:
            lines[2] = lines[2].replace("-", "_").replace('"en"', '"en_US"')
        with open(file, "w") as f:
            f.writelines(lines)


def no_locale(locale: str):
    """Print error message when entered locale is not valid."""
    print(
        f"\nVerify your language code '{RED}{locale}{NC}'. Case sensitive.\n"
        "If it's correct, ask a maintainer to add support for your language on FreeCAD."
        "\nYour language should have a progress of at least 25% on FreeCAD project on Crowdin.\n"
        f"\nSupported locales, '{BLUE}FreeCADGui.supportedLocales(){NC}': {YELLOW}",
        " ".join(supported_locales.keys()),
        NC,
    )


if __name__ == "__main__":
    LUPDATE = os.environ.get("LUPDATE", "/usr/lib/qt6/bin/lupdate")
    LRELEASE = os.environ.get("LRELEASE", "/usr/lib/qt6/bin/lrelease")

    check_third_line()

    command = None

    args = sys.argv[1:]
    if args:
        command = args[0]

    token = os.environ.get("CROWDIN_TOKEN", load_token())
    if command and not token:
        print("Token not found")
        sys.exit()

    project_identifier = "freecad-addons"

    updater = CrowdinUpdater(token or "", project_identifier)

    if command == "overall-status":
        status = updater.project_progress()
        print(
            f"{BLUE}Translation progress for all workbenches available on "
            f"'Freecad-addons' project on Crowdin{NC}\n"
        )
        print_translation_progress(status)

    elif command == "wb-status":
        status = updater.file_progress(translation_source[0].filename)
        print(f"{BLUE}Translation progress for {wb_location.module_name} workbench{NC}\n")
        print_translation_progress(status or [])
        print_translation_progress_md_table(status or [])

    elif command == "build":
        updater.build()

    elif command == "build-status":
        for item in updater.build_status():
            print(f"  id: {item['id']} progress: {item['progress']}% status: {item['status']}")

    elif command == "download":
        if len(args) == 2:
            updater.download(args[1])
        else:
            stat = updater.build_status()
            if not stat:
                print("no builds found")
            elif len(stat) == 1:
                updater.download(stat[0]["id"])
            else:
                print("available builds:")
                for item in stat:
                    print(
                        f"  id: {item['id']} progress: {item['progress']}% status: {item['status']}"
                    )
                print("please specify a build id")

    elif command in ["apply", "install"]:
        # copy files above threshold
        apply_translations()
        check_third_line()
        # normalize indentation
        for locale in supported_locales:
            update_locale(locale)
        # add files to stage area
        status = updater.file_progress(translation_source[0].filename)
        add_files_above_threshold(status or [])
        # compile qm files
        for file in glob.glob(f"{wb_location.module_name}_*.ts"):
            subprocess.run([LRELEASE, "-nounfinished", file])

    elif command == "gather":
        # NOTE: you can pass several locales at once
        # $ ./update_crowdin.py gather el fr pl sv-SE
        update_locale("")  # update agnostic file
        if len(args[1:]) > 0:
            for locale in args[1:]:
                if locale in supported_locales:
                    update_locale(locale)  # update valid locales
                else:
                    no_locale(locale)

    elif command == "update-source":
        # NOTE: Execute after "gather" command
        print("ts file being uploaded to Crowdin:", translation_source)
        updater.update_source(translation_source)

    elif command == "update-translation":
        # NOTE: you can pass several locales at once
        # $ ./update_crowdin.py update-translation de es-ES ja pt-BR
        for locale in args[1:]:
            # locales = sorted(updater._target_language_ids())
            if locale in supported_locales:
                updater.update_translation(locale)
            else:
                no_locale(locale)

    else:
        print(__doc__)
