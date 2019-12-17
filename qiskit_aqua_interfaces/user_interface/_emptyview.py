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

"""Empty view"""

import tkinter as tk
import tkinter.ttk as ttk


class EmptyView(ttk.Frame):
    """ Empty View """
    def __init__(self, parent, **options) -> None:
        super(EmptyView, self).__init__(parent, **options)
        self._child = tk.Frame(self, background='white')
        self._toolbar = ttk.Frame(self)

    def grid(self, **options):
        """ grid layout """
        self._toolbar.pack(side=tk.BOTTOM, fill=tk.X)
        self._child.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.TRUE)
        ttk.Frame.grid(self, **options)

    def set_toolbar_size(self, size):
        """ set toolbar size """
        self._toolbar.configure(width=size[0], height=size[1])
