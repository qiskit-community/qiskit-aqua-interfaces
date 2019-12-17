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

"""Preferences Dialog"""

import tkinter as tk
import tkinter.ttk as ttk
from collections import OrderedDict
import logging
from ._dialog import Dialog
from ._credentialsview import CredentialsView

# pylint: disable=import-outside-toplevel


class PreferencesDialog(Dialog):
    """ Preferences Dialog """
    log_levels = OrderedDict(
        [(logging.CRITICAL, logging.getLevelName(logging.CRITICAL)),
         (logging.ERROR, logging.getLevelName(logging.ERROR)),
         (logging.WARNING, logging.getLevelName(logging.WARNING)),
         (logging.INFO, logging.getLevelName(logging.INFO)),
         (logging.DEBUG, logging.getLevelName(logging.DEBUG)),
         (logging.NOTSET, logging.getLevelName(logging.NOTSET))]
    )

    def __init__(self, parent, guiprovider) -> None:
        super(PreferencesDialog, self).__init__(guiprovider.controller, parent, 'Preferences')
        self._guiprovider = guiprovider
        self._credentialsview = None
        self._level_combo = None
        self._check_button = None
        self._populate_defaults = tk.IntVar()

    def body(self, parent, options):
        preferences = self._guiprovider.create_uipreferences()
        logging_config = preferences.get_logging_config()
        if logging_config is not None:
            self._guiprovider.set_logging_config(logging_config)

        populate = preferences.get_populate_defaults(True)
        self._populate_defaults.set(1 if populate else 0)

        current_row = 0
        from qiskit.aqua.utils import has_ibmq
        if has_ibmq():
            credentials_group = ttk.LabelFrame(parent,
                                               text='IBMQ Credentials',
                                               padding=(6, 6, 6, 6),
                                               borderwidth=4,
                                               relief=tk.GROOVE)
            credentials_group.grid(padx=(7, 7), pady=6, row=current_row,
                                   column=0, sticky='nsew')
            self._credentialsview = CredentialsView(credentials_group)
            current_row += 1

        defaults_group = ttk.LabelFrame(parent,
                                        text='Defaults',
                                        padding=(6, 6, 6, 6),
                                        borderwidth=4,
                                        relief=tk.GROOVE)
        defaults_group.grid(padx=(7, 7), pady=6, row=current_row, column=0, sticky='nsw')
        defaults_group.columnconfigure(1, pad=7)
        current_row += 1

        self._check_button = ttk.Checkbutton(defaults_group,
                                             text="Populate on file new/open",
                                             variable=self._populate_defaults)
        self._check_button.grid(row=0, column=1, sticky='nsw')

        logging_group = ttk.LabelFrame(parent,
                                       text='Logging Configuration',
                                       padding=(6, 6, 6, 6),
                                       borderwidth=4,
                                       relief=tk.GROOVE)
        logging_group.grid(padx=(7, 7), pady=6, row=current_row, column=0, sticky='nsw')
        logging_group.columnconfigure(1, pad=7)
        current_row += 1

        loglevel = self._guiprovider.get_logging_level()

        ttk.Label(logging_group,
                  text="Level:",
                  borderwidth=0,
                  anchor=tk.E).grid(row=0, column=0, sticky='nsew')
        self._level_combo = ttk.Combobox(logging_group,
                                         exportselection=0,
                                         state='readonly',
                                         values=list(PreferencesDialog.log_levels.values()))
        index = list(PreferencesDialog.log_levels.keys()).index(loglevel)
        self._level_combo.current(index)
        self._level_combo.grid(row=0, column=1, sticky='nsw')

        self.entry = \
            self._credentialsview.initial_focus if self._credentialsview else self._check_button
        return self.entry  # initial focus

    def validate(self):
        if self._credentialsview:
            if not self._credentialsview.validate():
                self.initial_focus = self._credentialsview.initial_focus
                return False

            self.initial_focus = self._credentialsview.initial_focus

        return True

    def apply(self):
        try:
            level_name = self._level_combo.get()
            levels = \
                [key for key, value in PreferencesDialog.log_levels.items() if value == level_name]
            loglevel = levels[0]

            logging_config = self._guiprovider.build_logging_config(loglevel)
            populate = self._populate_defaults.get()
            preferences = self._guiprovider.create_uipreferences()
            preferences.set_logging_config(logging_config)
            preferences.set_populate_defaults(populate != 0)
            preferences.save()

            self._guiprovider.set_logging_config(logging_config)

            if self._credentialsview:
                from qiskit.aqua import Preferences
                preferences = Preferences()
                self._credentialsview.apply(preferences)
                preferences.save()

            self._controller.model.get_available_providers()
        except Exception as ex:  # pylint: disable=broad-except
            self.controller.outputview.write_line(str(ex))

    def do_cancel(self):
        if self._credentialsview:
            self._credentialsview.do_cancel()
