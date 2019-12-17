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

"""Scrollbar view"""

import tkinter as tk
import tkinter.ttk as ttk


class ScrollbarView(ttk.Frame):
    """ Aqua Browser Scrollbar View """
    def __init__(self, parent, **options) -> None:
        super(ScrollbarView, self).__init__(parent, **options)
        self._child = None
        self._hscrollbar = None
        self._vscrollbar = None

    def init_widgets(self, child):
        """ initialize widget """
        if self._child is not None:
            self._child.destroy()

        if self._hscrollbar is not None:
            self._hscrollbar.destroy()
            self._hscrollbar = None

        if self._vscrollbar is not None:
            self._vscrollbar.destroy()
            self._vscrollbar = None

        self._child = child
        self._hscrollbar = ttk.Scrollbar(self, orient=tk.HORIZONTAL)
        self._vscrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL)
        self._child.config(yscrollcommand=self._vscrollbar.set)
        self._child.config(xscrollcommand=self._hscrollbar.set)
        self._vscrollbar.config(command=self._child.yview)
        self._hscrollbar.config(command=self._child.xview)

    def pack(self, **options):
        """ pack layout """
        if self._hscrollbar is not None:
            self._hscrollbar.pack(side=tk.BOTTOM, fill=tk.X, expand=tk.FALSE)

        if self._vscrollbar is not None:
            self._vscrollbar.pack(side=tk.RIGHT, fill=tk.Y, expand=tk.FALSE)

        if self._child is not None:
            self._child.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.TRUE)

        ttk.Frame.pack(self, **options)

    def grid(self, **options):
        """ grid layout """
        if self._hscrollbar is not None:
            self._hscrollbar.pack(side=tk.BOTTOM, fill=tk.X, expand=tk.FALSE)

        if self._vscrollbar is not None:
            self._vscrollbar.pack(side=tk.RIGHT, fill=tk.Y, expand=tk.FALSE)

        if self._child is not None:
            self._child.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.TRUE)

        ttk.Frame.grid(self, **options)
