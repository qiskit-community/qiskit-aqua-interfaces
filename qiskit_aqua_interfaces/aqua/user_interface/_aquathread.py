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

"""Aqua User Interface run experiment thread"""

import threading
import tempfile
import sys
import logging
import io
import platform
import os
import subprocess
import psutil
from qiskit_aqua_interfaces.user_interface import GUIProvider

logger = logging.getLogger(__name__)


class AquaThread(threading.Thread):
    """ Aqua Thread """
    def __init__(self, model, output, queue) -> None:
        super(AquaThread, self).__init__(name='Aqua run thread')
        self.model = model
        self._output = output
        self._thread_queue = queue
        self._popen = None

    def stop(self):
        """ stop thread """
        self._output = None
        self._thread_queue = None
        if self._popen is not None:
            proc = self._popen
            self._kill(proc.pid)
            proc.stdout.close()

    def _kill(self, proc_pid):
        try:
            process = psutil.Process(proc_pid)
            for proc in process.children(recursive=True):
                proc.kill()
            process.kill()
        except Exception as ex:  # pylint: disable=broad-except
            if self._output is not None:
                self._output.write_line(
                    'Process kill has failed: {}'.format(str(ex)))

    def run(self):
        input_file = None
        temp_input = False
        try:
            algorithms_directory = os.path.dirname(os.path.realpath(__file__))
            algorithms_directory = os.path.abspath(
                os.path.join(algorithms_directory, '../command_line'))
            input_file = self.model.get_filename()
            if input_file is None or self.model.is_modified():
                f_d, input_file = tempfile.mkstemp(suffix='.in')
                os.close(f_d)
                temp_input = True
                self.model.save_to_file(input_file)

            self._popen = subprocess.Popen(['qiskit_aqua_cmd',
                                            algorithms_directory,
                                            input_file],
                                           stdin=subprocess.DEVNULL,
                                           stdout=subprocess.PIPE,
                                           stderr=subprocess.STDOUT,
                                           startupinfo=None)
            if self._thread_queue is not None:
                self._thread_queue.put(GUIProvider.START)

            for line in io.TextIOWrapper(self._popen.stdout, encoding='utf-8', newline=''):
                if self._output is not None:
                    if platform.system() == "Windows":
                        line = line.replace('\r\n', '\n')

                    self._output.write(line)

            self._popen.stdout.close()
            self._popen.wait()
        except Exception as ex:  # pylint: disable=broad-except
            if self._output is not None:
                self._output.write('Process has failed: {}'.format(str(ex)))
        finally:
            self._popen = None
            if self._thread_queue is not None:
                self._thread_queue.put(GUIProvider.STOP)

            if temp_input and input_file is not None:
                os.remove(input_file)

            input_file = None
