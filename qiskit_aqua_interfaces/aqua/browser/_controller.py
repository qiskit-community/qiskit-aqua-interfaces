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

"""Qiskit Aqua browser controller."""

import tkinter as tk
import logging
from ._model import Model

logger = logging.getLogger(__name__)


class Controller:
    """ Aqua Browser Controller """
    _NAME = 'name'

    def __init__(self, view) -> None:
        self._view = view
        self._model = None
        self._filemenu = None
        self._sections_view = None
        self._empty_view = None
        self._sections_view_title = tk.StringVar()
        self._properties_view = None

    @property
    def model(self):
        """ return model """
        if self._model is None:
            self._model = Model()

        return self._model

    def pluggable_names(self):
        """ get pluggable names """
        return self.model.pluggable_names()

    def populate_sections(self):
        """ populate sections """
        self._sections_view.populate(self.model.get_sections())

    def pluggable_type_select(self, pluggable_type):
        """ select pluggable type """
        del pluggable_type
        self._sections_view_title.set('')
        self._empty_view.tkraise()

    def pluggable_schema_select(self, pluggable_type, pluggable_name):
        """ select pluggable schema """
        self._sections_view_title.set(
            self.model.get_pluggable_description(pluggable_type, pluggable_name))
        properties = self.model.get_pluggable_schema_properties(pluggable_type, pluggable_name)
        column_titles = \
            self.model.get_pluggable_schema_property_titles(pluggable_type, pluggable_name)
        self._properties_view.populate(column_titles, properties)
        self._properties_view.tkraise()

    def pluggable_problems_select(self, pluggable_type, pluggable_name):
        """ select pluggable problems """
        problems = \
            self.model.get_pluggable_problems(pluggable_type, pluggable_name)
        self._properties_view.populate(['oneOf'], {'name': {'oneOf': problems}})
        self._properties_view.tkraise()

    def pluggable_depends_select(self, pluggable_type, pluggable_name):
        """ select pluggable depends """
        self._sections_view_title.set(
            self.model.get_pluggable_description(pluggable_type, pluggable_name))
        self._empty_view.tkraise()

    def pluggable_dependency_select(self, pluggable_type, pluggable_name, dependency_type):
        """ select pluggable dependency """
        dependency = \
            self.model.get_pluggable_dependency(pluggable_type, pluggable_name, dependency_type)
        default = dependency.get('default', {})
        self._properties_view.populate(list(default.keys()), {'default': default})
        self._properties_view.tkraise()
