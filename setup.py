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

import setuptools
import os

long_description = """Qiskit Aqua Interfaces, a set of user-interface components for
 <a href="https://github.com/Qiskit/qiskit-aqua" rel=nofollow>Qiskit Aqua</a>."""

requirements = [
    "qiskit-aqua>=0.6.0,<0.7.0",
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
    url='https://github.com/Qiskit/qiskit_aqua_interfaces',
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
        "Programming Language :: Python :: 3.7",
        "Topic :: Scientific/Engineering"
    ),
    keywords='qiskit sdk quantum aqua',
    packages=setuptools.find_packages(exclude=['test*']),
    install_requires=requirements,
    include_package_data=True,
    python_requires=">=3.5",
    entry_points={
        'console_scripts': [
                'qiskit_aqua_cmd=qiskit_aqua_interfaces.aqua.command_line.command_line:main',
                'qiskit_chemistry_cmd=qiskit_aqua_interfaces.chemistry.command_line.command_line:main'
        ],
        'gui_scripts': [
                'qiskit_aqua_ui=qiskit_aqua_interfaces.aqua.user_interface.command_line:main',
                'qiskit_aqua_browser=qiskit_aqua_interfaces.aqua.browser.command_line:main',
                'qiskit_chemistry_ui=qiskit_aqua_interfaces.chemistry.user_interface.command_line:main'
        ]
    }
)
