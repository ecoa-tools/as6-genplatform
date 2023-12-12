.. Copyright 2023 Dassault Aviation
.. MIT License (see LICENSE.txt)

.. _usage:

*****
Usage
*****

This section aims to show how to use the differents options allowed in the tool. The tool must have been installed before, go see the
:ref:`installation<installation>`.

Basic run
#########

To run the EXVT tool:

.. code-block:: bash

    ecoa-exvt -p <path/to/the/ecoa/project/file>

Given paths can be absolute or relative (from the current directory where the user run the tool).

Example
*******

Project PingPong content:
::

  PingPong
  +-- 0-Types
    +-- ECOA.h
    +-- ECOA.hpp
    +-- pingpong.types.xml
  +-- 1-Services
    +-- svc_PingPong.interface.xml
  +-- 2-ComponentDefinitions
    +-- Ping
      +-- Ping.componentType
      +-- Required-svc_PingPong.interface.qos.xml
    +-- Pong
      +-- Pong.componentType
      +-- Required-svc_PingPong.interface.qos.xml
  +-- 3-InitialAssembly
      +-- demo.composite
  +-- 4-ComponentImplementations
    +-- Ping
      +-- myDemoPing.impl.xml
    +-- Pong
      +-- myDemoPong.impl.xml
  +-- 5-Integration
    +-- demo.impl.composite
    +-- deployment.xml
    +-- logical_system.xml
  +-- PingPong.project.xml

In PingPong.project.xml, a relative path in <outputDirectory> is given : "6-Output".

.. code-block:: bash

    ecoa-exvt -p PingPong/PingPong.project.xml

At the end of the command, the tool display the status of the validation.
::

    INFO    |=============== PARSER
    INFO    |parsing file: PingPong/PingPong.project.xml
    INFO    | == Parse libraries
    INFO    |parsing file: PingPong/0-Types/pingpong.types.xml
    INFO    |Library Name: ECOA 0 18
    INFO    |Library Name: pingpong 1 6
    INFO    | == Parse service definitions
    INFO    |parsing file: PingPong/1-Services/svc_PingPong.interface.xml
    INFO    | == Parse component types in
    INFO    |parsing file: PingPong/2-ComponentDefinitions/Ping/Ping.componentType
    INFO    |parsing file: PingPong/2-ComponentDefinitions/Pong/Pong.componentType
    INFO    | == Parse component implementations
    INFO    |parsing file: PingPong/4-ComponentImplementations/myDemoPing/myDemoPing.impl.xml
    INFO    |parsing file: PingPong/4-ComponentImplementations/myDemoPong/myDemoPong.impl.xml
    INFO    | == Parse binary descriptions
    INFO    | == Parse Initial Assembly files
    INFO    |parsing file: PingPong/3-InitialAssembly/demo.composite
    INFO    | == Parse Final Assembly composite files
    INFO    |parsing file: PingPong/5-Integration/demo.impl.composite
    INFO    | == Parse logical system
    INFO    |parsing file: PingPong/5-Integration/cs1.logical-system.xml
    INFO    | == Parse deployment files
    INFO    |parsing file: PingPong/5-Integration/demo.deployment.xml
    INFO    | == Check final assembly 'demo'
    INFO    | == Check component-component_type-component_implementation consistency
    INFO    | == Check wire mapping of logical system 'cs1'
    INFO    | == Parse cross platforms view
    INFO    |No cross platforms view
    INFO    | == Parse EUIDs
    INFO    |=============== Completed


    INFO    |=============== BUILD MODEL
    INFO    |[Ping_PD], reduce number of repository by 0
    INFO    |[Pong_PD], reduce number of repository by 0
    INFO    |=============== Completed


    End with :
     - 0 critcal messages
     - 0 error messages
     - 0 warning messages

Options
#######

Help
****

To display the ECOA version used and the different available options for the tool:

.. code-block:: bash

    ecoa-exvt -h

.. csv-table::
    :name: Help flags
    :header: "Flag", "Description"
    :widths: auto
    :delim: :
    :align: center
    :width: 66%

    "-h, --help":"Displays the optional parameters and the ECOA version of the tool."

