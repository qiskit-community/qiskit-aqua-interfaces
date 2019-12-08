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

"""Qiskit Aqua browser user interface model."""

from collections import OrderedDict
import copy

# pylint: disable=import-outside-toplevel


class Model:
    """ Aqua Browser Model """
    def __init__(self) -> None:
        """Create Model object."""
        self._data_loaded = False
        self._schema_property_titles = None
        self._sections = None

    def _load_data(self):
        if self._data_loaded:
            return

        from qiskit.aqua import (local_pluggables_types,
                                 local_pluggables,
                                 get_pluggable_configuration)

        self._schema_property_titles = OrderedDict()
        self._sections = OrderedDict()
        for pluggable_type in sorted(local_pluggables_types(), key=lambda x: x.value):
            self._sections[pluggable_type.value] = OrderedDict()
            self._schema_property_titles[pluggable_type.value] = OrderedDict()
            for pluggable_name in sorted(local_pluggables(pluggable_type)):
                config = copy.deepcopy(get_pluggable_configuration(pluggable_type, pluggable_name))
                self._populate_section(pluggable_type.value, pluggable_name, config)

        self._data_loaded = True

    def _populate_section(self, pluggable_type, pluggable_name, configuration):
        self._sections[pluggable_type][pluggable_name] = OrderedDict()
        self._sections[pluggable_type][pluggable_name]['description'] = pluggable_name
        self._sections[pluggable_type][pluggable_name]['properties'] = OrderedDict()
        self._sections[pluggable_type][pluggable_name]['problems'] = []
        self._sections[pluggable_type][pluggable_name]['depends'] = OrderedDict()
        self._schema_property_titles[pluggable_type][pluggable_name] = OrderedDict()
        for config_name, config_value in configuration.items():
            if config_name == 'description':
                self._sections[pluggable_type][pluggable_name]['description'] = str(config_value)
                continue

            if config_name == 'problems' and isinstance(config_value, list):
                self._sections[pluggable_type][pluggable_name]['problems'] = config_value
                continue

            if config_name == 'depends' and isinstance(config_value, list):
                self._sections[pluggable_type][pluggable_name]['depends'] = config_value
                continue

            if config_name == 'input_schema' and isinstance(config_value, dict):
                schema = config_value
                if 'properties' in schema:
                    for prop, values in schema['properties'].items():
                        if 'items' in values:
                            if 'type' in values['items']:
                                values['items'] = values['items']['type']
                        if 'oneOf' in values:
                            values['oneOf'] = values['oneOf'][0]
                            if 'enum' in values['oneOf']:
                                values['oneOf'] = values['oneOf']['enum']

                            values['one of'] = values['oneOf']
                            del values['oneOf']

                        self._sections[pluggable_type][pluggable_name]['properties'][prop] = values
                        for k, _ in values.items():
                            self._schema_property_titles[pluggable_type][pluggable_name][k] = None
                continue

        self._schema_property_titles[pluggable_type][pluggable_name] = \
            list(self._schema_property_titles[pluggable_type][pluggable_name].keys())

    def pluggable_names(self):
        """ get all pluggable names """
        self._load_data()
        return list(self._sections.keys())

    def get_pluggable_description(self, pluggable_type, pluggable_name):
        """ get pluggable description """
        self._load_data()
        return self._sections[pluggable_type][pluggable_name]['description']

    def get_pluggable_problems(self, pluggable_type, pluggable_name):
        """ get pluggable problems """
        self._load_data()
        return self._sections[pluggable_type][pluggable_name]['problems']

    def get_pluggable_dependency(self, pluggable_type, pluggable_name, dependency_type):
        """ get pluggable dependency """
        self._load_data()
        depends = self._sections[pluggable_type][pluggable_name]['depends']
        for dependency in depends:
            if dependency.get('pluggable_type') == dependency_type:
                return dependency

        return {}

    def get_pluggable_schema_property_titles(self, pluggable_type, pluggable_name):
        """ get pluggable schema property titles """
        self._load_data()
        return self._schema_property_titles[pluggable_type][pluggable_name]

    def get_sections(self):
        """ get sections """
        self._load_data()
        return self._sections

    def get_pluggable_schema_properties(self, pluggable_type, pluggable_name):
        """ get pluggable schema properties """
        self._load_data()
        return self._sections[pluggable_type][pluggable_name]['properties']
