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

"""Credentials view"""

import threading
import queue
import logging
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import font
from tkinter import messagebox
import urllib
from ._customwidgets import EntryCustom
from ._toolbarview import ToolbarView
from ._dialog import Dialog

logger = logging.getLogger(__name__)

# pylint: disable=import-outside-toplevel


class CredentialsView(ttk.Frame):
    """ Credentials View """
    _START, _STOP = 'Start', 'Stop'

    def __init__(self, parent, **options) -> None:
        super(CredentialsView, self).__init__(parent, **options)

        self._thread_queue = queue.Queue()
        self._thread = None

        self.pack(fill=tk.BOTH, expand=tk.TRUE)

        from qiskit.aqua import Preferences
        preferences = Preferences()
        cred_prefs = preferences.ibmq_credentials_preferences

        self._token = tk.StringVar()
        self._token.set(cred_prefs.token if cred_prefs.token is not None else '')
        ttk.Label(self,
                  text="Token:",
                  borderwidth=0,
                  anchor=tk.E).grid(row=0, column=0, pady=5, sticky='nsew')
        self._token_entry = EntryCustom(self,
                                        textvariable=self._token,
                                        width=120,
                                        state=tk.NORMAL)
        self._token_entry.grid(row=0, column=1, padx=5, pady=5, sticky='nsew')

        self._hub = tk.StringVar()
        self._hub.set(cred_prefs.hub if cred_prefs.hub is not None else '')
        ttk.Label(self,
                  text="Hub:",
                  borderwidth=0,
                  anchor=tk.E).grid(row=1, column=0, pady=5, sticky='nsew')
        self._hub_entry = ttk.Label(self,
                                    textvariable=self._hub,
                                    borderwidth=0,
                                    width=50)
        self._hub_entry.grid(row=1, column=1, padx=5, pady=5, sticky='nsw')

        self._group = tk.StringVar()
        self._group.set(cred_prefs.group if cred_prefs.group is not None else '')
        ttk.Label(self,
                  text="Group:",
                  borderwidth=0,
                  anchor=tk.E).grid(row=2, column=0, pady=5, sticky='nsew')
        self._group_entry = ttk.Label(self,
                                      textvariable=self._group,
                                      borderwidth=0,
                                      width=50)
        self._group_entry.grid(row=2, column=1, padx=5, pady=5, sticky='nsw')

        self._project = tk.StringVar()
        self._project.set(cred_prefs.project if cred_prefs.project is not None else '')
        ttk.Label(self,
                  text="Project:",
                  borderwidth=0,
                  anchor=tk.E).grid(row=3, column=0, pady=5, sticky='nsew')
        self._project_entry = ttk.Label(self,
                                        textvariable=self._project,
                                        borderwidth=0,
                                        width=50)
        self._project_entry.grid(row=3, column=1, padx=5, pady=5, sticky='nsw')

        self._chose_button = ttk.Button(self,
                                        text='Chose Hub/Group/Project',
                                        state='enable',
                                        command=self.cb_chose)
        self._chose_button.grid(row=4, column=1, padx=5, pady=5, sticky='nsw')

        ttk.Label(self,
                  text="Proxies:",
                  borderwidth=0,
                  anchor=tk.E).grid(row=5, column=0, pady=5, sticky='nsew')
        self._proxiespage = ProxiesPage(self, cred_prefs)
        self._proxiespage.grid(row=6, column=0, columnspan=2, pady=5, sticky='nsew')
        self._proxiespage.show_add_button(True)
        self._proxiespage.show_remove_button(self._proxiespage.has_selection())
        self._proxiespage.show_defaults_button(False)
        self._proxiespage.enable(True)

        self.initial_focus = self._token_entry

    def cb_chose(self):
        """ chose Hub/Group/Project callback """
        try:
            self._chose_button.state(['disabled'])
            self.after(100, self._process_thread_queue)
            proxy_urls = self._proxiespage._proxy_urls
            self._thread = HGPThread(CredentialsView._get_var_value(self._token),
                                     {} if proxy_urls is None else {'urls': proxy_urls},
                                     self._thread_queue)
            self._thread.daemon = True
            self._thread.start()
        except Exception as ex:  # pylint: disable=broad-except
            self._thread = None
            self._thread_queue.put(None)
            self._chose_button.state(['!disabled'])
            logger.debug('Failed to access hub/group/project: %s', ex)

    def is_valid(self):
        """ check is entries are valid """
        return self._proxiespage.is_valid()

    def validate(self):
        """ validate entries """
        if not self._proxiespage.is_valid():
            self.initial_focus = self._proxiespage.initial_focus
            return False

        self.initial_focus = self._token_entry
        return True

    def do_cancel(self):
        """ cancel dialog """
        self._stop()

    @staticmethod
    def _get_var_value(stringvar):
        value = stringvar.get().strip()
        if value == '':
            value = None

        return value

    def apply(self, preferences):
        """ save changes """
        self._stop()
        # save previously shown data
        preferences.ibmq_credentials_preferences.hub = CredentialsView._get_var_value(self._hub)
        preferences.ibmq_credentials_preferences.group = CredentialsView._get_var_value(self._group)
        preferences.ibmq_credentials_preferences.project = \
            CredentialsView._get_var_value(self._project)
        preferences.ibmq_credentials_preferences.set_credentials(
            CredentialsView._get_var_value(self._token),
            self._proxiespage._proxy_urls)

    @staticmethod
    def _is_valid_url(url):
        if url is None or not isinstance(url, str):
            return False

        url = url.strip()
        if not url:
            return False

        min_attributes = ('scheme', 'netloc')
        valid = True
        try:
            token = urllib.parse.urlparse(url)
            if not all([getattr(token, attr) for attr in min_attributes]):
                valid = False
        except Exception:  # pylint: disable=broad-except
            valid = False

        return valid

    @staticmethod
    def _validate_url(url):
        valid = CredentialsView._is_valid_url(url)
        if not valid:
            messagebox.showerror("Error", 'Invalid url')

        return valid

    def _stop(self):
        self._thread = None
        self._thread_queue.put(None)

    def _process_thread_queue(self):
        try:
            line = self._thread_queue.get_nowait()
            if line is None:
                self._thread = None
                self._chose_button.state(['!disabled'])
                return
            elif line is CredentialsView._START:
                self._chose_button.state(['disabled'])
            elif line is CredentialsView._STOP:
                self.after(0, self._show_hgp_dialog, self._thread.hgp)
                self._thread = None
                self._chose_button.state(['!disabled'])
                return

            self.update_idletasks()
        except Exception:  # pylint: disable=broad-except
            pass

        self.after(100, self._process_thread_queue)

    def _show_hgp_dialog(self, hgp):
        if hgp:
            dialog = HGPEntryDialog(self.master)
            dialog.do_init(values=hgp)
            dialog.do_modal()
            if dialog.result:
                self._hub.set(dialog.result[0])
                self._group.set(dialog.result[1])
                self._project.set(dialog.result[2])
        else:
            messagebox.showerror("Warning", 'No Hub/Group/Project found.')


