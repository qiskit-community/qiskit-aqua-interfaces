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
from ._toolbarview import ToolbarView
from ._customwidgets import SectionComboDialog


class SectionsView(ToolbarView):

    def __init__(self, controller, parent, **options):
        super(SectionsView, self).__init__(parent, **options)
        self._controller = controller
        ttk.Style().configure("SectionsView.Treeview.Heading", font=(None, 12, 'bold'))
        self._tree = ttk.Treeview(self, style='SectionsView.Treeview', selectmode=tk.BROWSE)
        self._tree.heading('#0', text='Section')
        self._tree.bind('<<TreeviewSelect>>', self._on_tree_select)
        self.init_widgets(self._tree)

    def clear(self):
        for i in self._tree.get_children():
            self._tree.delete([i])

    def populate(self, section_names, section_select=None):
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
        return self._tree.selection()

    def _on_tree_select(self, event):
        for item in self._tree.selection():
            item_text = self._tree.item(item, 'text')
            self._controller.on_section_select(item_text)
            return

    def onadd(self):
        sections = self._controller.get_sections_names_missing()
        dialog = SectionComboDialog(self._controller, self.master)
        dialog.do_init(sections=sections)
        dialog.do_modal()
        if dialog.result is None:
            return

        if dialog.result is not None and len(dialog.result) > 0:
            if self._controller.on_section_add(dialog.result):
                self.populate(self._controller.model.get_section_names(), dialog.result)

    def onremove(self):
        for item in self._tree.selection():
            item_text = self._tree.item(item, 'text')
            if self._controller.on_section_remove(item_text):
                self._tree.delete([item])
                self.show_remove_button(self.has_selection())
            break
