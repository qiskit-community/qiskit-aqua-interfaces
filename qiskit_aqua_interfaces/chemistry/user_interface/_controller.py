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

"""Qiskit Chemistry user interface controller."""

from tkinter import messagebox
import logging
from qiskit_aqua_interfaces.user_interface import BaseController
from ._model import Model

logger = logging.getLogger(__name__)

# pylint: disable=import-outside-toplevel


class Controller(BaseController):
    """ Chemistry Controller """
    def __init__(self, guiprovider) -> None:
        super().__init__(guiprovider, Model())

    def open_file(self, filename):
        ret = super().open_file(filename)
        if ret and not self.model.get_section_names():
            self.outputview.write_line('The file appears not to be a qiskit chemistry input file; '
                                       'no begin/end sections found.')

        return ret

    def cb_section_select(self, section_name):
        self._sections_view.show_remove_button(True)
        self._sections_view_title.set(section_name)
        if self.model.section_is_text(section_name):
            self._text_view.populate(self.model.get_section_text(section_name))
            self._text_view.section_name = section_name
            self._text_view.show_add_button(False)
            self._text_view.show_remove_button(False)
            self._text_view.show_defaults_button(
                not self.model.default_properties_equals_properties(section_name))
            self._text_view.tkraise()
        else:
            self._properties_view.show_add_button(self.shows_add_button(section_name))
            self._properties_view.populate(
                self.model.get_section_properties_with_substitution(section_name))
            self._properties_view.section_name = section_name
            self._properties_view.show_remove_button(False)
            self._properties_view.show_defaults_button(
                not self.model.default_properties_equals_properties(section_name))
            self._properties_view.tkraise()

    def cb_section_defaults(self, section_name):
        from qiskit.chemistry.parser import InputParser
        try:
            self.model.set_default_properties_for_name(section_name)
            if section_name == InputParser.DRIVER:
                section_names = self.model.get_section_names()
                self._sections_view.populate(section_names)
                missing = self.get_sections_names_missing()
                self._sections_view.show_add_button(bool(missing))

            self.cb_section_select(section_name)
            return True
        except Exception as ex:  # pylint: disable=broad-except
            messagebox.showerror("Error", str(ex))

        return False

    def cb_property_set(self, section_name, property_name, value):
        from qiskit.aqua.parser import JSONSchema
        try:
            self.model.set_section_property(section_name, property_name, value)
        except Exception as ex:  # pylint: disable=broad-except
            messagebox.showerror("Error", str(ex))
            return False

        try:
            self._properties_view.populate(
                self.model.get_section_properties_with_substitution(section_name))
            self._properties_view.show_add_button(self.shows_add_button(section_name))
            _show_remove = property_name not in (JSONSchema.PROVIDER, JSONSchema.NAME) \
                if section_name == JSONSchema.BACKEND else property_name != JSONSchema.NAME
            self._properties_view.show_remove_button(
                _show_remove and self._properties_view.has_selection())
            self._properties_view.show_defaults_button(
                not self.model.default_properties_equals_properties(section_name))
            section_names = self.model.get_section_names()
            self._sections_view.populate(section_names, section_name)
            missing = self.get_sections_names_missing()
            self._sections_view.show_add_button(bool(missing))
            return True
        except Exception as ex:  # pylint: disable=broad-except
            messagebox.showerror("Error", str(ex))

        return False

    def cb_section_property_remove(self, section_name, property_name):
        try:
            self.model.delete_section_property(section_name, property_name)
            self._properties_view.populate(
                self.model.get_section_properties_with_substitution(section_name))
            self._properties_view.show_add_button(self.shows_add_button(section_name))
            self._properties_view.show_remove_button(False)
            self._properties_view.show_defaults_button(
                not self.model.default_properties_equals_properties(section_name))
        except Exception as ex:  # pylint: disable=broad-except
            self.outputview.write_line(str(ex))

    def get_combobox_parameters(self, section_name, property_name):
        from qiskit.aqua.parser import JSONSchema
        from qiskit.chemistry.parser import InputParser
        from qiskit.chemistry.drivers import local_drivers
        values = None
        types = ['string']
        combobox_state = 'readonly'
        if InputParser.OPERATOR == section_name and JSONSchema.NAME == property_name:
            values = self.model.get_operator_section_names()
        elif InputParser.DRIVER == section_name and JSONSchema.NAME == property_name:
            values = local_drivers()
        else:
            combobox_state, types, values = \
                super().get_combobox_parameters(section_name, property_name)

        return combobox_state, types, values