Example
=======

Use the command :

.. code-block:: bash

    ecoa-exvt --help

The help option displays the different options and the ECOA version used:

::

    usage: ecoa-exvt [-h] -p PROJECT [-l {0,1,2,3,4,5}] [-v {0,1,2,3,4}]

    Generate ECOA modules. this program validates an ECOA platform described by the project file. ECOA standard version : 6

    optional arguments:
      -h, --help            show this help message and exit
      -p PROJECT, --project PROJECT
                            Path to the ECOA project file
      -l {0,1,2,3,4,5}, --level {0,1,2,3,4,5}
                            ECOA level to validate
      -v {0,1,2,3,4}, --verbose {0,1,2,3,4}
                            Verbosity level: 0 = Critical, 4 = Debug

Project
*******

The project option is **mandatory** and allows the tool to run a desire xml project.

.. code-block:: bash

    ecoa-exvt -p <path/to/the/ecoa/project/file>

.. csv-table::
    :name: Project flag
    :header: "Flag", "Description"
    :widths: auto
    :delim: :
    :align: center
    :width: 66%

    "-p, --project":"The path to the ECOA project file."

Example
=======

Project ECOA content:
::

  PingPong
  +-- 0-Types
  +-- 1-Services
  +-- 2-ComponentDefinitions
  +-- 3-InitialAssembly
  +-- 4-ComponentImplementations
  +-- 5-Integration
  +-- PingPong.project.xml

In PingPong.project.xml, a relative path in <outputDirectory> is given : "6-Output".

.. code-block:: bash

    ecoa-exvt -p PingPong/PingPong.project.xml

At the end of the command, the tool display the status of the validation.
::

    INFO    |=============== PARSER
    INFO    |parsing file: PingPong/PingPong.project.xml
    INFO    | == Parse libraries
    INFO    |parsing file: PingPong/0-Types/pingpong.types.xml
    INFO    |Library Name: ECOA 0 18
    INFO    |Library Name: pingpong 1 6
    INFO    | == Parse service definitions
    INFO    |parsing file: PingPong/1-Services/svc_PingPong.interface.xml
    INFO    | == Parse component types in
    INFO    |parsing file: PingPong/2-ComponentDefinitions/Ping/Ping.componentType
    INFO    |parsing file: PingPong/2-ComponentDefinitions/Pong/Pong.componentType
    INFO    | == Parse component implementations
    INFO    |parsing file: PingPong/4-ComponentImplementations/myDemoPing/myDemoPing.impl.xml
    INFO    |parsing file: PingPong/4-ComponentImplementations/myDemoPong/myDemoPong.impl.xml
    INFO    | == Parse binary descriptions
    INFO    | == Parse Initial Assembly files
    INFO    |parsing file: PingPong/3-InitialAssembly/demo.composite
    INFO    | == Parse Final Assembly composite files
    INFO    |parsing file: PingPong/5-Integration/demo.impl.composite
    INFO    | == Parse logical system
    INFO    |parsing file: PingPong/5-Integration/cs1.logical-system.xml
    INFO    | == Parse deployment files
    INFO    |parsing file: PingPong/5-Integration/demo.deployment.xml
    INFO    | == Check final assembly 'demo'
    INFO    | == Check component-component_type-component_implementation consistency
    INFO    | == Check wire mapping of logical system 'cs1'
    INFO    | == Parse cross platforms view
    INFO    |No cross platforms view
    INFO    | == Parse EUIDs
    INFO    |=============== Completed


    INFO    |=============== BUILD MODEL
    INFO    |[Ping_PD], reduce number of repository by 0
    INFO    |[Pong_PD], reduce number of repository by 0
    INFO    |=============== Completed


    End with :
     - 0 critcal messages
     - 0 error messages
     - 0 warning messages

Validation Level
****************

The validation level option allows to validate a partial description of an ECOA project until the specified level, considering the ECOA working tree structure (0-Types, 1-Services, 2-ComponentDefinitions, 3-InitialAssembly, 4-ComponentImplementations, 5-Integration).

