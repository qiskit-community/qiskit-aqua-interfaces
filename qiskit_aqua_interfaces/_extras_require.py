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

"""Extra requirements check"""

import pkg_resources


def _check_extra_requires(entry_point_type, entry_point_name):
    """Check if extra requirements are installed"""

    entry_point = pkg_resources.get_entry_info('qiskit_aqua_interfaces',
                                               entry_point_type,
                                               entry_point_name)
    if not entry_point:
        raise ValueError("Entry Point not found: '{}' '{}'.".format(entry_point_type,
                                                                    entry_point_name))

    # make sure that all extras are installed
    entry_point.require()