class HGPEntryDialog(Dialog):
    """ Hub/Group/Project Entry Dialog """
    def __init__(self, parent) -> None:
        super(HGPEntryDialog, self).__init__(None, parent, "Chose Hub/Group/Project")
        self._hgp = []

    def body(self, parent, options):
        ttk.Label(parent,
                  text="Hub/Group/Project:",
                  borderwidth=0).grid(padx=7, pady=6, row=0)
        self._hgp = options['values']
        hgp = ['{}/{}/{}'.format(hgp[0], hgp[1], hgp[2]) for hgp in self._hgp]
        self.entry = ttk.Combobox(parent,
                                  exportselection=0,
                                  state='readonly',
                                  values=hgp)
        self.entry.current(0)
        self.entry.grid(padx=(0, 7), pady=6, row=0, column=1)
        return self.entry  # initial focus

    def apply(self):
        index = self.entry.current()
        if index >= 0:
            self.result = self._hgp[index]


class HGPThread(threading.Thread):
    """ Hub/Group/Project Thread """
    def __init__(self, token, proxies, thread_queue) -> None:
        super(HGPThread, self).__init__(name='Hub/Group/Project thread')
        self._token = token
        self._proxies = proxies
        self._thread_queue = thread_queue
        self._hgp = []

    @property
    def hgp(self):
        """ return hub/group/project """
        return self._hgp

    def run(self):
        """ h/g/p thread process """
        try:
            self._hgp = []
            if self._thread_queue is not None:
                self._thread_queue.put(CredentialsView._START)
            # pylint: disable=no-name-in-module, import-error
            if self._token:
                from qiskit.providers.ibmq import IBMQFactory
                ibmq = IBMQFactory()
                ibmq.enable_account(self._token, proxies=self._proxies)
                providers = ibmq.providers()
                for provider in providers:
                    self._hgp.append((provider.credentials.hub,
                                      provider.credentials.group,
                                      provider.credentials.project))
        except Exception as ex:  # pylint: disable=broad-except
            logger.warning('IBMQ account Account Failure. Proxies:%s :%s', self._proxies, ex)
        finally:
            if self._thread_queue is not None:
                self._thread_queue.put(CredentialsView._STOP)