.. code-block:: bash

    ecoa-exvt -p <path/to/the/ecoa/project/file> -l <level>

.. csv-table::
    :name: Log flags
    :header: "Flag", "Description"
    :widths: auto
    :delim: :
    :align: center
    :width: 66%

    "-l, --level":"Validates the ECOA project until the specified level."

Specific parameters can be combined with -l flag :

.. csv-table::
    :name: Level Parameters
    :header: "Parameters", "Description"
    :widths: auto
    :delim: :
    :align: center
    :width: 66%

    "0":"Validates files in 0-Types directory."
    "1":"Validates files in 1-Services directory and 'lower' directories."
    "2":"Validates files in 2-ComponentDefinitions directory and 'lower' directories."
    "3":"Validates files in 3-InitialAssembly directory and 'lower' directories."
    "4":"Validates files in 4-ComponentImplementations directory and 'lower' directories."
    "5":"Validates files in 5-Integration directory and 'lower' directories (default)."

Example
=======

Project ECOA content:
::

  PingPong
  +-- 0-Types
  +-- 1-Services
  +-- 2-ComponentDefinitions
  +-- 3-InitialAssembly
  +-- 4-ComponentImplementations
  +-- 5-Integration
  +-- PingPong.project.xml

When running the tool with the level 3, files are only validated until the 3-InitialAssembly directory.

.. code-block:: bash

    ecoa-exvt -p Pingpong/PingPong.project.xml -l 3

At the end of the command, the tool display the status of the validation until the level 3.

.. code-block:: bash

    INFO    |=============== PARSER
    INFO    |parsing file: PingPong/PingPong.project.xml
    INFO    | == Parse libraries
    INFO    |parsing file: PingPong/0-Types/pingpong.types.xml
    INFO    |Library Name: ECOA 0 18
    INFO    |Library Name: pingpong 1 6
    INFO    | == Parse service definitions
    INFO    |parsing file: PingPong/1-Services/svc_PingPong.interface.xml
    INFO    | == Parse component types in
    INFO    |parsing file: PingPong/2-ComponentDefinitions/Ping/Ping.componentType
    INFO    |parsing file: PingPong/2-ComponentDefinitions/Pong/Pong.componentType
    INFO    | == Parse Initial Assembly files
    INFO    |parsing file: PingPong/3-InitialAssembly/demo.composite
    INFO    |=============== Completed


    End with :
     - 0 critcal messages
     - 0 error messages
     - 0 warning messages

Verbose
*******

The verbose option displays more detailled information when the tool is running.

.. code-block:: bash

    ecoa-exvt -p <path/to/the/ecoa/project/file> -v <verbose level>

.. csv-table::
    :name: Verbose flags
    :header: "Flag", "Description"
    :widths: auto
    :delim: :
    :align: center
    :width: 66%

    "-v, --verbose":"Displays informations according to the verbose level during ECOA project validation."

Specific parameters can be combined with -v flag :

.. csv-table::
    :name: Verbose Parameters
    :header: "Parameters", "Description"
    :widths: auto
    :delim: :
    :align: center
    :width: 66%

    "0":"CRITICAL"
    "1":"ERROR"
    "2":"WARNING"
    "3":"INFO"
    "4":"DEBUG"

Example
=======

Project ECOA content:
::

  PingPong
  +-- 0-Types
  +-- 1-Services
  +-- 2-ComponentDefinitions
  +-- 3-InitialAssembly
  +-- 4-ComponentImplementations
  +-- 5-Integration
  +-- PingPong.project.xml

When running the tool with the verbose options, the informations are displayed until DEBUG level.

.. code-block:: bash

    ecoa-exvt -p PingPong/PingPong.project.xml -v 4

At the end of the command, the tool display the status of the validation.

