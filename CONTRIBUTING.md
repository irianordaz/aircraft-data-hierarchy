# Contributing

We welcome contributions! Here is a brief guide on the process:

1. Fork/clone the repository.
2. Create a new branch (git checkout -b feature-branch).
3. Make your changes and commit them (git commit -m 'Add some feature').
4. Push to the branch (git push origin feature-branch).
5. Open a [pull request.](https://github.com/Boeing/aircraft-data-hierarchy/pulls)


# Getting Started as a Developer

## Cloning the Aircraft Data Hierarchy Repository

The sections [Setting Up The Python Environment](#setting-up-the-python-environment), [Building The Aircraft Data Hierarchy Package](#building-the-aircraft-data-hierarchy-package), and [Testing](#testing) assume you have a local copy of the Aircraft Data Hierarchy repository. Begin by cloning the latest version of the package: 

```shell
git clone https://github.com/Boeing/aircraft-data-hierarchy
```

By default, the cloned project folder created will be named `aircraft-data-hierarchy`

## Setting Up The Python Environment

To ensure a clean and isolated environment for running the Aircraft Data Hierarchy package, we recommend you create a new Anaconda environment. If you wish to skip creating an Anaconda environment continue to [Step 5](#5-install-the-required-packages) of this section.

### 1. Open a command or Anaconda Prompt.

### 2. Create a new Anaconda environment:

```shell
conda create -n your-environment-name
```

Replacing `your-environment-name` with the desired name for your environment. 

### 3. Activate the new environment:

```shell
conda activate your-environment-name
```

### 4. Navigate to the project directory:

```shell
cd aircraft-data-hierarchy
```

### 5. Install the required packages.

In some cases `pip` will not be automatically installed when creating the new environment. If that is the case for you, install `pip` using conda.

```shell
conda install pip
```

Once you have `pip`, install the package dependencies specified in the [pyproject.toml](pyproject.toml) file.

```shell
pip install .[dependencies]
```

This will install all the dependencies specified for the Aircraft Data Hierarchy package.

## Building The Aircraft Data Hierarchy Package

To get started with the Aircraft Data Hierarchy package, follow these steps:

### 1. Navigate to the project directory:

```shell
cd aircraft-data-hierarchy
```

### 2. Build the package using Python build:

```shell
python -m build
```

This will create a `dist` directory containing the built distribution files.

### 3. Install the package using `pip`:

```shell
pip install dist/your-package-name-<version>.whl
```

Replace <version> with the actual version number of the package wheel file from [Step 2](#2-build-the-package-using-python-build).

### 4. Now you can import and use the Aircraft Data Hierarchy package in your Python code:

```python
from aircraft_data_hierarchy.common_base_model import Metadata, CommonBaseModel
```

## Testing

You are encouraged to run the unit tests to ensure the Aircraft Data Hierarchy package is working correctly. Use the following steps to run the tests:

### 1. Navigate to the cloned project directory:

```shell
cd aircraft-data-hierarchy
```

### 2. Install the required testing packages:

Test dependencies are specified in the [pyproject.yml](pyproject.toml) file.

```shell
pip install .[test]
```
 
### 3. Run tests

```shell
pytest
```

This command will automatically discover and run all the tests in the project directory.

### 4. Review the test results

The pytest framework will provide detailed information about the tests that passed or failed. If the Aircraft Data Hierarchy package was installed correctly and everything works, you should see all tests pass.

