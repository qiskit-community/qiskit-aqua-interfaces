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

"""Qiskit User Interface base controller"""

from abc import ABC, abstractmethod
import os
import threading
import queue
import tkinter as tk
from tkinter import messagebox
import ast
import json
import logging
from .guiprovider import GUIProvider
from .base_model import BaseModel
from ._customwidgets import (EntryPopup, ComboboxPopup, TextPopup)

logger = logging.getLogger(__name__)

# pylint: disable=import-outside-toplevel


class BaseController(ABC):
    """Base GUI Controller."""

    @abstractmethod
    def __init__(self, guiprovider, model) -> None:
        self._view = None
        self._guiprovider = guiprovider
        self._model = model
        self._filemenu = None
        self._title = tk.StringVar()
        self._sections_view = None
        self._empty_view = None
        self._sections_view_title = tk.StringVar()
        self._properties_view = None
        self._text_view = None
        self._outputview = None
        self._progress = None
        self._button_text = None
        self._start_button = None
        self._thread_queue = queue.Queue()
        self._thread = None
        self._command = GUIProvider.START
        self._process_stop = False
        self._validate_integer_command = None
        self._validate_float_command = None

    @property
    def view(self):
        """Return controller view."""
        return self._view

    @view.setter
    def view(self, val):
        """Sets controller view."""
        self._view = val
        self._validate_integer_command = self._view.register(BaseController._cb_validate_integer)
        self._validate_float_command = self._view.register(BaseController._cb_validate_float)

    @staticmethod
    def _cb_validate_integer(action, index, value_if_allowed,
                             prior_value, text, validation_type, trigger_type, widget_name):
        # action=1 -> insert
        if action != '1' or value_if_allowed == '+' or value_if_allowed == '-':
            return True

        ret = True
        try:
            int(value_if_allowed)
        except ValueError:
            ret = False

        return ret

    @staticmethod
    def _cb_validate_float(action, index, value_if_allowed,
                           prior_value, text, validation_type, trigger_type, widget_name):
        # action=1 -> insert
        if action != '1' or value_if_allowed == '+' or value_if_allowed == '-':
            return True

        ret = True
        if value_if_allowed is not None:
            index = value_if_allowed.find('e')
            if index == 0:
                return False

            if index > 0:
                try:
                    float(value_if_allowed[:index])
                except ValueError:
                    ret = False

                if ret and index < len(value_if_allowed) - 1:
                    right = value_if_allowed[index + 1:]
                    if right not in ('+', '-'):
                        try:
                            int(right)
                        except ValueError:
                            ret = False

                return ret

        try:
            float(value_if_allowed)
        except ValueError:
            ret = False

        return ret

    @property
    def outputview(self):
        """ return output view """
        return self._outputview

    @outputview.setter
    def outputview(self, outputview):
        """ set output view """
        self._outputview = outputview

    @property
    def model(self):
        """ return model """
        return self._model

    def new_input(self):
        """ load new input data """
        ret = True
        try:
            self.stop()
            self.outputview.clear()
            self._start_button.state(['disabled'])
            self._title.set('')
            self._sections_view.clear()
            self._sections_view.show_add_button(True)
            self._sections_view.show_remove_button(False)
            self._text_view.clear()
            self._sections_view_title.set('')
            self._properties_view.clear()
            self._properties_view.show_remove_button(False)
            self._empty_view.tkraise()

            section_names = self.model.new()
            self._sections_view.populate(section_names)
            self._start_button.state(['!disabled'])
            missing = self.get_sections_names_missing()
            self._sections_view.show_add_button(bool(missing))
        except Exception as ex:  # pylint: disable=broad-except
            self.outputview.clear()
            self.outputview.write_line(str(ex))
            ret = False

        return ret

    def open_file(self, filename):
        """ open file """
        ret = True
        try:
            self.stop()
            self.outputview.clear()
            self._start_button.state(['disabled'])
            self._title.set('')
            self._sections_view.clear()
            self._sections_view.show_add_button(True)
            self._sections_view.show_remove_button(False)
            self._text_view.clear()
            self._sections_view_title.set('')
            self._properties_view.clear()
            self._properties_view.show_remove_button(False)
            self._empty_view.tkraise()
            try:
                self.model.load_file(filename)
            except Exception as ex:  # pylint: disable=broad-except
                messagebox.showerror("Error", str(ex))
                # Only return false if no file or if file not found
                if self.model.get_filename() is None or isinstance(ex, FileNotFoundError):
                    ret = False

            self._title.set(os.path.basename(filename))
            section_names = self.model.get_section_names()
            self._sections_view.populate(section_names)
            self._start_button.state(['!disabled'])
            missing = self.get_sections_names_missing()
            self._sections_view.show_add_button(bool(missing))
        except Exception as ex:  # pylint: disable=broad-except
            self.outputview.clear()
            self.outputview.write_line(str(ex))
            ret = False

        return ret

    def is_empty(self):
        """ check if is empty """
        return self.model.is_empty()

    def save_file(self):
        """ save file """
        filename = self.model.get_filename()
        if not filename:
            self.outputview.write_line("No file to save.")
            return False

        try:
            self.model.save_to_file(filename)
            self.outputview.write_line("Saved file: {}".format(filename))
            return True
        except Exception as ex:  # pylint: disable=broad-except
            messagebox.showerror("Error", str(ex))

        return False

    def save_file_as(self, filename):
        """ save file to a different path """
        try:
            self.model.save_to_file(filename)
            self.open_file(filename)
            return True
        except Exception as ex:  # pylint: disable=broad-except
            messagebox.showerror("Error", str(ex))

        return False

    @abstractmethod
    def cb_section_select(self, section_name):
        """ select section callback """
        pass

    def cb_property_select(self, section_name, property_name):
        """ property selection callback """
        from qiskit.aqua.parser import JSONSchema
        _show_remove = property_name not in (JSONSchema.PROVIDER, JSONSchema.NAME) \
            if section_name == JSONSchema.BACKEND else property_name != JSONSchema.NAME
        self._properties_view.show_remove_button(_show_remove)

    def cb_section_add(self, section_name):
        """ add section callback """
        try:
            if section_name is None:
                section_name = ''
            section_name = section_name.lower().strip()
            if not section_name:
                return False

            self.model.set_section(section_name)
            missing = self.get_sections_names_missing()
            self._sections_view.show_add_button(bool(missing))
        except Exception as ex:  # pylint: disable=broad-except
            messagebox.showerror("Error", str(ex))
            return False

        return True

    def validate_section_add(self, section_name):
        """ validate add section """
        try:
            if section_name in self.model.get_section_names():
                return'Duplicate section name'
        except Exception as ex:  # pylint: disable=broad-except
            return str(ex)

        return None

    def cb_section_remove(self, section_name):
        """ remove section callback """
        try:
            self._sections_view.show_remove_button(False)
            self.model.delete_section(section_name)
            missing = self.get_sections_names_missing()
            self._sections_view.show_add_button(bool(missing))
            self._sections_view_title.set('')
            self._properties_view.clear()
            self._text_view.clear()
            self._empty_view.tkraise()
        except Exception as ex:  # pylint: disable=broad-except
            messagebox.showerror("Error", str(ex))
            return False

        return True

    @abstractmethod
    def cb_section_defaults(self, section_name):
        """ section defaults callback """
        pass

    def get_sections_names_missing(self):
        """ get missing section names """
        try:
            section_names = self.model.get_section_names()
            default_sections = self.model.get_default_sections()
            return list(set(default_sections.keys()) - set(section_names))
        except Exception as ex:  # pylint: disable=broad-except
            self.outputview.write_line(str(ex))

    def get_property_names_missing(self, section_name):
        """ get missing property names """
        try:
            properties = self.model.get_section_properties(section_name)
            default_properties = self.model.get_section_default_properties(
                section_name)
            if default_properties is None:
                return None
            return list(set(default_properties.keys()) - set(properties.keys()))
        except Exception as ex:  # pylint: disable=broad-except
            self.outputview.write_line(str(ex))

    def shows_add_button(self, section_name):
        """ check if it should show add button """
        if self.model.allows_additional_properties(section_name):
            return True

        missing = self.get_property_names_missing(section_name)
        return missing

    def on_property_add(self, section_name, property_name):
        """ property add callback """
        try:
            return self.cb_property_set(section_name,
                                        property_name,
                                        self.model.get_property_default_value(section_name,
                                                                              property_name))
        except Exception as ex:  # pylint: disable=broad-except
            messagebox.showerror("Error", str(ex))

        return False

    @abstractmethod
    def cb_property_set(self, section_name, property_name, value):
        """ property set callback """
        pass

    def validate_property_add(self, section_name, property_name):
        """ validate add property """
        try:
            value = self.model.get_section_property(section_name, property_name)
            if value is not None:
                return 'Duplicate property name'
        except Exception as ex:  # pylint: disable=broad-except
            return str(ex)

        return None

    @abstractmethod
    def cb_section_property_remove(self, section_name, property_name):
        """ section property remove callback """
        pass

    def cb_text_set(self, section_name, value):
        """ set text callback """
        try:
            self.model.set_section_text(section_name, value)
            self._text_view.show_defaults_button(
                not self.model.default_properties_equals_properties(section_name))
        except Exception as ex:  # pylint: disable=broad-except
            self.outputview.write_line(str(ex))
            return False

        return True

    def get_combobox_parameters(self, section_name, property_name):
        """ get combobox parameters """
        from qiskit.aqua.parser import JSONSchema
        values = None
        types = ['string']
        combobox_state = 'readonly'
        if JSONSchema.NAME == property_name and BaseModel.is_pluggable_section(section_name):
            values = self.model.get_pluggable_section_names(section_name)
        elif JSONSchema.BACKEND == section_name and \
                property_name in (JSONSchema.NAME, JSONSchema.PROVIDER):
            values = []
            if JSONSchema.PROVIDER == property_name:
                combobox_state = 'normal'
                for provider, _ in self.model.providers.items():
                    values.append(provider)
            else:
                provider_name = \
                    self.model.get_section_property(JSONSchema.BACKEND, JSONSchema.PROVIDER)
                values = self.model.providers.get(provider_name, [])
        else:
            values = self.model.get_property_default_values(section_name, property_name)
            types = self.model.get_property_types(section_name, property_name)

        return combobox_state, types, values

    def create_popup(self, section_name, property_name, parent, value):
        """ shows popup """
        combobox_state, types, values = self.get_combobox_parameters(section_name, property_name)

        if values is not None:
            widget = ComboboxPopup(self, section_name,
                                   property_name,
                                   parent,
                                   exportselection=0,
                                   state=combobox_state,
                                   values=values)
            widget._text = '' if value is None else str(value)
            if values:
                if value in values:
                    widget.current(values.index(value))
                else:
                    widget.current(0)

            return widget

        value = '' if value is None else value

        if 'object' in types or 'array' in types:
            try:
                if isinstance(value, str):
                    value = value.strip()
                    if value:
                        value = ast.literal_eval(value)

                if isinstance(value, (dict, list)):
                    value = json.dumps(value, sort_keys=True, indent=4)
            except Exception:  # pylint: disable=broad-except
                pass
        elif 'number' in types or 'integer' in types:
            vcmd = self._validate_integer_command if \
                    'integer' in types else self._validate_float_command
            vcmd = (vcmd, '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
            widget = EntryPopup(self,
                                section_name,
                                property_name,
                                parent,
                                value,
                                validate='all',
                                validatecommand=vcmd,
                                state=tk.NORMAL)
            widget.select_all()
            return widget

        widget = TextPopup(self,
                           section_name,
                           property_name,
                           parent,
                           value)
        widget.select_all()
        return widget

    def toggle(self):
        """ toggle between start/stop """
        if self.model.is_empty():
            self.outputview.write_line("Missing Input")
            return

        self._start_button.state(['disabled'])
        self._filemenu.entryconfig(0, state='disabled')
        self._filemenu.entryconfig(1, state='disabled')
        self._filemenu.entryconfig(2, state='disabled')
        self._view.after(100, self._process_thread_queue)
        try:
            if self._command is GUIProvider.START:
                self.outputview.clear()
                self._thread = self._guiprovider.create_run_thread(
                    self.model, self.outputview, self._thread_queue)
                if self._thread is not None:
                    self._thread.daemon = True
                    self._thread.start()
                else:
                    self._thread_queue.put(None)
                    self._start_button.state(['!disabled'])
                    self._filemenu.entryconfig(0, state='normal')
                    self._filemenu.entryconfig(1, state='normal')
                    self._filemenu.entryconfig(2, state='normal')
            else:
                self.stop()
        except Exception as ex:  # pylint: disable=broad-except
            self._thread = None
            self._thread_queue.put(None)
            self.outputview.write_line("Failure: {}".format(str(ex)))
            self._start_button.state(['!disabled'])
            self._filemenu.entryconfig(0, state='normal')
            self._filemenu.entryconfig(1, state='normal')
            self._filemenu.entryconfig(2, state='normal')

    def stop(self):
        """ stop start thread """
        if self._thread is not None:
            stopthread = threading.Thread(target=BaseController._stop,
                                          args=(self._thread,),
                                          name='Stop thread')
            stopthread.daemon = True
            stopthread.start()
            self.outputview.clear_buffer()
            self._thread = None
            self._process_stop = True
            self._thread_queue.put(GUIProvider.STOP)

    @staticmethod
    def _stop(thread):
        try:
            if thread is not None:
                thread.stop()
        except Exception:  # pylint: disable=broad-except
            pass

    def _process_thread_queue(self):
        try:
            line = self._thread_queue.get_nowait()
            if line is None:
                return
            elif line is GUIProvider.START:
                self._progress.start(500)
                self._command = GUIProvider.STOP
                self._button_text.set(self._command)
                self._start_button.state(['!disabled'])
            elif line is GUIProvider.STOP:
                if not self.outputview.buffer_empty():
                    # repost stop
                    self._thread_queue.put(GUIProvider.STOP)
                else:
                    self._thread = None
                    self._progress.stop()
                    self._command = GUIProvider.START
                    self._button_text.set(self._command)
                    self._start_button.state(['!disabled'])
                    self._filemenu.entryconfig(0, state='normal')
                    self._filemenu.entryconfig(1, state='normal')
                    self._filemenu.entryconfig(2, state='normal')
                    if self._process_stop:
                        self._process_stop = False
                        self.outputview.write_line('Process stopped.')
                    return

            self._view.update_idletasks()
        except Exception:  # pylint: disable=broad-except
            pass

        self._view.after(100, self._process_thread_queue)
