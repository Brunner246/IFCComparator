# IFC Comparator

## Overview

IFC Comparator is a Python-based tool designed to compare two IFC (Industry Foundation Classes) files and identify the
differences between them. The tool recursively compares the attributes of elements within the IFC files and outputs the
differences in a JSON file. Inspired
by [IFC Diff](https://academy.ifcopenshell.org/posts/calculate-differences-of-ifc-files-with-hashing/).

## Features

- Compare two IFC files and identify differences in attributes.
- Supports nested structures with floats, lists, and dictionaries.
- Outputs differences in a JSON file.
- Uses fuzzy comparison for numerical values with a specified tolerance.

## Requirements

- Python 3.12+
- `ifcopenshell` library

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/Brunner246/IFCComparator.git
    cd IFCComparator
    ```

2. Create a virtual environment and activate it:
    ```sh
    python -m venv .venv
    .\.venv\Scripts\activate
    ```

3. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

## Usage

To compare two IFC files, run the `main.py` script with the following arguments:

- `-f1` or `--file1_path`: Path to the first IFC file.
- `-f2` or `--file2_path`: Path to the second IFC file.
- `-dir` or `--output_dir`: Directory to save the output JSON file.

Example:

```sh
python .\main.py -f1 .\tests\materialLayer1.ifc -f2 .\tests\materialLayer2.ifc -dir .