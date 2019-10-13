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

""" Chemistry Section Properties View """

import tkinter as tk
from tkinter import messagebox
from qiskit_aqua_interfaces.user_interface import SectionPropertiesView, TextPopup


class ChemSectionPropertiesView(SectionPropertiesView):
    """ Chemistry Section Properties View """
    def populate(self, properties):
        self.clear()
        for property_name, value_tuple in properties.items():
            value = '' if value_tuple[0] is None else str(value_tuple[0])
            value = value.replace('\r', '\\r').replace('\n', '\\n')
            if value_tuple[1]:
                self._tree.insert('', tk.END, text=property_name, values=[], tags="SUBSTITUTIONS")
            else:
                self._tree.insert('', tk.END, text=property_name, values=[value])

        self._tree.tag_configure('SUBSTITUTIONS', foreground='gray')
        self._properties = properties

    def _cb_tree_edit(self, event):
        rowid = self._tree.identify_row(event.y)
        if not rowid:
            return

        column = self._tree.identify_column(event.x)
        if column == '#1':
            x, y, width, height = self._tree.bbox(rowid, column)
            pady = height // 2

            item = self._tree.identify("item", event.x, event.y)
            property_name = self._tree.item(item, "text")
            value_tuple = self._properties[property_name]
            if not value_tuple[1]:
                try:
                    self._popup_widget = self._controller.create_popup(self.section_name,
                                                                       property_name,
                                                                       self._tree,
                                                                       value_tuple[0])
                except Exception as ex:  # pylint: disable=broad-except
                    messagebox.showerror("Error", str(ex))
                    return

                if isinstance(self._popup_widget, TextPopup):
                    height = self._tree.winfo_height() - y
                    self._popup_widget.place(x=x, y=y, width=width, height=height)
                else:
                    self._popup_widget.place(x=x, y=y + pady, anchor=tk.W, width=width)
