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

from abc import ABC, abstractmethod
import os
import threading
import queue
import tkinter as tk
from tkinter import messagebox
import logging
from qiskit_aqua_interfaces.aqua.user_interface import GUIProvider

logger = logging.getLogger(__name__)


class BaseController(ABC):
    """Base GUI Controller."""

    @abstractmethod
    def __init__(self, guiprovider, model):
        self._view = None
        self._guiprovider = guiprovider
        self._model = model
        self._filemenu = None
        self._title = tk.StringVar()
        self._sectionsView = None
        self._emptyView = None
        self._sectionView_title = tk.StringVar()
        self._propertiesView = None
        self._textView = None
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
        self._validate_integer_command = self._view.register(BaseController._validate_integer)
        self._validate_float_command = self._view.register(BaseController._validate_float)

    @staticmethod
    def _validate_integer(action, index, value_if_allowed,
                          prior_value, text, validation_type, trigger_type, widget_name):
        # action=1 -> insert
        if action != '1':
            return True

        if value_if_allowed == '+' or value_if_allowed == '-':
            return True

        try:
            int(value_if_allowed)
            return True
        except ValueError:
            return False

    @staticmethod
    def _validate_float(action, index, value_if_allowed,
                        prior_value, text, validation_type, trigger_type, widget_name):
        # action=1 -> insert
        if action != '1':
            return True

        if value_if_allowed == '+' or value_if_allowed == '-':
            return True

        if value_if_allowed is not None:
            index = value_if_allowed.find('e')
            if index == 0:
                return False

            if index > 0:
                try:
                    float(value_if_allowed[:index])
                except ValueError:
                    return False

                if index < len(value_if_allowed) - 1:
                    right = value_if_allowed[index + 1:]
                    if right == '+' or right == '-':
                        return True
                    try:
                        int(right)
                    except ValueError:
                        return False

                return True

        try:
            float(value_if_allowed)
            return True
        except ValueError:
            return False

    @property
    def outputview(self):
        return self._outputview

    @outputview.setter
    def outputview(self, outputview):
        self._outputview = outputview

    @property
    def model(self):
        return self._model

    def new_input(self):
        rc = True
        try:
            self.stop()
            self.outputview.clear()
            self._start_button.state(['disabled'])
            self._title.set('')
            self._sectionsView.clear()
            self._sectionsView.show_add_button(True)
            self._sectionsView.show_remove_button(False)
            self._textView.clear()
            self._sectionView_title.set('')
            self._propertiesView.clear()
            self._propertiesView.show_remove_button(False)
            self._emptyView.tkraise()

            section_names = self.model.new()
            self._sectionsView.populate(section_names)
            self._start_button.state(['!disabled'])
            missing = self.get_sections_names_missing()
            self._sectionsView.show_add_button(True if missing else False)
        except Exception as e:
            self.outputview.clear()
            self.outputview.write_line(str(e))
            rc = False

        return rc

    def open_file(self, filename):
        rc = True
        try:
            self.stop()
            self.outputview.clear()
            self._start_button.state(['disabled'])
            self._title.set('')
            self._sectionsView.clear()
            self._sectionsView.show_add_button(True)
            self._sectionsView.show_remove_button(False)
            self._textView.clear()
            self._sectionView_title.set('')
            self._propertiesView.clear()
            self._propertiesView.show_remove_button(False)
            self._emptyView.tkraise()
            try:
                self.model.load_file(filename)
            except Exception as e:
                self.outputview.clear()
                messagebox.showerror("Error", str(e))
                rc = False

            self._title.set(os.path.basename(filename))
            section_names = self.model.get_section_names()
            self._sectionsView.populate(section_names)
            self._start_button.state(['!disabled'])
            missing = self.get_sections_names_missing()
            self._sectionsView.show_add_button(True if missing else False)
        except Exception as e:
            self.outputview.clear()
            self.outputview.write_line(str(e))
            rc = False

        return rc

    def is_empty(self):
        return self.model.is_empty()

    def save_file(self):
        filename = self.model.get_filename()
        if filename is None or len(filename) == 0:
            self.outputview.write_line("No file to save.")
            return False

        try:
            self.model.save_to_file(filename)
            self.outputview.write_line("Saved file: {}".format(filename))
            return True
        except Exception as e:
            messagebox.showerror("Error", str(e))

        return False

    def save_file_as(self, filename):
        try:
            self.model.save_to_file(filename)
            self.open_file(filename)
            return True
        except Exception as e:
            messagebox.showerror("Error", str(e))

        return False

    @abstractmethod
    def on_section_select(self, section_name):
        pass

    def on_property_select(self, section_name, property_name):
        from qiskit.aqua.parser import JSONSchema
        _show_remove = property_name != JSONSchema.PROVIDER and property_name != JSONSchema.NAME \
            if section_name == JSONSchema.BACKEND else property_name != JSONSchema.NAME
        self._propertiesView.show_remove_button(_show_remove)

    def on_section_add(self, section_name):
        try:
            if section_name is None:
                section_name = ''
            section_name = section_name.lower().strip()
            if len(section_name) == 0:
                return False

            self.model.set_section(section_name)
            missing = self.get_sections_names_missing()
            self._sectionsView.show_add_button(True if missing else False)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return False

        return True

    def validate_section_add(self, section_name):
        try:
            if section_name in self.model.get_section_names():
                return'Duplicate section name'
        except Exception as e:
            return e.message

        return None

    def on_section_remove(self, section_name):
        try:
            self._sectionsView.show_remove_button(False)
            self.model.delete_section(section_name)
            missing = self.get_sections_names_missing()
            self._sectionsView.show_add_button(True if missing else False)
            self._sectionView_title.set('')
            self._propertiesView.clear()
            self._textView.clear()
            self._emptyView.tkraise()
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return False

        return True

    @abstractmethod
    def on_section_defaults(self, section_name):
        pass

    def get_sections_names_missing(self):
        try:
            section_names = self.model.get_section_names()
            default_sections = self.model.get_default_sections()
            return list(set(default_sections.keys()) - set(section_names))
        except Exception as e:
            self.outputview.write_line(str(e))

    def get_property_names_missing(self, section_name):
        try:
            properties = self.model.get_section_properties(section_name)
            default_properties = self.model.get_section_default_properties(
                section_name)
            if default_properties is None:
                return None
            return list(set(default_properties.keys()) - set(properties.keys()))
        except Exception as e:
            self.outputview.write_line(str(e))

    def shows_add_button(self, section_name):
        if self.model.allows_additional_properties(section_name):
            return True

        missing = self.get_property_names_missing(section_name)
        return missing is None or len(missing) > 0

    def on_property_add(self, section_name, property_name):
        try:
            return self.on_property_set(section_name,
                                        property_name,
                                        self.model.get_property_default_value(section_name, property_name))
        except Exception as e:
            messagebox.showerror("Error", str(e))

        return False

    @abstractmethod
    def on_property_set(self, section_name, property_name, value):
        pass

    def validate_property_add(self, section_name, property_name):
        try:
            value = self.model.get_section_property(section_name, property_name)
            if value is not None:
                return 'Duplicate property name'
        except Exception as e:
            return e.message

        return None

    @abstractmethod
    def on_section_property_remove(self, section_name, property_name):
        pass

    def on_text_set(self, section_name, value):
        try:
            self.model.set_section_text(section_name, value)
            self._textView.show_defaults_button(not self.model.default_properties_equals_properties(section_name))
        except Exception as e:
            self.outputview.write_line(str(e))
            return False

        return True

    @abstractmethod
    def create_popup(self, section_name, property_name, parent, value):
        pass

    def toggle(self):
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
                self._thread = self._guiprovider.create_run_thread(self.model, self.outputview, self._thread_queue)
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
        except Exception as e:
            self._thread = None
            self._thread_queue.put(None)
            self.outputview.write_line("Failure: {}".format(str(e)))
            self._start_button.state(['!disabled'])
            self._filemenu.entryconfig(0, state='normal')
            self._filemenu.entryconfig(1, state='normal')
            self._filemenu.entryconfig(2, state='normal')

    def stop(self):
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
        except:
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
        except:
            pass

        self._view.after(100, self._process_thread_queue)
