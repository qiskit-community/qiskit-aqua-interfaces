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

import setuptools
import os

long_description = """Qiskit Aqua Interfaces, a set of user-interface components for
 <a href="https://github.com/Qiskit/qiskit-aqua" rel=nofollow>Qiskit Aqua</a> and
 <a href="https://github.com/Qiskit/qiskit-chemistry" rel=nofollow>Qiskit Chemistry</a>."""

requirements = [
    "qiskit-aqua>=0.5.0",
    "pyobjc-core; sys_platform == 'darwin'",
    "pyobjc-framework-Cocoa; sys_platform == 'darwin'"
]

VERSION_PATH = os.path.join(os.path.dirname(__file__), "qiskit_aqua_interfaces", "VERSION.txt")
with open(VERSION_PATH, "r") as version_file:
    VERSION = version_file.read().strip()

setuptools.setup(
    name='qiskit-aqua-interfaces',
    version=VERSION,
    description='Qiskit Aqua Interfaces',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/Qiskit/qiskit-aqua-uis',
    author='Qiskit Aqua Development Team',
    author_email='qiskit@us.ibm.com',
    license='Apache-2.0',
    classifiers=(
        "Environment :: Console",
        "License :: OSI Approved :: Apache Software License",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Topic :: Scientific/Engineering"
    ),
    keywords='qiskit sdk quantum aqua',
    packages=setuptools.find_packages(exclude=['test*']),
    install_requires=requirements,
    include_package_data=True,
    python_requires=">=3.5",
    extras_require={
        'qiskit_chemistry': ['qiskit-chemistry>=0.5.0']
    },
    entry_points={
        'console_scripts': [
                'qiskit_aqua_cmd=qiskit_aqua_interfaces.aqua.command_line.command_line:main',
                'qiskit_chemistry_cmd=qiskit_aqua_interfaces.chemistry.command_line.command_line:main [qiskit_chemistry]'
        ],
        'gui_scripts': [
                'qiskit_aqua_ui=qiskit_aqua_interfaces.aqua.user_interface.command_line:main',
                'qiskit_aqua_browser=qiskit_aqua_interfaces.aqua.browser.command_line:main',
                'qiskit_chemistry_ui=qiskit_aqua_interfaces.chemistry.user_interface.command_line:main [qiskit_chemistry]'
        ]
    }
)
