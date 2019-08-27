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

"""Base Dialog view"""

import tkinter as tk
import tkinter.ttk as ttk


class Dialog(tk.Toplevel):
    """ Dialog """
    def __init__(self, controller, parent, title='') -> None:
        super(Dialog, self).__init__(parent)
        self.transient(parent)
        self.resizable(0, 0)
        self.title(title)
        self._controller = controller
        self.result = None
        self.initial_focus = None
        self.entry = None

    def do_init(self, cancel_side=tk.RIGHT, **options):
        """ initialize dialog """
        body = ttk.Frame(self)
        self.initial_focus = self.body(body, options)
        body.pack(fill=tk.BOTH, expand=tk.TRUE)

        self._buttonbox(cancel_side)

        self.grab_set()

        if not self.initial_focus:
            self.initial_focus = self

        self.protocol("WM_DELETE_WINDOW", self._cb_cancel)

        w_s = self.master.winfo_reqwidth()
        h_s = self.master.winfo_reqheight()
        x = int(self.master.winfo_rootx() + w_s / 3 - self.winfo_reqwidth() / 2)
        y = int(self.master.winfo_rooty() + h_s / 3 - self.winfo_reqheight() / 2)

        self.geometry('+{}+{}'.format(x, y))

    def do_modal(self):
        """ modal processing """
        self.initial_focus.focus_set()
        self.wait_window(self)

    @property
    def controller(self):
        """ return controller """
        return self._controller

    def _buttonbox(self, cancel_side=tk.RIGHT):
        box = ttk.Frame(self)

        w = ttk.Button(box, text="OK", width=10, command=self._cb_ok, default=tk.ACTIVE)
        w.pack(side=tk.LEFT, padx=5, pady=5)
        w = ttk.Button(box, text="Cancel", width=10, command=self._cb_cancel)
        w.pack(side=cancel_side, padx=5, pady=5)

        self.bind("<Return>", self._cb_ok)
        self.bind("<Escape>", self._cb_cancel)

        box.pack(side=tk.BOTTOM, expand=tk.NO, fill=tk.X)

    def _cb_ok(self, event=None):
        if not self.validate():
            self.initial_focus.focus_set()
            return

        self.withdraw()
        self.update_idletasks()

        self.apply()

        self._cb_cancel()

    def _cb_cancel(self, event=None):
        self.do_cancel()
        self.master.focus_set()
        self.destroy()

    def body(self, parent, options):
        """ populate body """
        del parent
        del options
        return self  # override

    def validate(self):
        """ validate entries """
        return True  # override

    def apply(self):
        """ save data """
        pass  # override

    def do_cancel(self):
        """ cancel entries """
        pass  # override
