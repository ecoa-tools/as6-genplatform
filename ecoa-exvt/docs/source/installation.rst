.. Copyright 2023 Dassault Aviation
.. MIT License (see LICENSE.txt)

.. _installation:

************
Installation
************

This category aims to explain each step needed to install the EXVT tool.

.. warning::
    In order to succeed the installation of the tool, please verify that those :underline:`prerequisites` are respected:|br|

      * Python 3.8 or higher |br|
      * Pip 21.3 or higher |br|
      * Setuptools 64.0 or higher |br|
      * Unix or Windows 10 environment |br|
      * GCC or MSVC |br|
      * Makefile or MSVC |br|
      * CMake |br|

(Optional) Create and activate the virtual environnement
********************************************************

If needed, at the root of the ECOA tool directory, create and activate the virtual python environnement following those lines:

**Linux**

.. code-block:: bash

    python3 -m venv .venv
    source .venv/bin/activate

**Windows**

.. code-block:: bash

    py -3 -m venv venv
    venv/Scripts/activate.bat

Installation of the tools
*************************

At the root of the ecoa directory, install the following tools:

.. code-block:: bash

    cd ecoa-exvt
    pip install .

EXVT tool is now installed, to see if the installation worked, call the help flag of the tool:

.. code-block:: bash

    ecoa-exvt -h
    (or) ecoa-exvt --help

A block of optional arguments displays. To know more about the usage of the different parameters of the tool, you can read the :ref:`usage<usage>` documentation.

Error output
============

If you obtain this error when installing the tool :

.. code-block:: bash

    ERROR: File "setup.py" not found. Directory cannot be installed in editable mode: /path/to/ecoa-exvt
    (A "pyproject.toml" file was found, but editable mode currently requires a setup.py based build.)

    Solution:
    pip install pip --upgrade
    (On a Dassault host) pip install pip --upgrade -i http://svinfulanxu.dassault-avion.fr:8081/repository/SODA-pypi/simple --trusted-host svinfulanxu.dassault-avion.fr

    pip install setuptools --upgrade
    (On a Dassault host) pip install setuptools --upgrade -i http://svinfulanxu.dassault-avion.fr:8081/repository/SODA-pypi/simple --trusted-host svinfulanxu.dassault-avion.fr

Testing
=======

The tool unit tests can be performed using 'pytest' framework.

**Linux**

.. code-block:: bash

    cd ecoa-exvt
    pytest -sv .
