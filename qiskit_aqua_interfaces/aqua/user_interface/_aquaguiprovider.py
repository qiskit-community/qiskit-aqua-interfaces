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

"""Aqua User Interface Provider"""

from qiskit_aqua_interfaces.user_interface import GUIProvider, SectionPropertiesView
from ._uipreferences import UIPreferences
from ._aquathread import AquaThread
from ._controller import Controller

# pylint: disable=import-outside-toplevel


class AquaGUIProvider(GUIProvider):
    """Aqua GUIProvider"""

    def __init__(self) -> None:
        super().__init__()
        self._controller = None

    @property
    def title(self):
        """Return provider title."""
        return 'Qiskit Aqua'

    @property
    def help_hyperlink(self):
        """Return provider help hyperlink."""
        return 'https://qiskit.org/'

    @property
    def controller(self):
        """Return provider controller."""
        if self._controller is None:
            self._controller = Controller(self)

        return self._controller

    def create_uipreferences(self):
        """Creates provider UI preferences."""
        return UIPreferences()

    def get_logging_level(self):
        """get level for the named logger."""
        from qiskit.aqua._logging import get_logging_level as aqua_get_logging_level
        return aqua_get_logging_level()

    def set_logging_config(self, logging_config):
        """Update logger configurations using a SDK default one."""
        from qiskit.aqua._logging import set_logging_config as aqua_set_logging_config
        aqua_set_logging_config(logging_config)

    def build_logging_config(self, level):
        """Creates a the configuration dict of the named loggers"""
        from qiskit.aqua._logging import build_logging_config as aqua_build_logging_config
        return aqua_build_logging_config(level)

    def create_section_properties_view(self, parent):
        """Creates provider section properties view"""
        return SectionPropertiesView(self.controller, parent)

    def add_toolbar_items(self, toolbar):
        """Add items to toolbar"""
        pass

    def add_file_menu_items(self, file_menu):
        """Add items to file menu"""
        pass

    def create_run_thread(self, model, outputview, thread_queue):
        """Creates run thread"""
        return AquaThread(model, outputview, thread_queue)
