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

import tkinter as tk
import tkinter.ttk as ttk
from ._dialog import Dialog
from collections import OrderedDict
from ._credentialsview import CredentialsView
import logging


class PreferencesDialog(Dialog):

    _LOG_LEVELS = OrderedDict(
        [(logging.CRITICAL, logging.getLevelName(logging.CRITICAL)),
         (logging.ERROR, logging.getLevelName(logging.ERROR)),
         (logging.WARNING, logging.getLevelName(logging.WARNING)),
         (logging.INFO, logging.getLevelName(logging.INFO)),
         (logging.DEBUG, logging.getLevelName(logging.DEBUG)),
         (logging.NOTSET, logging.getLevelName(logging.NOTSET))]
    )

    def __init__(self, parent, guiprovider):
        super(PreferencesDialog, self).__init__(guiprovider.controller, parent, 'Preferences')
        self._guiprovider = guiprovider
        self._credentialsview = None
        self._levelCombo = None
        self._checkButton = None
        self._populateDefaults = tk.IntVar()

    def body(self, parent, options):
        preferences = self._guiprovider.create_uipreferences()
        logging_config = preferences.get_logging_config()
        if logging_config is not None:
            self._guiprovider.set_logging_config(logging_config)

        populate = preferences.get_populate_defaults(True)
        self._populateDefaults.set(1 if populate else 0)

        current_row = 0
        from qiskit.aqua.utils import has_ibmq
        if has_ibmq():
            credentialsGroup = ttk.LabelFrame(parent,
                                              text='IBMQ Credentials',
                                              padding=(6, 6, 6, 6),
                                              borderwidth=4,
                                              relief=tk.GROOVE)
            credentialsGroup.grid(padx=(7, 7), pady=6, row=current_row,
                                  column=0, sticky='nsew')
            self._credentialsview = CredentialsView(credentialsGroup)
            current_row += 1

        defaultsGroup = ttk.LabelFrame(parent,
                                       text='Defaults',
                                       padding=(6, 6, 6, 6),
                                       borderwidth=4,
                                       relief=tk.GROOVE)
        defaultsGroup.grid(padx=(7, 7), pady=6, row=current_row, column=0, sticky='nsw')
        defaultsGroup.columnconfigure(1, pad=7)
        current_row += 1

        self._checkButton = ttk.Checkbutton(defaultsGroup,
                                            text="Populate on file new/open",
                                            variable=self._populateDefaults)
        self._checkButton.grid(row=0, column=1, sticky='nsw')

        loggingGroup = ttk.LabelFrame(parent,
                                      text='Logging Configuration',
                                      padding=(6, 6, 6, 6),
                                      borderwidth=4,
                                      relief=tk.GROOVE)
        loggingGroup.grid(padx=(7, 7), pady=6, row=current_row, column=0, sticky='nsw')
        loggingGroup.columnconfigure(1, pad=7)
        current_row += 1

        loglevel = self._guiprovider.get_logging_level()

        ttk.Label(loggingGroup,
                  text="Level:",
                  borderwidth=0,
                  anchor=tk.E).grid(row=0, column=0, sticky='nsew')
        self._levelCombo = ttk.Combobox(loggingGroup,
                                        exportselection=0,
                                        state='readonly',
                                        values=list(PreferencesDialog._LOG_LEVELS.values()))
        index = list(PreferencesDialog._LOG_LEVELS.keys()).index(loglevel)
        self._levelCombo.current(index)
        self._levelCombo.grid(row=0, column=1, sticky='nsw')

        self.entry = self._credentialsview.initial_focus if self._credentialsview else self._checkButton
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
            level_name = self._levelCombo.get()
            levels = [key for key, value in PreferencesDialog._LOG_LEVELS.items() if value == level_name]
            loglevel = levels[0]

            logging_config = self._guiprovider.build_logging_config(loglevel)
            populate = self._populateDefaults.get()
            preferences = self._guiprovider.create_uipreferences()
            preferences.set_logging_config(logging_config)
            preferences.set_populate_defaults(False if populate == 0 else True)
            preferences.save()

            self._guiprovider.set_logging_config(logging_config)

            if self._credentialsview:
                from qiskit.aqua import Preferences
                from qiskit.aqua import disable_ibmq_account
                preferences = Preferences()
                disable_ibmq_account(preferences.get_url(), preferences.get_token(), preferences.get_proxies({}))
                self._credentialsview.apply(preferences)
                preferences.save()

            self._controller.model.get_available_providers()
        except Exception as e:
            self.controller.outputview.write_line(str(e))
