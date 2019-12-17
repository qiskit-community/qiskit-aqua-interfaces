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

"""Qiskit User Interface base model"""

from abc import ABC, abstractmethod
import json
from collections import OrderedDict
import copy
import threading
import logging

logger = logging.getLogger(__name__)

# pylint: disable=import-outside-toplevel


class BaseModel(ABC):
    """Base GUI Model."""

    def __init__(self) -> None:
        """Create Model object."""
        self._parser = None
        self._custom_providers = {}
        self._available_providers = {}
        self._backendsthread = None
        self.get_available_providers()

    @property
    def providers(self):
        """ get providers """
        providers = copy.deepcopy(self._custom_providers)
        providers.update(self._available_providers)
        return providers

    def get_available_providers(self):
        """ get available providers """
        from qiskit.aqua import register_ibmq_and_get_known_providers
        if self._backendsthread is not None:
            return

        self._reg_method = register_ibmq_and_get_known_providers
        self._backendsthread = threading.Thread(target=self._get_available_providers,
                                                name='Available providers')
        self._backendsthread.daemon = True
        self._backendsthread.start()

    def _get_available_providers(self):
        try:
            self._available_providers = OrderedDict([x for x in
                                                     self._reg_method().items() if len(x[1]) > 0])
        except Exception as ex:  # pylint: disable=broad-except
            logger.debug(str(ex))
        finally:
            self._backendsthread = None

    def is_empty(self):
        """ check if no data """
        return self._parser is None or len(self._parser.get_section_names()) == 0

    def new_model(self, parser_class, template_file, populate_defaults):
        """ create new model """
        try:
            json_dict = {}
            jsonfile = template_file
            with open(jsonfile) as json_file:
                json_dict = json.load(json_file)

            self._parser = parser_class(json_dict)
            self._parser.parse()
            if populate_defaults:
                self._parser.validate_merge_defaults()
                self._parser.commit_changes()

            return self._parser.get_section_names()
        except Exception:
            self._parser = None
            raise

    def load_model(self, filename, parser_class, populate_defaults):
        """ load a model """
        from qiskit.aqua.parser import JSONSchema
        from qiskit.aqua import get_provider_from_backend, get_backends_from_provider
        if filename is None:
            return []
        try:
            self._parser = parser_class(filename)
            self._parser.parse()
            # check if there was any data, if there is no data, just return empty file
            if not self.get_section_names():
                return []

            # before merging defaults attempts to find a provider for the backend
            provider = self._parser.get_section_property(JSONSchema.BACKEND, JSONSchema.PROVIDER)
            if provider is None:
                backend_name = \
                    self._parser.get_section_property(JSONSchema.BACKEND, JSONSchema.NAME)
                if backend_name is not None:
                    self._parser.set_section_property(JSONSchema.BACKEND, JSONSchema.PROVIDER,
                                                      get_provider_from_backend(backend_name))
            else:
                try:
                    if provider not in self.providers:
                        self._custom_providers[provider] = get_backends_from_provider(provider)
                except Exception as ex:  # pylint: disable=broad-except
                    logger.debug(str(ex))
        except Exception:
            self._parser = None
            raise

        try:
            if populate_defaults:
                self._parser.validate_merge_defaults()

            return self.get_section_names()
        finally:
            self._parser.commit_changes()

    def get_filename(self):
        """ get filename """
        if self._parser is None:
            return None

        return self._parser.get_filename()

    def is_modified(self):
        """ check if data was modified """
        if self._parser is None:
            return False

        return self._parser.is_modified()

    def save_to_file(self, filename):
        """ save to another file """
        if self.is_empty():
            raise Exception("Empty input data.")

        self._parser.save_to_file(filename)

    def get_section_names(self):
        """ get section names """
        if self._parser is None:
            return []

        return self._parser.get_section_names()

    def get_property_default_values(self, section_name, property_name):
        """ get property default values """
        if self._parser is None:
            return None

        return self._parser.get_property_default_values(section_name, property_name)

    def section_is_text(self, section_name):
        """ check if section is text """
        if self._parser is None:
            return False

        return self._parser.section_is_text(section_name)

    def get_section(self, section_name):
        """ get section """
        return self._parser.get_section(section_name) if self._parser is not None else None

    def get_section_text(self, section_name):
        """ get section text """
        if self._parser is None:
            return ''

        return self._parser.get_section_text(section_name)

    def get_section_properties(self, section_name):
        """ get section properties """
        if self._parser is None:
            return {}

        return self._parser.get_section_properties(section_name)

    @abstractmethod
    def default_properties_equals_properties(self, section_name):
        """ check if default properties are same as current  properties """
        pass

    def get_section_property(self, section_name, property_name):
        """ get section property """
        if self._parser is None:
            return None

        return self._parser.get_section_property(section_name, property_name)

    def set_section(self, section_name):
        """ set section """
        if self._parser is None:
            raise Exception('Input not initialized.')

        value = self._parser.get_section_default_properties(section_name)
        if isinstance(value, dict):
            from qiskit.aqua.parser import JSONSchema
            # if there is no pluggable default name, use the first one found
            if value.get(JSONSchema.NAME, '') == '' and \
               BaseModel.is_pluggable_section(section_name):
                from qiskit.aqua import local_pluggables
                pluggable_names = local_pluggables(section_name)
                if pluggable_names:
                    value[JSONSchema.NAME] = pluggable_names[0]

            for property_name, property_value in value.items():
                self._parser.set_section_property(section_name, property_name, property_value)

            # do one more time in case schema was updated
            value = self._parser.get_section_default_properties(section_name)
            for property_name, property_value in value.items():
                self._parser.set_section_property(section_name, property_name, property_value)
        else:
            if value is None:
                types = self._parser.get_section_types(section_name)
                if 'null' not in types:
                    if 'string' in types:
                        value = ''
                    elif 'object' in types:
                        value = {}
                    elif 'array' in types:
                        value = []

            self._parser.set_section_data(section_name, value)

    def set_default_properties_for_name(self, section_name):
        """ set default properties for name key """
        from qiskit.aqua.parser import JSONSchema
        from qiskit.aqua import get_backends_from_provider
        if self._parser is None:
            raise Exception('Input not initialized.')

        # First get the properties that will remain
        provider_name = None
        name = self._parser.get_section_property(section_name, JSONSchema.NAME)
        if JSONSchema.BACKEND == section_name:
            provider_name = self._parser.get_section_property(section_name, JSONSchema.PROVIDER)
            if provider_name is not None:
                backend_names = get_backends_from_provider(provider_name)
                if name not in backend_names:
                    # use first backend available in provider
                    name = backend_names[0] if backend_names else None

        # now delete all current properties
        self._parser.delete_section_properties(section_name)

        # set first the properties that remained
        if provider_name is not None:
            self._parser.set_section_property(section_name, JSONSchema.PROVIDER, provider_name)
        if name is not None:
            self._parser.set_section_property(section_name, JSONSchema.NAME, name)

        # now fetch all default properties from updated schema
        value = self._parser.get_section_default_properties(section_name)

        if isinstance(value, dict):
            if JSONSchema.NAME in value:
                # remove name from defaults to be updated, since it should remain intact
                del value[JSONSchema.NAME]

            if JSONSchema.BACKEND == section_name and JSONSchema.PROVIDER in value:
                # remove provider name from defaults to be updated, since it should remain intact
                del value[JSONSchema.PROVIDER]

            # add all default properties
            for property_name, property_value in value.items():
                self._parser.set_section_property(section_name, property_name, property_value)
        else:
            if value is None:
                types = self._parser.get_section_types(section_name)
                if 'null' not in types:
                    if 'string' in types:
                        value = ''
                    elif 'object' in types:
                        value = {}
                    elif 'array' in types:
                        value = []

            self._parser.set_section_data(section_name, value)

    @staticmethod
    def is_pluggable_section(section_name):
        """ check if section is a pluggable """
        from qiskit.aqua.parser import BaseParser
        return BaseParser.is_pluggable_section(section_name)

    def get_pluggable_section_names(self, section_name):
        """ get all pluggable section names """
        from qiskit.aqua.parser import BaseParser
        from qiskit.aqua import PluggableType, local_pluggables
        from qiskit.aqua.parser import JSONSchema
        if not BaseModel.is_pluggable_section(section_name):
            return []

        if PluggableType.ALGORITHM.value == section_name:
            problem_name = None
            if self._parser is not None:
                problem_name = self.get_section_property(JSONSchema.PROBLEM, JSONSchema.NAME)
            if problem_name is None:
                problem_name = self.get_property_default_value(JSONSchema.PROBLEM, JSONSchema.NAME)

            if problem_name is None:
                return local_pluggables(PluggableType.ALGORITHM)

            algo_names = []
            for algo_name in local_pluggables(PluggableType.ALGORITHM):
                problems = BaseParser.get_algorithm_problems(algo_name)
                if problem_name in problems:
                    algo_names.append(algo_name)

            return algo_names

        return local_pluggables(section_name)

    def delete_section(self, section_name):
        """ delete a section """
        if self._parser is None:
            raise Exception('Input not initialized.')

        self._parser.delete_section(section_name)

    def get_default_sections(self):
        """ get default sections """
        if self._parser is None:
            raise Exception('Input not initialized.')

        return self._parser.get_default_sections()

    def get_section_default_properties(self, section_name):
        """ get default section properties """
        if self._parser is None:
            raise Exception('Input not initialized.')

        return self._parser.get_section_default_properties(section_name)

    def allows_additional_properties(self, section_name):
        """ check if section allows new properties """
        if self._parser is None:
            raise Exception('Input not initialized.')

        return self._parser.allows_additional_properties(section_name)

    def get_property_default_value(self, section_name, property_name):
        """ get section property default values """
        if self._parser is None:
            raise Exception('Input not initialized.')

        return self._parser.get_property_default_value(section_name, property_name)

    def get_property_types(self, section_name, property_name):
        """ get section property types """
        if self._parser is None:
            raise Exception('Input not initialized.')

        return self._parser.get_property_types(section_name, property_name)

    def set_section_property(self, section_name, property_name, value):
        """ set section property """
        from qiskit.aqua.parser import BaseParser
        from qiskit.aqua.parser import JSONSchema
        from qiskit.aqua import get_backends_from_provider
        if self._parser is None:
            raise Exception('Input not initialized.')

        self._parser.set_section_property(section_name, property_name, value)
        value = self._parser.get_section_property(section_name, property_name)

        # set default properties
        if (section_name == JSONSchema.BACKEND and property_name in
                [JSONSchema.PROVIDER, JSONSchema.NAME]) or \
           (property_name == JSONSchema.NAME and BaseParser.is_pluggable_section(section_name)):
            properties = self._parser.get_section_default_properties(section_name)
            if isinstance(properties, dict):
                if section_name == JSONSchema.BACKEND:
                    properties[JSONSchema.PROVIDER] = \
                        self._parser.get_section_property(section_name, JSONSchema.PROVIDER)
                    properties[JSONSchema.NAME] = \
                        self._parser.get_section_property(section_name, JSONSchema.NAME)

                # move name to top
                if JSONSchema.NAME in properties:
                    properties.move_to_end(JSONSchema.NAME, last=False)

                # move provider to top
                if JSONSchema.PROVIDER in properties:
                    properties.move_to_end(JSONSchema.PROVIDER, last=False)

                properties[property_name] = value
                self._parser.delete_section_properties(section_name)
                for prop_name, prop_value in properties.items():
                    self._parser.set_section_property(section_name, prop_name, prop_value)

        if section_name == JSONSchema.BACKEND and property_name == JSONSchema.PROVIDER:
            # refresh backends for this provider
            backends = get_backends_from_provider(value)
            if value not in self.providers:
                self._custom_providers[value] = backends

    def delete_section_property(self, section_name, property_name):
        """ delete section property """
        from qiskit.aqua.parser import BaseParser
        from qiskit.aqua.parser import JSONSchema
        if self._parser is None:
            raise Exception('Input not initialized.')

        self._parser.delete_section_property(section_name, property_name)
        if property_name == JSONSchema.NAME and BaseParser.is_pluggable_section(section_name):
            self._parser.delete_section_properties(section_name)
        elif section_name == JSONSchema.BACKEND and \
                property_name in (JSONSchema.PROVIDER, JSONSchema.NAME):
            self._parser.delete_section_properties(section_name)

    def set_section_text(self, section_name, value):
        """ set section text """
        if self._parser is None:
            raise Exception('Input not initialized.')

        self._parser.set_section_data(section_name, value)
