# -*- coding: utf-8 -*-

# This code is part of Qiskit.
#
# (C) Copyright IBM 2018, 2019.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

"""Qiskit Chemistry user interface preferences."""

import os
import json
from typing import Optional, List, Dict


class UIPreferences:
    """ Chemistry UI Preferences """
    _FILENAME = '.qiskit_chemistry_ui'
    _VERSION = '1.0'

    def __init__(self) -> None:
        """Create UIPreferences object."""
        self._preferences = {
            'version': UIPreferences._VERSION
        }
        home = os.path.expanduser("~")
        self._filepath = os.path.join(home, UIPreferences._FILENAME)
        try:
            with open(self._filepath) as json_pref:
                self._preferences = json.load(json_pref)
        except Exception:  # pylint: disable=broad-except
            pass

    @property
    def filepath(self) -> str:
        """ get filepath """
        return self._filepath

    def save(self) -> None:
        """ save preferences """
        with open(self._filepath, 'w') as pref_output:
            json.dump(self._preferences, pref_output, sort_keys=True, indent=4)

    def get_version(self) -> str:
        """ get version """
        if 'version' in self._preferences:
            return self._preferences['version']

        return None

    def get_geometry(self, default_value: Optional[str] = None) -> str:
        """ get chemistry geometry """
        if 'geometry' in self._preferences:
            return self._preferences['geometry']

        return default_value

    def set_geometry(self, geometry: str) -> None:
        """ set chemistry geometry """
        self._preferences['geometry'] = geometry

    def get_openfile_initialdir(self) -> str:
        """ get open file initial folder """
        if 'openfile_initialdir' in self._preferences:
            if not os.path.isdir(self._preferences['openfile_initialdir']):
                self._preferences['openfile_initialdir'] = os.getcwd()

            return self._preferences['openfile_initialdir']

        return os.getcwd()

    def set_openfile_initialdir(self, initialdir: str) -> None:
        """ set open file initial folder """
        self._preferences['openfile_initialdir'] = initialdir

    def get_savefile_initialdir(self) -> str:
        """ get save file initial folder """
        if 'savefile_initialdir' in self._preferences:
            if not os.path.isdir(self._preferences['savefile_initialdir']):
                self._preferences['savefile_initialdir'] = os.getcwd()

            return self._preferences['savefile_initialdir']

        return os.getcwd()

    def set_savefile_initialdir(self, initialdir: str) -> None:
        """ set save file initial folder """
        self._preferences['savefile_initialdir'] = initialdir

    def get_populate_defaults(self, default_value: Optional[bool] = None) -> bool:
        """ get populate defaults flag """
        if 'populate_defaults' in self._preferences:
            return self._preferences['populate_defaults']

        return default_value

    def set_populate_defaults(self, populate_defaults: bool) -> None:
        """ set populate defaults flag """
        self._preferences['populate_defaults'] = populate_defaults

    def get_recent_files(self) -> List[str]:
        """ get recent files list """
        files = []
        if 'recent_files' in self._preferences:
            for file in self._preferences['recent_files']:
                if os.path.isfile(file):
                    files.append(file)

            self._preferences['recent_files'] = files

        return files

    def add_recent_file(self, file: str) -> None:
        """ add a recent file """
        recent_files = self.get_recent_files()
        if file not in recent_files:
            recent_files.append(file)
            if len(recent_files) > 6:
                recent_files = recent_files[1:]
        self._preferences['recent_files'] = recent_files

    def clear_recent_files(self) -> None:
        """ clear recent files list """
        if 'recent_files' in self._preferences:
            del self._preferences['recent_files']

    def get_logging_config(self,
                           default_value: Optional[Dict[str, object]] = None) -> Dict[str, object]:
        """ get chemistry logging """
        if 'logging_config' in self._preferences:
            return self._preferences['logging_config']

        return default_value

    def set_logging_config(self, logging_config: Dict[str, object]) -> None:
        """ set chemistry logging """
        self._preferences['logging_config'] = logging_config
