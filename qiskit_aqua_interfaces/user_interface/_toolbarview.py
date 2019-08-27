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

"""Toolbar View"""

import tkinter as tk
import tkinter.ttk as ttk
from ._scrollbarview import ScrollbarView


class ToolbarView(ScrollbarView):
    """ Toolbar View """
    def __init__(self, parent, **options) -> None:
        super(ToolbarView, self).__init__(parent, **options)
        self._child = None
        self._toolbar = None
        self._add_button = None
        self._remove_button = None
        self._defaults_button = None
        self._hscrollbar = None
        self._vscrollbar = None
        self._add_button_shown = False
        self._remove_button_shown = False
        self._defaults_button_shown = False
        self._make_toolbar()

    def _make_toolbar(self):
        self._toolbar = ttk.Frame(self)
        self._add_button = ttk.Button(self._toolbar,
                                      text='Add',
                                      state='enable',
                                      command=self.cb_add)
        self._remove_button = ttk.Button(self._toolbar,
                                         text='Remove',
                                         state='enable',
                                         command=self.cb_remove)
        self._defaults_button = ttk.Button(self._toolbar,
                                           text='Defaults',
                                           state='enable',
                                           command=self.cb_defaults)

    def cb_add(self):
        """ add callback """
        pass

    def cb_remove(self):
        """ remove callback """
        pass

    def cb_defaults(self):
        """ defaults callback """
        pass

    def get_toolbar_size(self):
        """ get size """
        if self._toolbar is None:
            return (0, 0)

        return (self._toolbar.winfo_width(), self._toolbar.winfo_height())

    def pack(self, **options):
        """ pack layout """
        if self._toolbar is not None:
            self._toolbar.pack(side=tk.BOTTOM, fill=tk.X)
            self._add_button.pack(side=tk.LEFT)
            self._remove_button.pack(side=tk.LEFT)
            self._defaults_button.pack(side=tk.RIGHT)

        ScrollbarView.pack(self, **options)

    def grid(self, **options):
        """ grid layout """
        if self._toolbar is not None:
            self._toolbar.pack(side=tk.BOTTOM, fill=tk.X)
            self._add_button.pack(side=tk.LEFT)
            self._remove_button.pack(side=tk.LEFT)
            self._defaults_button.pack(side=tk.RIGHT)

        ScrollbarView.grid(self, **options)

    def show_add_button(self, show):
        """ show/hide add button """
        self._add_button_shown = show
        if show:
            if self._remove_button_shown:
                self._remove_button.pack_forget()
            self._add_button.pack(side=tk.LEFT)
            if self._remove_button_shown:
                self._remove_button.pack(side=tk.LEFT)
        else:
            self._add_button.pack_forget()

    def show_remove_button(self, show):
        """ show/hide remove button """
        self._remove_button_shown = show
        if show:
            self._remove_button.pack(side=tk.LEFT)
        else:
            self._remove_button.pack_forget()

    def show_defaults_button(self, show):
        """ show/hide defaults button """
        self._defaults_button_shown = show
        if show:
            self._defaults_button.pack(side=tk.RIGHT)
        else:
            self._defaults_button.pack_forget()
