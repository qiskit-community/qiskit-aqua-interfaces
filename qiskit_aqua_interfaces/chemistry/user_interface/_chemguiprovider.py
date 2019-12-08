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

"""Chemistry User Interface Provider"""

import tkinter as tk
import tkinter.ttk as ttk
import tkinter.filedialog as tkfd
from tkinter import messagebox
import os
import json
import pprint
from qiskit_aqua_interfaces.user_interface import GUIProvider
from ._uipreferences import UIPreferences
from ._chemsectionpropertiesview import ChemSectionPropertiesView
from ._chemthread import ChemistryThread
from ._controller import Controller

# pylint: disable=import-outside-toplevel


class ChemistryGUIProvider(GUIProvider):
    """Chemistry GUIProvider"""

    def __init__(self) -> None:
        super().__init__()
        self._save_algo_json = None
        self._controller = None

    @property
    def save_algo_json(self):
        """ get save algorithm json flag """
        if self._save_algo_json is None:
            self._save_algo_json = tk.IntVar()
            self._save_algo_json.set(0)

        return self._save_algo_json

    @property
    def title(self):
        """Return provider title."""
        return 'Qiskit Chemistry'

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
        from qiskit.chemistry._logging import get_logging_level as chem_get_logging_level
        return chem_get_logging_level()

    def set_logging_config(self, logging_config):
        """Update logger configurations using a SDK default one."""
        from qiskit.chemistry._logging import set_logging_config as chem_set_logging_config
        chem_set_logging_config(logging_config)

    def build_logging_config(self, level):
        """Creates a the configuration dict of the named loggers"""
        from qiskit.chemistry._logging import build_logging_config as chem_build_logging_config
        return chem_build_logging_config(level)

    def create_section_properties_view(self, parent):
        """Creates provider section properties view"""
        return ChemSectionPropertiesView(self.controller, parent)

    def add_toolbar_items(self, toolbar):
        """Add items to toolbar"""
        checkbutton = ttk.Checkbutton(toolbar,
                                      text="Generate Algorithm Input",
                                      variable=self.save_algo_json)
        checkbutton.pack(side=tk.LEFT)

    def add_file_menu_items(self, file_menu):
        """Add items to file menu"""
        dict_menu = tk.Menu(file_menu, tearoff=False)
        file_menu.add_cascade(label="Export Dictionary", menu=dict_menu)
        dict_menu.add_command(label='Clipboard', command=self._export_dictionary_to_clipboard)
        dict_menu.add_command(label='File...', command=self._export_dictionary_to_file)

    def create_run_thread(self, model, outputview, thread_queue):
        """Creates run thread"""
        filename = None
        if self.save_algo_json.get() != 0:
            preferences = self.create_uipreferences()
            filename = tkfd.asksaveasfilename(parent=self.controller.view,
                                              title='Algorithm Input',
                                              initialdir=preferences.get_savefile_initialdir())
            if not filename:
                return None

            preferences.set_savefile_initialdir(os.path.dirname(filename))
            preferences.save()

        return ChemistryThread(model, outputview, thread_queue, filename)

    def _export_dictionary_to_clipboard(self):
        if self.controller.is_empty():
            self.controller.outputview.write_line("No data to export.")
            return

        try:
            value = json.loads(json.dumps(self.controller.model.get_dictionary()))
            value = pprint.pformat(value, indent=4)
            self.controller.view.clipboard_clear()
            self.controller.view.clipboard_append(value)
            self.controller.outputview.write_line("Exported to clibpoard.")
        except Exception as ex:  # pylint: disable=broad-except
            messagebox.showerror("Error", str(ex))

    def _export_dictionary_to_file(self):
        if self.controller.is_empty():
            self.controller.outputview.write_line("No data to export.")
            return

        preferences = self.create_uipreferences()
        filename = tkfd.asksaveasfilename(parent=self.controller.view,
                                          title='Export Chemistry Input',
                                          initialdir=preferences.get_savefile_initialdir())
        if filename:
            try:
                self.controller.model.export_dictionary(filename)
                self.controller.outputview.write_line("Exported to file: {}".format(filename))
                preferences.set_savefile_initialdir(os.path.dirname(filename))
                preferences.save()
            except Exception as ex:  # pylint: disable=broad-except
                messagebox.showerror("Error", str(ex))
