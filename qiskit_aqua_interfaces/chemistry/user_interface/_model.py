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

"""Qiskit Chemistry user interface model."""

import os
from collections import OrderedDict
import logging
from qiskit_aqua_interfaces.user_interface import BaseModel
from ._uipreferences import UIPreferences

logger = logging.getLogger(__name__)

# pylint: disable=import-outside-toplevel


class Model(BaseModel):
    """ Chemistry Model """
    def new(self):
        """ new model """
        from qiskit.chemistry.parser import InputParser
        uipreferences = UIPreferences()
        return super().new_model(InputParser,
                                 os.path.join(os.path.dirname(__file__), 'input_template.json'),
                                 uipreferences.get_populate_defaults(True))

    def load_file(self, filename):
        """ load input data """
        from qiskit.chemistry.parser import InputParser
        uipreferences = UIPreferences()
        return super().load_model(filename, InputParser, uipreferences.get_populate_defaults(True))

    def default_properties_equals_properties(self, section_name):
        """ check if default properties are the same as current properties """
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

        if len(default_properties) != len(properties):
            return False

        substitution_tuples = self._parser.check_if_substitution_key(
            section_name, list(properties.keys()))
        for substitution_tuple in substitution_tuples:
            property_name = substitution_tuple[0]
            if property_name not in default_properties:
                return False

            if not substitution_tuple[1]:
                if default_properties[property_name] != properties[property_name]:
                    return False

        return True

    def get_dictionary(self):
        """ get data dictionary """
        if self.is_empty():
            raise Exception("Empty input data.")

        return self._parser.to_dictionary()

    def export_dictionary(self, filename):
        """ export data dictionary """
        if self.is_empty():
            raise Exception("Empty input data.")

        self._parser.export_dictionary(filename)

    def get_section_properties_with_substitution(self, section_name):
        """ get section properties after updating values """
        properties = self.get_section_properties(section_name)
        result_tuples = \
            self._parser.check_if_substitution_key(section_name, list(properties.keys()))
        properties_with_substitution = OrderedDict()
        for result_tuple in result_tuples:
            properties_with_substitution[result_tuple[0]] = \
                    (properties[result_tuple[0]], result_tuple[1])

        return properties_with_substitution

    def get_operator_section_names(self):
        """ get operator section names """
        from qiskit.aqua.parser import JSONSchema
        from qiskit.chemistry.parser import InputParser
        from qiskit.chemistry.core import local_chemistry_operators
        problem_name = None
        if self._parser is not None:
            problem_name = self.get_section_property(JSONSchema.PROBLEM, JSONSchema.NAME)
        if problem_name is None:
            problem_name = self.get_property_default_value(JSONSchema.PROBLEM, JSONSchema.NAME)

        if problem_name is None:
            return local_chemistry_operators()

        operator_names = []
        for operator_name in local_chemistry_operators():
            problems = InputParser.get_operator_problems(operator_name)
            if problem_name in problems:
                operator_names.append(operator_name)

        return operator_names
