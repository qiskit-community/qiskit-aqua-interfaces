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

"""Section Properties view"""

import tkinter as tk
import tkinter.ttk as ttk
from ._scrollbarview import ScrollbarView


class SectionPropertiesView(ScrollbarView):
    """ Aqua Browser Section Properties View """
    def __init__(self, controller, parent, **options) -> None:
        super(SectionPropertiesView, self).__init__(parent, **options)
        self._controller = controller
        self._tree = None

    def clear(self):
        """ clear sections """
        if self._tree is not None:
            for i in self._tree.get_children():
                self._tree.delete([i])

    def populate(self, column_titles, properties):
        """ populate sections """
        self.clear()
        ttk.Style().configure("BrowseSectionPropertiesView.Treeview.Heading",
                              font=(None, 12, 'bold'))
        self._tree = ttk.Treeview(self, style='BrowseSectionPropertiesView.Treeview',
                                  selectmode=tk.BROWSE, columns=column_titles)
        self._tree.heading('#0', text='property')
        self.init_widgets(self._tree)
        for value in column_titles:
            self._tree.heading(value, text=value)

        self._controller._properties_view.grid(row=0, column=0, sticky='nsew')

        for name, props in properties.items():
            values = [''] * len(column_titles)
            for k, v in props.items():
                index = column_titles.index(k)
                if isinstance(v, list) and not v:
                    v = str(v)
                values[index] = ','.join(str(t) for t in v) if isinstance(v, list) else str(v)

            self._tree.insert('', tk.END, text=name, values=values)
