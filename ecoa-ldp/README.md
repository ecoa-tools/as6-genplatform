# ecoa-ldp

The Lightweight Development Platform tool (`LDP`) allows to generate the source code of an ECOA application.

Documentation about the architecture, requirements and more are available in the [docs](./docs) directory.

The Lightweight Development Platform tool (`LDP`) is provided “as is”, without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose and noninfringement. In no event shall the authors or copyright holders be liable for any claim, damages or other liability, whether in an action of contract, tort or otherwise, arising from, out of or in connection with the software or the use or other dealings in the software. The Lightweight Development Platform tool (`LDP`) and its outputs are not claimed to be fit or safe for any purpose. Any user should satisfy themselves that this software or its outputs are appropriate for its intended purpose.

This software is MIT licensed : see file LICENSE.txt.

Copyright 2023 Dassault Aviation

## Structure

    .
    +-- CHANGELOG.md             # Changelog
    +-- conftest.py              # Configuration file for functional tests
    +-- docs                     # Documentation
        +-- source               # Sphinx documentation
        +-- TOR                  # Tool Operational Requirements
        +-- UM                   # User Manual
        +-- VDD                  # Version Description Document
    +-- LICENSE.txt              # License
    +-- MANIFEST.in              # Package distribution file
    +-- pyproject.toml           # Package configuration file
    +-- README.md
    +-- src                      # Source code
        +-- ecoa_genplatform     # Actual package
        +-- ecoa_tools           # Utilities
    +-- tests                    # Functional tests

## Prerequisites

* Python 3.8 or higher
* Pip 21.3 or higher
* Setuptools 64.0 or higher
* Unix
* GCC
* Makefile
* CMake

## Installation

From the Git repository :

```sh
pip install -e .
```

From a Python packages repository :

```sh
pip install ecoa-ldp
```

with the following options: `--no-build-isolation --no-deps` in the command line or in the `pip.conf` file.

## Usage

```sh
ecoa-ldp -p <path/to/the/ecoa/project/file>
```

Check out the [docs](./docs) for full usage.
