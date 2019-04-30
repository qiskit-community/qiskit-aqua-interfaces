# -*- coding: utf-8 -*-

# This code is part of Qiskit.
#
# (C) Copyright IBM 2019.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

"""
InputParser test.
"""

import unittest
from test.common import QiskitAquaUisTestCase
from qiskit_aqua_interfaces.aqua.user_interface._model import Model
from qiskit.aqua import AquaError


class TestAquaModel(QiskitAquaUisTestCase):
    """Aqua UI Model tests."""

    def setUp(self):
        super().setUp()
        _filepath = self._get_resource_path('resources/vqe.json')
        self._model = Model()
        self._model.load_file(_filepath)

    def test_new(self):
        section_names = self._model.new()
        for name in ['algorithm', 'backend']:
            self.assertIn(name, section_names)

    def test_open(self):
        section_names = self._model.get_section_names()
        for name in ['algorithm', 'backend', 'initial_state', 'input', 'optimizer', 'problem', 'variational_form']:
            self.assertIn(name, section_names)

    def test_get_input_section_names(self):
        section_names = self._model.get_input_section_names()
        self.assertEqual(section_names, ['EnergyInput'])

    def test_get_property_default_values(self):
        modes = self._model.get_property_default_values('algorithm', 'operator_mode')
        self.assertEqual(modes, ['matrix', 'paulis', 'grouped_paulis'])

    def test_section_is_text(self):
        ret = self._model.section_is_text('problem')
        self.assertFalse(ret)

    def test_get_section(self):
        section = self._model.get_section('initial_state')
        self.assertEqual(section, {'name': 'ZERO'})

    def test_get_section_text(self):
        text = self._model.get_section_text('algorithm')
        self.assertIsInstance(text, str)

    def test_get_section_properties(self):
        expected = {
            'depth': 3,
            'entanglement': "linear",
            'entangler_map': None,
            'name': "RYRZ"
        }
        properties = self._model.get_section_properties('variational_form')
        subset = {k: v for k, v in properties.items() if k in expected}
        self.assertDictEqual(subset, expected)

    def test_default_properties_equals_properties(self):
        ret = self._model.default_properties_equals_properties('optimizer')
        self.assertTrue(ret)

    def test_get_section_property(self):
        prop = self._model.get_section_property('algorithm', 'name')
        self.assertEqual(prop, 'VQE')

    def test_set_section(self):
        self._model.set_section('oracle')
        section_names = self._model.get_section_names()
        self.assertIn('oracle', section_names)

    def test_get_pluggable_section_names(self):
        section_names = self._model.get_pluggable_section_names('initial_state')
        for name in ['CUSTOM', 'ZERO', 'HartreeFock']:
            self.assertIn(name, section_names)

    def test_get_default_sections(self):
        section_names = self._model.get_default_sections().keys()
        for name in ['algorithm', 'backend', 'initial_state', 'input', 'optimizer', 'problem', 'variational_form']:
            self.assertIn(name, section_names)

    def test_get_section_default_properties(self):
        properties = self._model.get_section_default_properties('initial_state')
        self.assertEqual(properties, {'name': 'ZERO'})

    def test_allows_additional_properties(self):
        ret = self._model.allows_additional_properties('algorithm')
        self.assertFalse(ret)

    def test_get_property_default_value(self):
        value = self._model.get_property_default_value('algorithm', 'name')
        self.assertEqual(value, 'VQE')

    def test_get_property_types(self):
        types = self._model.get_property_types('algorithm', 'operator_mode')
        self.assertEqual(types, ['string'])

    def test_set_section_property(self):
        self._model.set_section_property('algorithm', 'operator_mode', 'paulis')
        prop = self._model.get_section_property('algorithm', 'operator_mode')
        self.assertEqual(prop, 'paulis')

    def test_delete_section_property(self):
        self._model.delete_section_property('optimizer', 'factr')
        ret = self._model.get_section_property('optimizer', 'factr')
        self.assertIsNone(ret)

    def test_set_section_text(self):
        # check that it fails because algorithm doesn't allow text
        with self.assertRaises(AquaError):
            self._model.set_section_text('algorithm', 'dummy')


if __name__ == '__main__':
    unittest.main()
