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

import sys
import logging
import tkinter as tk
from tkinter import messagebox
from qiskit_aqua_interfaces.aqua.user_interface import MainView
from qiskit_aqua_interfaces._extras_require import _check_extra_requires


def set_preferences_logging():
    """
    Update logging setting with latest external packages
    """
    from qiskit.chemistry._logging import get_logging_level, build_logging_config, set_logging_config
    from ._chemguiprovider import ChemistryGUIProvider
    guiProvider = ChemistryGUIProvider()
    preferences = guiProvider.create_uipreferences()
    logging_level = logging.INFO
    if preferences.get_logging_config() is not None:
        set_logging_config(preferences.get_logging_config())
        logging_level = get_logging_level()

    preferences.set_logging_config(build_logging_config(logging_level))
    preferences.save()


def main():
    _check_extra_requires('gui_scripts', 'qiskit_chemistry_ui')
    error_msg = None
    guiProvider = None
    try:
        from ._chemguiprovider import ChemistryGUIProvider
        guiProvider = ChemistryGUIProvider()
    except ImportError:
        error_msg = 'Please install qiskit-chemistry before running.'

    if sys.platform == 'darwin' and guiProvider is not None:
        from Foundation import NSBundle
        bundle = NSBundle.mainBundle()
        if bundle:
            info = bundle.localizedInfoDictionary() or bundle.infoDictionary()
            info['CFBundleName'] = guiProvider.title

    root = tk.Tk()
    root.withdraw()
    root.update_idletasks()
    if error_msg is not None:
        messagebox.showerror("Error", error_msg)
        return

    preferences = guiProvider.create_uipreferences()
    geometry = preferences.get_geometry()
    if geometry is None:
        ws = root.winfo_screenwidth()
        hs = root.winfo_screenheight()
        w = int(ws / 1.3)
        h = int(hs / 1.3)
        x = int(ws / 2 - w / 2)
        y = int(hs / 2 - h / 2)
        geometry = '{}x{}+{}+{}'.format(w, h, x, y)
        preferences.set_geometry(geometry)
        preferences.save()

    root.geometry(geometry)

    MainView(root, guiProvider)
    root.after(0, root.deiconify)
    root.after(0, set_preferences_logging)
    root.mainloop()
