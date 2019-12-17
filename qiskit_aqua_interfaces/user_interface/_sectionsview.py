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

"""Qiskit user interface sections view."""

import tkinter as tk
import tkinter.ttk as ttk
from ._toolbarview import ToolbarView
from ._customwidgets import SectionComboDialog


class SectionsView(ToolbarView):
    """Sections toolbar view."""

    def __init__(self, controller, parent, **options) -> None:
        super(SectionsView, self).__init__(parent, **options)
        self._controller = controller
        ttk.Style().configure("SectionsView.Treeview.Heading", font=(None, 12, 'bold'))
        self._tree = ttk.Treeview(self, style='SectionsView.Treeview', selectmode=tk.BROWSE)
        self._tree.heading('#0', text='Section')
        self._tree.bind('<<TreeviewSelect>>', self._cb_tree_select)
        self.init_widgets(self._tree)

    def clear(self):
        """Remove all entries from view.

        Returns:
            None
        """
        for i in self._tree.get_children():
            self._tree.delete([i])

    def populate(self, section_names, section_select=None):
        """Populates all entries from view.

        Args:
            section_names (list[str]): list of names.
            section_select (str): name of selected entry

        Returns:
            None
        """
        self.clear()
        item = None
        for name in section_names:
            i = self._tree.insert('', tk.END, text=name)
            if name == section_select:
                item = i

        if item is not None:
            self._tree.see(item)
            self._tree.selection_set(item)

    def has_selection(self):
        """Checks if an entry is selected.

        Returns:
            bool: True if the entry is selected, else False.
        """
        return self._tree.selection()

    def _cb_tree_select(self, event):
        for item in self._tree.selection():
            item_text = self._tree.item(item, 'text')
            self._controller.cb_section_select(item_text)
            return

    def cb_add(self):
        sections = self._controller.get_sections_names_missing()
        dialog = SectionComboDialog(self._controller, self.master)
        dialog.do_init(sections=sections)
        dialog.do_modal()
        if dialog.result is None:
            return

        if dialog.result:
            if self._controller.cb_section_add(dialog.result):
                self.populate(self._controller.model.get_section_names(), dialog.result)

    def cb_remove(self):
        for item in self._tree.selection():
            item_text = self._tree.item(item, 'text')
            if self._controller.cb_section_remove(item_text):
                self.populate(self._controller.model.get_section_names())
                self.show_remove_button(self.has_selection())
            break