class ProxiesPage(ToolbarView):
    """ Proxies Page View """
    def __init__(self, parent, preferences, **options) -> None:
        super(ProxiesPage, self).__init__(parent, **options)
        size = font.nametofont('TkHeadingFont').actual('size')
        ttk.Style().configure("ProxiesPage.Treeview.Heading", font=(None, size, 'bold'))
        self._tree = ttk.Treeview(
            self, style='ProxiesPage.Treeview', selectmode=tk.BROWSE, height=3, columns=['value'])
        self._tree.heading('#0', text='Protocol')
        self._tree.heading('value', text='URL')
        self._tree.column('#0', minwidth=0, width=150, stretch=tk.NO)
        self._tree.bind('<<TreeviewSelect>>', self._cb_tree_select)
        self._tree.bind('<Button-1>', self._cb_tree_edit)
        self.init_widgets(self._tree)

        self._proxy_urls = preferences.proxy_urls
        if self._proxy_urls is None:
            self._proxy_urls = {}
        self._popup_widget = None
        self.populate()
        self.initial_focus = self._tree

    def enable(self, enable=True):
        """ enable/disable proxy page """
        if enable and "disabled" in self._tree.state():
            self._tree.state(("!disabled",))
            self.show_add_button(True)
            self.show_remove_button(self.has_selection())
            return

        if not enable and "disabled" not in self._tree.state():
            self._tree.state(("disabled",))
            self.show_add_button(False)
            self.show_remove_button(False)

    def clear(self):
        """ clear proxies """
        if self._popup_widget is not None and self._popup_widget.winfo_exists():
            self._popup_widget.destroy()

        self._popup_widget = None
        for i in self._tree.get_children():
            self._tree.delete([i])

    def populate(self):
        """ populate proxies """
        self.clear()
        for protocol, url in self._proxy_urls.items():
            url = '' if url is None else str(url)
            url = url.replace('\r', '\\r').replace('\n', '\\n')
            self._tree.insert('', tk.END, text=protocol, values=[url])

    def set_proxy(self, protocol, url):
        """ update a proxy """
        for item in self._tree.get_children():
            if self._tree.item(item, "text") == protocol:
                self._tree.item(item, values=[url])
                break

    def has_selection(self):
        """ check if proxy entry is selected """
        return self._tree.selection()

    def _cb_tree_select(self, event):
        for _ in self._tree.selection():
            self.show_remove_button(True)
            return

    def _cb_tree_edit(self, event):
        if 'disabled' in self._tree.state():
            return

        rowid = self._tree.identify_row(event.y)
        if not rowid:
            return

        column = self._tree.identify_column(event.x)
        if column == '#1':
            x, y, width, height = self._tree.bbox(rowid, column)
            pady = height // 2

            item = self._tree.identify("item", event.x, event.y)
            protocol = self._tree.item(item, "text")
            self._popup_widget = URLPopup(self,
                                          protocol,
                                          self._tree,
                                          self._proxy_urls[protocol],
                                          state=tk.NORMAL)
            self._popup_widget.select_all()
            self._popup_widget.place(x=x, y=y + pady, anchor=tk.W, width=width)

    def cb_add(self):
        dialog = ProxyEntryDialog(self.master, self)
        dialog.do_init(tk.LEFT)
        dialog.do_modal()
        if dialog.result is None:
            return

        if dialog.result is not None:
            self._proxy_urls[dialog.result[0]] = dialog.result[1]
            self.populate()
            self.show_remove_button(self.has_selection())

    def cb_remove(self):
        for item in self._tree.selection():
            protocol = self._tree.item(item, 'text')
            if protocol in self._proxy_urls:
                del self._proxy_urls[protocol]
                self.populate()
                self.show_remove_button(self.has_selection())
            break

    def cb_proxy_set(self, protocol, url):
        """ proxy set callback """
        protocol = protocol.strip()
        if not protocol:
            return False

        url = url.strip()
        if not CredentialsView._validate_url(url):
            return False

        self._proxy_urls[protocol] = url
        self.populate()
        self.show_remove_button(self.has_selection())
        return True

    def is_valid(self):
        """ check if entries are valid """
        return True

    def validate(self):
        """ validate entries """
        return True

    def apply(self, preferences):
        """ save entries """
        preferences.set_proxy_urls(self._proxy_urls if self._proxy_urls else None)


