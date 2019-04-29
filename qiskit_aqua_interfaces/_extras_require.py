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

import pkg_resources


def _check_extra_requires(entry_point_type, entry_point_name):
    """
    Check if extra requirements are installed
    """

    entry_point = pkg_resources.get_entry_info('qiskit_aqua_interfaces',
                                               entry_point_type,
                                               entry_point_name)
    if not entry_point:
        raise ValueError("Entry Point not found: '{}' '{}'.".format(entry_point_type, entry_point_name))

    # make sure that all extras are installed
    entry_point.require()
