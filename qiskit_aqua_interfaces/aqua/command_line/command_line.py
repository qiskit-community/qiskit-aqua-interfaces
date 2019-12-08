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

"""Qiskit Aqua command line main."""

import sys
import argparse
import json
from collections import OrderedDict
import textwrap
import logging
from qiskit_aqua_interfaces import APP_DEPRECATION_MSG
from qiskit_aqua_interfaces._extras_require import _check_extra_requires

# pylint: disable=import-outside-toplevel


def main():
    """Runs main Aqua command line."""
    if sys.platform != 'darwin':
        _run()
        return

    # On MacOSX avoid possible matplotlib error in case it is imported by other imported libraries
    import tkinter as tk
    root = tk.Tk()
    root.withdraw()
    root.after(0, _run_delay, root)
    root.mainloop()


def _run_delay(root):
    try:
        _run()
    finally:
        if root is not None:
            root.destroy()


def _run():
    _check_extra_requires('console_scripts', 'qiskit_aqua_cmd')
    from qiskit.aqua._logging import (get_logging_level,
                                      build_logging_config,
                                      set_logging_config,
                                      set_qiskit_aqua_logging)
    from qiskit_aqua_interfaces.aqua.user_interface import UIPreferences
    from qiskit.aqua import run_algorithm
    from qiskit.aqua.utils import convert_json_to_dict

    preferences = UIPreferences()
    log_levels = OrderedDict(
        [(logging.getLevelName(logging.CRITICAL).lower(), logging.CRITICAL),
         (logging.getLevelName(logging.ERROR).lower(), logging.ERROR),
         (logging.getLevelName(logging.WARNING).lower(), logging.WARNING),
         (logging.getLevelName(logging.INFO).lower(), logging.INFO),
         (logging.getLevelName(logging.DEBUG).lower(), logging.DEBUG),
         (logging.getLevelName(logging.NOTSET).lower(), logging.NOTSET)]
    )

    parser = argparse.ArgumentParser(prog='qiskit_aqua_cmd',
                                     formatter_class=argparse.RawTextHelpFormatter,
                                     description='Qiskit Aqua Command Line Tool')
    parser.add_argument('input',
                        metavar='input',
                        help='Algorithm JSON input file')
    parser.add_argument('-jo',
                        metavar='output',
                        help='Algorithm JSON output file name')
    parser.add_argument('-l',
                        metavar='logging',
                        choices=log_levels.keys(),
                        help=textwrap.dedent('''\
                            Logging level:
                            {}
                            (defaults to level from preferences file: {})
                             '''.format(list(log_levels.keys()), preferences.filepath))
                        )

    args = parser.parse_args()

    if args.l is not None:
        set_qiskit_aqua_logging(log_levels.get(args.l, logging.INFO))
    else:
        # update logging setting with latest external packages
        logging_level = logging.INFO
        if preferences.get_logging_config() is not None:
            set_logging_config(preferences.get_logging_config())
            logging_level = get_logging_level()

        preferences.set_logging_config(build_logging_config(logging_level))
        preferences.save()
        set_logging_config(preferences.get_logging_config())

    params = None
    with open(args.input) as json_file:
        params = json.load(json_file)

    print(APP_DEPRECATION_MSG)
    ret = run_algorithm(params, None, True)

    if args.jo is not None:
        with open(args.jo, 'w') as run_output:
            print('{}'.format(ret), file=run_output)
    else:
        convert_json_to_dict(ret)
        print('\n\n--------------------------------- R E S U L T -----'
              '-------------------------------\n')
        if isinstance(ret, dict):
            for k, v in ret.items():
                print("'{}': {}".format(k, v))
        else:
            print(ret)
