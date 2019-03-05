# -*- coding: utf-8 -*-

# Copyright 2018 IBM.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# =============================================================================

"""
InputParser test.
"""

import unittest
from test.common import QiskitAquaUisTestCase
from qiskit_aqua_uis.chemistry.user_interface._model import Model


class TestChemistryModel(QiskitAquaUisTestCase):
    """Aqua UI Model tests."""

    def setUp(self):
        super().setUp()
        self._filepath = self._get_resource_path('resources/hdf5_h2_0.735_sto-3g.txt')

    def test_new(self):
        model = Model()
        section_names = model.new()
        for name in ['algorithm', 'backend', 'driver', 'hdf5', 'operator']:
            self.assertIn(name, section_names)

    def test_open(self):
        model = Model()
        model.load_file(self._filepath)
        section_names = model.get_section_names()
        for name in ['name', 'driver', 'hdf5', 'operator', 'optimizer', 'variational_form', 'algorithm', 'backend']:
            self.assertIn(name, section_names)


if __name__ == '__main__':
    unittest.main()
