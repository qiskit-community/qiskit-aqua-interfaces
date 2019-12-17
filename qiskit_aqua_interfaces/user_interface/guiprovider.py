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

"""User Interface Provider"""

from abc import ABC, abstractmethod


class GUIProvider(ABC):
    """Base class for GUIProviders."""

    START, STOP = 'Start', 'Stop'

    @abstractmethod
    def __init__(self) -> None:
        pass

    @property
    @abstractmethod
    def title(self):
        """Return provider title."""
        pass

    @property
    @abstractmethod
    def help_hyperlink(self):
        """Return provider help hyperlink."""
        pass

    @property
    @abstractmethod
    def controller(self):
        """Return provider controller."""
        pass

    @abstractmethod
    def create_uipreferences(self):
        """Creates provider UI preferences."""
        pass

    @abstractmethod
    def get_logging_level(self):
        """get level for the named logger."""
        pass

    @abstractmethod
    def set_logging_config(self, logging_config):
        """Update logger configurations using a SDK default one."""
        pass

    @abstractmethod
    def build_logging_config(self, level):
        """Creates a the configuration dict of the named loggers"""
        pass

    @abstractmethod
    def create_section_properties_view(self, parent):
        """Creates provider section properties view"""
        pass

    @abstractmethod
    def add_toolbar_items(self, toolbar):
        """Add items to toolbar"""
        pass

    @abstractmethod
    def add_file_menu_items(self, file_menu):
        """Add items to file menu"""
        pass

    @abstractmethod
    def create_run_thread(self, model, outputview, thread_queue):
        """Creates run thread"""
        pass
