<!-- markdownlint-disable MD033 MD041 -->

<img
    src="https://kura.pro/kktools/images/logo/kktools.webp"
    alt="KKTools logo"
    width="261"
    align="right" />

<!-- markdownlint-enable MD033 MD041 -->

# kktools

A comprehensive Python library designed for finance and treasury specialists, `kktools` offers a variety of tools to streamline financial operations and data analysis. This library encompasses modules for parsing bank statements in various formats, utilities for financial calculations, and other essential functionalities commonly used in the realm of finance and treasury.

## Features

- **Bank Statement Parsing**: Parse bank statements in various formats including CAMT and PAIN.
- **Financial Utilities**: Utilize a suite of tools tailored for financial calculations and data processing.

## Installation

To install `kktools`, run the following command:

```bash
pip install kktools
```

## Realized Functionality

### Bank Statement Parsers

- `CamtParser`: Class for parsing CAMT format bank statement files.
- `Pain001Parser`: Class for parsing SEPA PAIN.001 credit transfer files.

## Basic Usage

### Parsing CAMT Files

```python
from kktools import CamtParser

# Initialize the parser with the CAMT file path
camt_parser = CamtParser('path/to/camt/file.xml')

# Parse the file and get the results
results = camt_parser.parse()
```

### Parsing PAIN.001 Files

```python
from kktools import Pain001Parser

# Initialize the parser with the PAIN.001 file path
pain_parser = Pain001Parser('path/to/pain/file.xml')

# Parse the file and get the results
results = pain_parser.parse()
```
