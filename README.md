# angr Management

This is the GUI for angr.
Launch it and analyze some binaries!

Some screenshots:

[![Disassembly](https://github.com/angr/angr-management/blob/master/screenshots/disassembly.png)](https://github.com/angr/angr-management/blob/master/screenshots/disassembly.png)
[![Decompilation](https://github.com/angr/angr-management/blob/master/screenshots/decompilation.png)](https://github.com/angr/angr-management/blob/master/screenshots/decompilation.png)

## Installation

### Portable, pre-built executable

The easiest way to run angr-management is by grabbing a bundled release here: https://github.com/angr/angr-management/releases

This binary, built with pyinstaller, can be placed and executed anywhere.

### From PyPI

To install angr-management, use pip:

```
pip install angr-management
```

The version on PyPI may not be up-to-date.
Please consider having a development install if you plan to use latest features/fixes in angr Management.

### Development Install

- Create a virtual environment using virtualenv. Make sure that virtualenv creates a Python 3 environment for you!

```
virtualenv angr-env
cd angr-env
source bin/activate
```

- Clone the Git repository

```
git clone git@github.com:angr/angr-management.git
```

- Install angr Management

```
cd angr-management
pip install -e .
```

## Usage

### How to run

To run angr-management:

```
python -m angrmanagement
```

Or if you have a development install:

```
python start.py
```

### Shortcuts
- Load a new binary: ```Ctrl+O```
- Load a new Docker Image ```Ctrl+Shift+O```
- Save angr database... : ```Ctrl+S```
- Save angr database as... : ```Ctrl+Shift+S```
- Decompile: ```F5```
- Documentation: ```Alt+H```

- Next Tab: ```Ctrl+Tab```
- Previous Tab: ```Ctrl+Shift+Tab```
- Split / Unsplit View: ```Ctrl+D```

## Plugins

Plugins may be installed by placing a subdirectory under `plugins`. The directory must contain an `__init__.py` like that in `TestPlugin`:
```
from .test_plugin import TestPlugin
PLUGIN_CLS_NAME = TestPlugin.__name__
```

This also allows you to import a plugin class from another package entirely. The plugin itself should inherit from `BasePlugin`. Callbacks and events are a work in progress, so the API is subject to change. See `TestPlugin` for an example of a multithreaded plugin sample.

## Issues

### 'module' object has noattribute 'MIPS_GRP_CALL'

Your capstone install does not support functionality that angr-management uses.

To install a version that does (in your angr virtualenv):
```
workon angr
git clone https://github.com/angr/capstone
cd capstone
git checkout next
./make.sh
PACKAGES_PATH=$(python -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")
mkdir -p $PACKAGES_PATH/capstone
cp libcapstone.so.4 $PACKAGES_PATH/capstone/libcapstone.so
cd bindings/python
pip uninstall capstone  # if already installed
python setup.py install
```

