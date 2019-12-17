# Qiskit Aqua Interfaces
**Qiskit** is an open-source framework for working with noisy quantum computers at the level of pulses, circuits, and algorithms.

## Note
This project is currently deprecated and it will stop working after Qiskit Aqua 0.7.0

## Note
As of July 12, 2019 Qiskit Chemistry has been merged into Qiskit Aqua, and all the code of the
[Qiskit Chemistry repository](https://github.com/Qiskit/qiskit-chemistry)
has been integrated into the [Qiskit Aqua](https://github.com/Qiskit/qiskit-aqua) repository.  This change has impacted the
dependencies of [Qiskit Aqua Intefaces](https://github.com/Qiskit/qiskit-aqua-interfaces).  Follow the instructions in the
[Qiskit Chemistry README file](https://github.com/Qiskit/qiskit-chemistry/blob/master/README.md) to update your installation of
Qiskit Aqua and Qiskit Aqua Interfaces.

## Overview

Qiskit is made up elements that work together to enable quantum computing. This repository contains **Qiskit Aqua Interfaces**,
a set of user-interface components for [Qiskit Aqua](https://github.com/Qiskit/qiskit-aqua) (the element of Qiskit consisting
of a library of cross-domain algorithms upon which domain-specific applications can be
built) and Qiskit Chemistry (the chemistry-application component of Qiskit Aqua).

The following user interfaces are currently included in this repository:
1. A command-line interface for Qiskit Aqua
2. A command-line interface for Qiskit Chemistry
3. A Qiskit Chemistry Graphical User Interface (GUI) wizard
4. A Qiskit Aqua GUI wizard
5. A visual browser for the Qiskit Aqua and Qiskit Chemistry Application Programming Interfaces (APIs)

The command-line and wizards listed above include the following characteristics:
- Through the command-line and wizard interfaces, the user can execute Qiskit Aqua or Qiskit Chemistry as tools.  These
interfaces allow the user to configure an experiment and execute it on top of one of the simulators or quantum computers
interfaced by Qiskit.
- The command-line and wizard interfaces embed a schema-based configuration-correctness enforcement mechanism that
minimizes the chances for a user to make a configuration mistake, especially for experiments that mix domain- and
quantum-specific information.
- The command-line and wizard interfaces allow for configuration data and algorithm inputs to be serialized and deserialized
at different stages.  For example, Chemistry-specific information extracted from the classical computational-chemistry
software packages interfaced by Aqua can be serialized in the [HDF5](https://www.hdfgroup.org/) binary format and later
deserialized for faster experiment execution.  This also allows experiment inputs to be shared among quantum researchers,
thereby taking away the dependency from the particular classical computational-chemistry software package used to generate
those inputs.  Similarly, the input to a quantum algorithm can be serialized in [JSON](http://json.org/) format and later
deserialized, thereby allowing a quantum experiment to be executed at the algorithmic level, without any dependency on the
particular domain in which that input was generated.
- Finally, the wizard interfaces allow for automatically generating a Python dictionary summarizing an entire experiment.
Later on, that dictionary can be used as an input to the Qiskit Aqua or Qiskit Chemistry declarative API.
