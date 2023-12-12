===============
Platform tools
===============

This package contains 3 tools to generate external files that are not requiered by ECOA standard:
- compare types functions
- initialize types functions
- encapsulation functions for module container operations

-------------
generator
-------------
This diretory contains python script to generate these files.
**Currently, only C files are generated. CPP is not yet supported**

### Pattern Parser

The parsing of these files is done in `generator/pattern_files_parser.py`

#### Types functions
For types functions, it is possible to specify prefix and suffix of function names in `0-types/pattern/#LIB#_pattern_comp.txt` and `0-types/pattern/#LIB#_pattern_init.txt`. The parsing will find prefix, suffix and epsilon (for float number precision) and save it in library python object.

#### Encapsulation functions
It is possible to describe prefix of function names in `4-ComponentsImplementations/pattern/#COMPONENT#_encaps.txt`. This file is parse by the function `parse_component_pattern_file`.

It is also possible to write some function for each module in file `4-ComponentsImplementations/#COMP#/#MODULE#_pattern.c` and `4-ComponentsImplementations/#COMP#/#MODULE#_pattern.h`. To parse correctly theses module pattern files, use the function  `parse_module_pattern_file`. After parsing, implementation of functions are saved in a dictionary and are retrieved with the macro used to define it.

For more details about pattern files see documents in ```docs/```.


### type_function_generators.py
This file contains functions to generate types functions in C (and in CPP?), It contains 2 functions:
- generate_compare_types
- generate_zeroise_types

### encapsulation_functions_generator.py
For each module implementations in each component implementation:
- use prefix if defined
- If a pattern files is defined for a module, fill pattern dictionary
- generated encapsulation functions using pattern defined in dictionary or default implementation. The default implementation are defined in `C/tempaltes directory`

for user code section, the function prototypes to write in header file are read in pattern file header. If the file does not exist, the default code is written.

### usage
#### Compare functions
Require `Libraries` dictionary. The code below will generate compare functions files and overwrite existing files.
```
parse_type_pattern_files(types_directory, libraries_dict)
generate_compare_types(types_directory, libraries_dict, True)
```

#### Initialize functions
Require `Libraries` dictionary. The code below generates initialize function files and overwrites existing files.
```
parse_type_pattern_files(types_directory, libraries_dict)
generate_zeroise_types(types_directory, libraries_dict, True)
```

#### Encapsulation functions
Require 'Component_Implementations' dictionary. The function below parses files and generates or overwrites function files.
```
encaps_functions_generate(implementation_directory, component_implementations)
```

#### Exemple
The script below generates:
 - standart ECOA files to run platform
 - tool files for comparision and initialised types functions
 - tool files for encapsulated functions of module containers

```
import os,sys
from ecoa.utilities.genplatform_arguments import parse_args
from ecoa.ecoa_global_config import ECOA_Global_Config

from dev_tools.generator.pattern_files_parser import parse_type_pattern_files
from dev_tools.generator.type_functions_generator import generate_compare_types,  generate_zeroise_types
from dev_tools.generator.encapsulation_functions_generator import encaps_functions_generate

## Standart script to generate a platform
arguments = parse_args()
working_directory= os.path.dirname(os.path.abspath(arguments.config[0]))+"/"
xsd_directory = os.path.dirname(os.path.abspath(sys.argv[0]))+"/Extras"
file_log_dir = "logs"

Global_ECOA = ECOA_Global_Config(working_directory, arguments.config[0], arguments.verbose)

if not Global_ECOA.do_parsing(xsd_directory):
	Global_ECOA.end()
	sys.exit(-1)

if not Global_ECOA.build_model():
	Global_ECOA.end()
	sys.exit(-1)

Global_ECOA.set_instance_index(arguments.instance_index)
if not Global_ECOA.generate(file_log_dir, arguments.force):
	Global_ECOA.end()
	sys.exit(-1)

## Generate tools files
parse_type_pattern_files(Global_ECOA.types_output_dir, Global_ECOA.libraries)
generate_compare_types(Global_ECOA.types_output_dir, Global_ECOA.libraries, True)
generate_zeroise_types(Global_ECOA.types_output_dir, Global_ECOA.libraries, True)
encaps_functions_generate("", Global_ECOA.component_implementations, True)

## ending
Global_ECOA.end()
```

To run this script, the command line need a configuration files (see README.md of ```parsec/``` for more details):
```python3 path_to/script_name.py ldp path_to/config-exemple.xml```


### Limite(s)
In module pattern files, it is not recommanded to use comment on 1 ligne like : `/** comments **/`.

### Float comparaison
They are 2 ways to compare float numbers:
 - absolute methode : using the `precision` attribute of simple type in ECOA xml file.
```abs(a-b) < precision;```
 - relative methode : using `epsilon` value in library pattern file.
```
abs(a-b) < precision * abs(a); // a != 0 and b != 0
abs(a-b) < precision; // a == 0 or b == 0
```
If neither precision nor epsilon exists for a type, the absolute methode is used with precision = 0.0


-------------
Test scripts
-------------
They are 3 tests in `script_tests_tools/`:
 - Test_GeneComp: Test generation of compare types functions
 - Test_GeneInit: Test generation of initialized types functions
 - Test_GeneEncaps: Test generation of encapsulation of container module functions. Test also the execution of these functions thanks to an executable platform.
 **WARNING**: to run this platform, it is necessary to set the cmake configuration files and the cmake command :
Usage of Test_GeneEncaps.py:
```
python3 Test_GeneEncaps.py path_to_cmake_file.config 3 // to run cmake3
python3 Test_GeneEncaps.py path_to_cmake_file.config   // to run cmake
```


To run these 3 tests, use ```test_runner.py```. it is also necessary to set the cmake configuration files and cmake command:
```
python3 Path_to_script/test_runner.py -c path_to_cmake_file.config -n 3 // to run cmake3
python3 Path_to_script/test_runner.py -c path_to_cmake_file.config      // to run cmake
```
Possible option:
- `-h`: display help
- `-c <file>`: cmake config file
- `-n <number>`: [optional] cmake version to use : `cmake<number>`. By default: `cmake`,

This script will run tests and generate log files in ```Path_to_script/logs/```:
 - GeneComp.log
 - GeneInit.log
 - GeneEncaps.log

Tests can be run one by one. A log file is also generated in ```Path_to_script/logs/```

If test passed, generated files are removed.

