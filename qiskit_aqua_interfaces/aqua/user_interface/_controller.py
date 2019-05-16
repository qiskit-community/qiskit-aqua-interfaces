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

from .base_controller import BaseController
from ._model import Model
from tkinter import messagebox
import logging

logger = logging.getLogger(__name__)


class Controller(BaseController):

    def __init__(self, guiprovider):
        super().__init__(guiprovider, Model())

    def open_file(self, filename):
        ret = super().open_file(filename)
        if ret and len(self.model.get_section_names()) == 0:
            self.outputview.write_line('The file appears not to be a qiskit aqua input file; no sections found.')

        return ret

    def on_section_select(self, section_name):
        self._sectionsView.show_remove_button(True)
        self._sectionView_title.set(section_name)
        if self.model.section_is_text(section_name):
            self._textView.populate(self.model.get_section_text(section_name))
            self._textView.section_name = section_name
            self._textView.show_add_button(False)
            self._textView.show_remove_button(False)
            self._textView.show_defaults_button(not self.model.default_properties_equals_properties(section_name))
            self._textView.tkraise()
        else:
            self._propertiesView.show_add_button(self.shows_add_button(section_name))
            self._propertiesView.populate(self.model.get_section_properties(section_name))
            self._propertiesView.section_name = section_name
            self._propertiesView.show_remove_button(False)
            self._propertiesView.show_defaults_button(not self.model.default_properties_equals_properties(section_name))
            self._propertiesView.tkraise()

    def on_section_defaults(self, section_name):
        try:
            self.model.set_default_properties_for_name(section_name)
            self.on_section_select(section_name)
            return True
        except Exception as e:
            messagebox.showerror("Error", str(e))

        return False

    def on_property_set(self, section_name, property_name, value):
        from qiskit.aqua.parser import JSONSchema
        try:
            self.model.set_section_property(section_name, property_name, value)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return False

        try:
            self._propertiesView.populate(self.model.get_section_properties(section_name))
            self._propertiesView.show_add_button(self.shows_add_button(section_name))
            _show_remove = property_name != JSONSchema.PROVIDER and property_name != JSONSchema.NAME \
                if section_name == JSONSchema.BACKEND else property_name != JSONSchema.NAME
            self._propertiesView.show_remove_button(_show_remove and self._propertiesView.has_selection())
            self._propertiesView.show_defaults_button(not self.model.default_properties_equals_properties(section_name))
            section_names = self.model.get_section_names()
            self._sectionsView.populate(section_names, section_name)
            missing = self.get_sections_names_missing()
            self._sectionsView.show_add_button(True if missing else False)
            return True
        except Exception as e:
            messagebox.showerror("Error", str(e))

        return False

    def on_section_property_remove(self, section_name, property_name):
        try:
            self.model.delete_section_property(section_name, property_name)
            self._propertiesView.populate(self.model.get_section_properties(section_name))
            self._propertiesView.show_add_button(self.shows_add_button(section_name))
            self._propertiesView.show_remove_button(False)
            self._propertiesView.show_defaults_button(not self.model.default_properties_equals_properties(section_name))
        except Exception as e:
            self.outputview.write_line(str(e))

    def get_combobox_parameters(self, section_name, property_name):
        from qiskit.aqua import PluggableType
        from qiskit.aqua.parser import JSONSchema
        values = None
        types = ['string']
        combobox_state = 'readonly'
        if PluggableType.INPUT.value == section_name and JSONSchema.NAME == property_name:
            values = self.model.get_input_section_names()
        else:
            combobox_state, types, values = super().get_combobox_parameters(section_name, property_name)

        return combobox_state, types, values