.. code-block:: bash

    INFO    |=============== PARSER
    INFO    |parsing file: PingPong/PingPong.project.xml
    INFO    | == Parse libraries
    INFO    |parsing file: PingPong/0-Types/pingpong.types.xml
    INFO    |Library Name: ECOA 0 18
    INFO    |Library Name: pingpong 1 6
    INFO    | == Parse service definitions
    INFO    |parsing file: PingPong/1-Services/svc_PingPong.interface.xml
    DEBUG   |Service Name: svc_PingPong 0 1 4
    INFO    | == Parse component types in
    INFO    |parsing file: PingPong/2-ComponentDefinitions/Ping/Ping.componentType
    INFO    |parsing file: PingPong/2-ComponentDefinitions/Pong/Pong.componentType
    DEBUG   |Component type: Ping
      services:[]
      references: [<ecoa.models.component_type.Service_Instance object at 0x7f499883a880>]
      properties: []

    DEBUG   |Name: Ping 0 0 1
    DEBUG   |Component type: Pong
      services:[<ecoa.models.component_type.Service_Instance object at 0x7f499883a700>]
      references: []
      properties: []

    DEBUG   |Name: Pong 1 1 0
    INFO    | == Parse component implementations
    INFO    |parsing file: PingPong/4-ComponentImplementations/myDemoPing/myDemoPing.impl.xml
    DEBUG   |WCET for myDemoPing_AM_I.behaviour.xml : 0
    DEBUG   |WCET for Heart_Beat.behaviour.xml : 0
    INFO    |parsing file: PingPong/4-ComponentImplementations/myDemoPong/myDemoPong.impl.xml
    DEBUG   |WCET for myDemoPong_AM_I.behaviour.xml : 0
    INFO    | == Parse binary descriptions
    INFO    | == Parse Initial Assembly files
    INFO    |parsing file: PingPong/3-InitialAssembly/demo.composite
    DEBUG   |Composite properties:
    DEBUG   |Component: demoPing
      services: []
      references: ['svc_PingPong']
      properties: []

    DEBUG   |Name: demoPing 0 (Ping) 0 1
    DEBUG   |Component: demoPong
      services: ['svc_PingPong']
      references: []
      properties: []

    DEBUG   |Name: demoPong 1 (Pong) 1 0
    DEBUG   |Wire demoPing/svc_PingPong => demoPong/svc_PingPong
    INFO    | == Parse Final Assembly composite files
    INFO    |parsing file: PingPong/5-Integration/demo.impl.composite
    DEBUG   |Composite properties:
    DEBUG   |Component: demoPing
      services: []
      references: ['svc_PingPong']
      properties: []

    DEBUG   |Name: demoPing 2 (Ping) 0 1
    DEBUG   |Component: demoPong
      services: ['svc_PingPong']
      references: []
      properties: []

    DEBUG   |Name: demoPong 3 (Pong) 1 0
    DEBUG   |Wire demoPing/svc_PingPong => demoPong/svc_PingPong
    INFO    | == Parse logical system
    INFO    |parsing file: PingPong/5-Integration/cs1.logical-system.xml
    DEBUG   |Name: machine0 0 4 147376 10
    DEBUG   |Platform: myPlatform 0 4 147376 10
    INFO    | == Parse deployment files
    INFO    |parsing file: PingPong/5-Integration/demo.deployment.xml
    INFO    | == Check final assembly 'demo'
    INFO    | == Check component-component_type-component_implementation consistency
    INFO    | == Check wire mapping of logical system 'cs1'
    INFO    | == Parse cross platforms view
    INFO    |No cross platforms view
    INFO    | == Parse EUIDs
    INFO    | == Parse IP deployment files
    INFO    |parsing file: PingPong/5-Integration/ip_address_deployment.xml
    INFO    |=============== Completed


    INFO    |=============== BUILD MODEL
    INFO    |[Ping_PD], reduce number of repository by 0
    DEBUG   |VD repo. index: 0, num_reader: 0
      0 extern sockets
      0 local repo with index : []
      1 comp impl VD :
       demoPing
        notified mod: []
        local socket: []


    INFO    |[Pong_PD], reduce number of repository by 0
    DEBUG   |VD repo. index: 0, num_reader: 1
      0 extern sockets
      0 local repo with index : []
      1 comp impl VD :
       demoPong
        notified mod: []
        local socket: ['svc_PingPong']


    INFO    |=============== Completed


    End with :
     - 0 critcal messages
     - 0 error messages
     - 0 warning messages