class URLPopup(EntryCustom):
    """ URL Popup """
    def __init__(self, controller, protocol, parent, url, **options) -> None:
        # If relwidth is set, then width is ignored
        super(URLPopup, self).__init__(parent, **options)
        self._controller = controller
        self._protocol = protocol
        self._url = url
        self.insert(0, self._url)
        self.focus_force()
        self.bind("<Unmap>", self._cb_update_value)
        self.bind("<FocusOut>", self._cb_update_value)

    def select_all(self):
        """ select entry """
        self.focus_force()
        self.selection_range(0, tk.END)

    def _cb_update_value(self, *ignore):
        new_url = self.get().strip()
        valid = True
        if self._url != new_url:
            self._url = new_url
            valid = self._controller.cb_proxy_set(self._protocol, new_url)
        if valid:
            self.destroy()
        else:
            self.select_all()


class ProxyEntryDialog(Dialog):
    """ Proxy Entry Dialog """
    def __init__(self, parent, controller) -> None:
        super(ProxyEntryDialog, self).__init__(None, parent, "New Proxy")
        self._protocol = None
        self._url = None
        self._controller = controller

    def body(self, parent, options):
        """ create body """
        ttk.Label(parent,
                  text="Protocol:",
                  borderwidth=0,
                  anchor=tk.E).grid(padx=7, pady=6, row=0, sticky='nse')
        self._protocol = EntryCustom(parent, state=tk.NORMAL)
        self._protocol.grid(padx=(0, 7), pady=6, row=0, column=1, sticky='nsw')
        ttk.Label(parent,
                  text="URL:",
                  borderwidth=0,
                  anchor=tk.E).grid(padx=7, pady=6, row=1, sticky='nse')
        self._url = EntryCustom(parent, state=tk.NORMAL, width=50)
        self._url.grid(padx=(0, 7), pady=6, row=1, column=1, sticky='nsew')
        return self._protocol  # initial focus

    def validate(self):
        """ validate entries """
        protocol = self._protocol.get().strip()
        if not protocol or protocol in self._controller._proxy_urls:
            self.initial_focus = self._protocol
            return False

        url = self._url.get().strip()
        if not CredentialsView._validate_url(url):
            self.initial_focus = self._url
            return False

        self.initial_focus = self._protocol
        return True

    def apply(self):
        """ save entries """
        self.result = (self._protocol.get().strip(), self._url.get().strip())
