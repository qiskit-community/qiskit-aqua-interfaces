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

"""Chemistry Model test."""

import unittest
from test.common import QiskitAquaUisTestCase
from qiskit.aqua import AquaError
from qiskit_aqua_interfaces.chemistry.user_interface._model import Model


class TestChemistryModel(QiskitAquaUisTestCase):
    """Aqua UI Model tests."""

    def setUp(self):
        super().setUp()
        _filepath = self._get_resource_path('resources/hdf5_h2_0.735_sto-3g.txt')
        self._model = Model()
        self._model.load_file(_filepath)
        # make sure defaults are populated
        self._model._parser.validate_merge_defaults()

    def test_new(self):
        """Test new model. Passes if required sections are included."""
        section_names = self._model.new()
        for name in ['algorithm', 'backend', 'driver', 'hdf5', 'operator']:
            self.assertIn(name, section_names)

    def test_open(self):
        """Test open model. Passes if required sections are included."""
        section_names = self._model.get_section_names()
        for name in ['name', 'driver', 'hdf5', 'operator',
                     'optimizer', 'variational_form', 'algorithm', 'backend']:
            self.assertIn(name, section_names)

    def test_get_property_default_values(self):
        """Test if model has correct default values."""
        initial_point = self._model.get_property_default_values('algorithm', 'initial_point')
        self.assertEqual(initial_point, None)

    def test_section_is_text(self):
        """Test if model has correct text section."""
        ret = self._model.section_is_text('problem')
        self.assertFalse(ret)

    def test_get_section(self):
        """Test if model can access section."""
        section = self._model.get_section('initial_state')
        self.assertEqual(section, {'name': 'ZERO'})

    def test_get_section_text(self):
        """Test if model can access section text."""
        text = self._model.get_section_text('algorithm')
        self.assertIsInstance(text, str)

    def test_get_section_properties(self):
        """Test if model can access section properties."""
        expected = {
            'depth': 3,
            'entanglement': "full",
            'entangler_map': None,
            'name': "RYRZ"
        }
        properties = self._model.get_section_properties('variational_form')
        subset = {k: v for k, v in properties.items() if k in expected}
        self.assertDictEqual(subset, expected)

    def test_default_properties_equals_properties(self):
        """Test if model default properties are the same as current properties."""
        ret = self._model.default_properties_equals_properties('optimizer')
        self.assertTrue(ret)

    def test_get_section_property(self):
        """Test if model can access section property."""
        prop = self._model.get_section_property('algorithm', 'name')
        self.assertEqual(prop, 'VQE')

    def test_set_section(self):
        """Test if model can update section."""
        self._model.set_section('oracle')
        section_names = self._model.get_section_names()
        self.assertIn('oracle', section_names)

    def test_get_pluggable_section_names(self):
        """Test if model can access pluggable sections."""
        section_names = self._model.get_pluggable_section_names('initial_state')
        for name in ['CUSTOM', 'ZERO', 'HartreeFock']:
            self.assertIn(name, section_names)

    def test_get_default_sections(self):
        """Test if model can access default sections."""
        section_names = self._model.get_default_sections().keys()
        for name in ['name', 'driver', 'hdf5', 'operator', 'optimizer',
                     'variational_form', 'algorithm', 'backend']:
            self.assertIn(name, section_names)

    def test_get_section_default_properties(self):
        """Test if model can access default section properties."""
        properties = self._model.get_section_default_properties('initial_state')
        self.assertEqual(properties, {'name': 'ZERO'})

    def test_allows_additional_properties(self):
        """Test if model section allows more properties."""
        ret = self._model.allows_additional_properties('algorithm')
        self.assertFalse(ret)

    def test_get_property_default_value(self):
        """Test if model can access default section property default value."""
        value = self._model.get_property_default_value('algorithm', 'name')
        self.assertEqual(value, 'VQE')

    def test_get_property_types(self):
        """Test if model can access property types."""
        types = self._model.get_property_types('algorithm', 'initial_point')
        self.assertEqual(types, ['array', 'null'])

    def test_set_section_property(self):
        """Test if model can update property."""
        self._model.set_section_property('algorithm', 'initial_point', None)
        prop = self._model.get_section_property('algorithm', 'initial_point')
        self.assertEqual(prop, None)

    def test_delete_section_property(self):
        """Test if model can delete property."""
        self._model.delete_section_property('optimizer', 'factr')
        ret = self._model.get_section_property('optimizer', 'factr')
        self.assertIsNone(ret)

    def test_set_section_text(self):
        """check that it fails because algorithm doesn't allow text"""
        with self.assertRaises(AquaError):
            self._model.set_section_text('algorithm', 'dummy')

    def test_get_dictionary(self):
        """Test if model can access dictionary properties."""
        ret = self._model.get_dictionary()
        self.assertIsInstance(ret, dict)

    def test_get_section_properties_with_substitution(self):
        """Test if model can access properties with substitutions."""
        expected = {'name': ('ZERO', False)}
        props = self._model.get_section_properties_with_substitution('initial_state')
        self.assertEqual(props, expected)

    def test_get_operator_section_names(self):
        """Test if model can access operator section names."""
        operators = self._model.get_operator_section_names()
        self.assertIn('hamiltonian', operators)


if __name__ == '__main__':
    unittest.main()
