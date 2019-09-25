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

"""Section Text view"""

import tkinter as tk
from ._toolbarview import ToolbarView
from ._customwidgets import TextCustom

_LINESEP = '\n'


class SectionTextView(ToolbarView):
    """ Section Text View """
    def __init__(self, controller, parent, **options) -> None:
        super(SectionTextView, self).__init__(parent, **options)
        self._controller = controller
        self._text_widget = TextCustom(self, wrap=tk.NONE, state=tk.NORMAL)
        self.init_widgets(self._text_widget)
        self.bind("<Unmap>", self._cb_update_value)
        self.bind("<FocusOut>", self._cb_update_value)
        self._section_name = None
        self._text = None

    @property
    def section_name(self):
        """ get section name """
        return self._section_name

    @section_name.setter
    def section_name(self, new_section_name):
        """ set section name """
        self._section_name = new_section_name

    def populate(self, text):
        """ populate text """
        self._text_widget.delete(1.0, tk.END)
        if text is not None:
            self._text_widget.insert(tk.END, text)

        self._text = text

    def clear(self):
        """ clear text """
        self._text_widget.delete(1.0, tk.END)
        self._text = self._text_widget.get(1.0, tk.END)

    def _cb_update_value(self, *ignore):
        sep_pos = -len(_LINESEP)
        new_text = self._text_widget.get(1.0, tk.END)
        if len(new_text) >= len(_LINESEP) and new_text[sep_pos:] == _LINESEP:
            new_text = new_text[:sep_pos]

        if self._text != new_text:
            self._text = new_text
            self._controller.cb_text_set(self._section_name, new_text)

    def cb_defaults(self):
        self._controller.cb_section_defaults(self.section_name)
