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

"""Root main view"""

import sys
import tkinter as tk
import tkinter.messagebox as tkmb
import tkinter.ttk as ttk
import tkinter.filedialog as tkfd
from tkinter import font
import webbrowser
import os
from qiskit_aqua_interfaces import __version__, APP_DEPRECATION_MSG
from ._sectionsview import SectionsView
from ._sectiontextview import SectionTextView
from ._threadsafeoutputview import ThreadSafeOutputView
from ._emptyview import EmptyView
from ._preferencesdialog import PreferencesDialog

# pylint: disable=import-outside-toplevel


class MainView(ttk.Frame):
    """ Main View """
    def __init__(self, parent, guiprovider) -> None:
        """Create MainView object."""
        super(MainView, self).__init__(parent)
        self._guiprovider = guiprovider
        self._guiprovider.controller.view = self
        self.pack(expand=tk.YES, fill=tk.BOTH)
        self._create_widgets()
        self.master.title(self._guiprovider.title)
        if parent is not None:
            parent.protocol('WM_DELETE_WINDOW', self.quit)

    def _show_about_dialog(self):
        import qiskit.aqua as qa
        lines = ['Qiskit Aqua Interfaces',
                 'Version: {}'.format(__version__),
                 '',
                 'Qiskit Aqua',
                 'Version: {}'.format(qa.__version__),
                 ]
        tkmb.showinfo(self._guiprovider.title, message='\n'.join(lines))

    def _show_preferences(self):
        dialog = PreferencesDialog(self, self._guiprovider)
        dialog.do_init(tk.LEFT)
        dialog.do_modal()

    def _create_widgets(self):
        self._make_menubar()
        self._make_toolbar()
        self._create_pane()

    def _make_toolbar(self):
        toolbar = ttk.Frame(self, relief=tk.SUNKEN, borderwidth=2)
        toolbar.pack(side=tk.BOTTOM, fill=tk.X)
        self._guiprovider.controller._button_text = tk.StringVar()
        self._guiprovider.controller._button_text.set(self._guiprovider.controller._command)
        self._guiprovider.controller._start_button = \
            ttk.Button(toolbar,
                       textvariable=self._guiprovider.controller._button_text,
                       state='disabled',
                       command=self._guiprovider.controller.toggle)
        self._guiprovider.controller._start_button.pack(side=tk.LEFT)
        self._guiprovider.add_toolbar_items(toolbar)
        self._guiprovider.controller._progress = ttk.Progressbar(toolbar, orient=tk.HORIZONTAL)
        self._guiprovider.controller._progress.pack(side=tk.RIGHT, fill=tk.BOTH, expand=tk.TRUE)

    def _make_menubar(self):
        menubar = tk.Menu(self.master)
        if sys.platform == 'darwin':
            app_menu = tk.Menu(menubar, name='apple')
            menubar.add_cascade(menu=app_menu)
            app_menu.add_command(label='About {}'.format(
                self._guiprovider.title), command=self._show_about_dialog)
            self.master.createcommand('tk::mac::ShowPreferences', self._show_preferences)
            self.master.createcommand('tk::mac::Quit', self.quit)

        self.master.config(menu=menubar)
        self._guiprovider.controller._filemenu = self._make_filemenu(menubar)

        if sys.platform != 'darwin':
            tools_menu = tk.Menu(menubar, tearoff=False)
            tools_menu.add_command(label='Options', command=self._show_preferences)
            menubar.add_cascade(label='Tools', menu=tools_menu)

        help_menu = tk.Menu(menubar, tearoff=False)
        if sys.platform != 'darwin':
            help_menu.add_command(label='About {}'.format(self._guiprovider.title),
                                  command=self._show_about_dialog)

        help_menu.add_command(label='Open Help Center', command=self._open_help_center)
        menubar.add_cascade(label='Help', menu=help_menu)

    def _open_help_center(self):
        webbrowser.open(self._guiprovider.help_hyperlink)

    def _make_filemenu(self, menubar):
        file_menu = tk.Menu(menubar, tearoff=False, postcommand=self._recent_files_menu)
        file_menu.add_command(label='New', command=self._new_input)
        file_menu.add_command(label='Open...', command=self._open_file)
        file_menu.add_cascade(label='Open Recent', menu=tk.Menu(file_menu, tearoff=False))
        file_menu.add_separator()
        file_menu.add_command(label='Save', command=self._save_file)
        file_menu.add_command(label='Save As...', command=self._save_file_as)

        self._guiprovider.add_file_menu_items(file_menu)

        if sys.platform != 'darwin':
            file_menu.add_separator()
            file_menu.add_command(label='Exit', command=self.quit)

        menubar.add_cascade(label='File', menu=file_menu)
        return file_menu

    def _recent_files_menu(self):
        recent_menu = tk.Menu(self._guiprovider.controller._filemenu, tearoff=False)
        preferences = self._guiprovider.create_uipreferences()
        for file in preferences.get_recent_files():
            recent_menu.add_command(label=file, command=lambda f=file: self._open_recent_file(f))

        recent_menu.add_separator()
        recent_menu.add_command(label='Clear', command=self._clear_recent)
        self._guiprovider.controller._filemenu.entryconfig(2, menu=recent_menu)

    def _new_input(self):
        self._guiprovider.controller.new_input()

    def _open_file(self):
        preferences = self._guiprovider.create_uipreferences()
        filename = tkfd.askopenfilename(parent=self,
                                        title='Open File',
                                        initialdir=preferences.get_openfile_initialdir())
        if filename and self._guiprovider.controller.open_file(filename):
            preferences.add_recent_file(filename)
            preferences.set_openfile_initialdir(os.path.dirname(filename))
            preferences.save()

    def _open_recent_file(self, filename):
        self._guiprovider.controller.open_file(filename)

    def _clear_recent(self):
        preferences = self._guiprovider.create_uipreferences()
        preferences.clear_recent_files()
        preferences.save()

    def _save_file(self):
        self._guiprovider.controller.save_file()

    def _save_file_as(self):
        if self._guiprovider.controller.is_empty():
            self._guiprovider.controller.outputview.write_line("No data to save.")
            return

        preferences = self._guiprovider.create_uipreferences()
        filename = tkfd.asksaveasfilename(parent=self,
                                          title='Save File',
                                          initialdir=preferences.get_savefile_initialdir())
        if filename and self._guiprovider.controller.save_file_as(filename):
            preferences.add_recent_file(filename)
            preferences.set_savefile_initialdir(os.path.dirname(filename))
            preferences.save()

    def _create_pane(self):
        label_font = font.nametofont('TkHeadingFont').copy()
        label_font.configure(size=12, weight='bold')
        style = ttk.Style()
        style.configure('Title.TLabel',
                        borderwidth=0,
                        anchor=tk.CENTER)
        label = ttk.Label(self,
                          style='Title.TLabel',
                          padding=(5, 5, 5, 5),
                          textvariable=self._guiprovider.controller._title)
        label['font'] = label_font
        label.pack(side=tk.TOP, expand=tk.NO, fill=tk.X)
        main_pane = ttk.PanedWindow(self, orient=tk.VERTICAL)
        main_pane.pack(expand=tk.YES, fill=tk.BOTH)
        top_pane = ttk.PanedWindow(main_pane, orient=tk.HORIZONTAL)
        top_pane.pack(expand=tk.YES, fill=tk.BOTH)
        main_pane.add(top_pane)

        self._guiprovider.controller._sections_view = \
            SectionsView(self._guiprovider.controller, top_pane)
        self._guiprovider.controller._sections_view.pack(expand=tk.YES, fill=tk.BOTH)
        top_pane.add(self._guiprovider.controller._sections_view, weight=1)

        main_container = tk.Frame(top_pane)
        main_container.pack(expand=tk.YES, fill=tk.BOTH)
        style = ttk.Style()
        style.configure('PropViewTitle.TLabel',
                        borderwidth=1,
                        relief=tk.RIDGE,
                        anchor=tk.CENTER)
        label = ttk.Label(main_container,
                          style='PropViewTitle.TLabel',
                          padding=(5, 5, 5, 5),
                          textvariable=self._guiprovider.controller._sections_view_title)
        label['font'] = label_font

        label.pack(side=tk.TOP, expand=tk.NO, fill=tk.X)
        container = tk.Frame(main_container)
        container.pack(side=tk.BOTTOM, expand=tk.YES, fill=tk.BOTH)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        self._guiprovider.controller._empty_view = EmptyView(container)
        self._guiprovider.controller._empty_view.grid(row=0, column=0, sticky='nsew')

        self._guiprovider.controller._text_view = \
            SectionTextView(self._guiprovider.controller, container)
        self._guiprovider.controller._text_view.grid(row=0, column=0, sticky='nsew')

        self._guiprovider.controller._properties_view = \
            self._guiprovider.create_section_properties_view(container)
        self._guiprovider.controller._properties_view.grid(row=0, column=0, sticky='nsew')
        self._guiprovider.controller._empty_view.tkraise()
        top_pane.add(main_container, weight=1)

        self._guiprovider.controller.outputview = ThreadSafeOutputView(main_pane)
        self._guiprovider.controller.outputview.pack(expand=tk.YES, fill=tk.BOTH)
        main_pane.add(self._guiprovider.controller.outputview)

        # redirect output
        sys.stdout = self._guiprovider.controller.outputview
        sys.stderr = self._guiprovider.controller.outputview
        # update logging after redirect
        self.after(0, self._set_preferences_logging)

        self.update_idletasks()
        self._guiprovider.controller._sections_view.show_add_button(False)
        self._guiprovider.controller._sections_view.show_remove_button(False)
        self._guiprovider.controller._sections_view.show_defaults_button(False)
        self._guiprovider.controller._empty_view.set_toolbar_size(
            self._guiprovider.controller._sections_view.get_toolbar_size())

        self._guiprovider.controller.outputview.write_line(APP_DEPRECATION_MSG)

    def _set_preferences_logging(self):
        preferences = self._guiprovider.create_uipreferences()
        config = preferences.get_logging_config()
        if config is not None:
            self._guiprovider.set_logging_config(config)

    def quit(self):
        if tkmb.askyesno('Verify quit', 'Are you sure you want to quit?'):
            preferences = self._guiprovider.create_uipreferences()
            preferences.set_geometry(self.master.winfo_geometry())
            preferences.save()
            self._guiprovider.controller.stop()
            ttk.Frame.quit(self)
            return True

        return False
