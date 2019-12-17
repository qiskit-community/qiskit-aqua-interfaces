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

"""Qiskit Aqua user interface model."""

import os
import logging
from qiskit_aqua_interfaces.aqua.user_interface._uipreferences import UIPreferences
from qiskit_aqua_interfaces.user_interface import BaseModel

logger = logging.getLogger(__name__)

# pylint: disable=import-outside-toplevel


class Model(BaseModel):
    """ Aqua Model """
    def new(self):
        """ Create new model """
        from qiskit.aqua.parser._inputparser import InputParser
        uipreferences = UIPreferences()
        return super().new_model(InputParser,
                                 os.path.join(os.path.dirname(__file__), 'input_template.json'),
                                 uipreferences.get_populate_defaults(True))

    def load_file(self, filename):
        """ load input file """
        from qiskit.aqua.parser._inputparser import InputParser
        uipreferences = UIPreferences()
        return super().load_model(filename, InputParser, uipreferences.get_populate_defaults(True))

    def default_properties_equals_properties(self, section_name):
        from qiskit.aqua.parser import JSONSchema
        if self.section_is_text(section_name):
            return self.get_section_default_properties(section_name) == \
                    self.get_section_text(section_name)

        default_properties = self.get_section_default_properties(section_name)
        properties = self.get_section_properties(section_name)
        if not isinstance(default_properties, dict) or not isinstance(properties, dict):
            return default_properties == properties

        if JSONSchema.BACKEND == section_name and JSONSchema.PROVIDER in properties:
            default_properties[JSONSchema.PROVIDER] = properties[JSONSchema.PROVIDER]

        if JSONSchema.NAME in properties:
            default_properties[JSONSchema.NAME] = properties[JSONSchema.NAME]

        return dict(default_properties) == dict(properties)

    def get_input_section_names(self):
        """ get input section valid names """
        from qiskit.aqua.parser._inputparser import InputParser
        from qiskit.aqua import local_pluggables, PluggableType
        from qiskit.aqua.parser import JSONSchema
        problem_name = None
        if self._parser is not None:
            problem_name = self.get_section_property(JSONSchema.PROBLEM, JSONSchema.NAME)
        if problem_name is None:
            problem_name = self.get_property_default_value(JSONSchema.PROBLEM, JSONSchema.NAME)

        if problem_name is None:
            return local_pluggables(PluggableType.INPUT)

        input_names = []
        for input_name in local_pluggables(PluggableType.INPUT):
            problems = InputParser.get_input_problems(input_name)
            if problem_name in problems:
                input_names.append(input_name)

        return input_names
