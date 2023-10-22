<!-- markdownlint-disable MD033 MD041 -->

<img
    src="https://kura.pro/kktools/images/logo/kktools.webp"
    alt="KKTools logo"
    width="261"
    align="right" />

<!-- markdownlint-enable MD033 MD041 -->

# kktools

`kktools` is a versatile and comprehensive Python library meticulously crafted for professionals in finance and treasury. It stands out as an indispensable toolkit, aiming to simplify complex financial operations and enhance data analysis precision.

## Key Features

- **Bank Statement Parsing**: Supports multiple formats, including the widely-used CAMT (ISO 20022), ensuring seamless integration with various banking systems.
- **Financial Calculations**: Offers a suite of utilities for accurate and efficient financial calculations, catering to the unique needs of financial analysis.
- **Data Analysis**: Facilitates in-depth analysis of financial data, helping users derive meaningful insights and make informed decisions.
- **User-Friendly CLI**: Comes with a command-line interface, allowing for easy integration into existing workflows and automation of routine tasks.

## Why kktools

- **Tailored for Finance**: Every module and function is designed with the specific requirements of finance and treasury professionals in mind, ensuring relevance and efficacy.
- **Streamlined Operations**: Aims to reduce the complexity of financial data handling, turning cumbersome tasks into straightforward processes.
- **Community-Driven**: Actively developed and supported by a community of finance and treasury specialists, ensuring continuous improvement and adaptation to the industry’s evolving needs.

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

## Command Line Interface (CLI)

`kktools` also provides a command line interface for parsing bank statement files.

### Usage

```bash
python cli.py --type <file_type> --input <input_file> [--output <output_file>]
```

- `--type`: Type of the bank statement file. Currently supported types are "camt" and "pain001".
- `--input`: Path to the bank statement file.
- `--output`: (Optional) Path to save the parsed data. If not provided, data is printed to the console.

### Examples

1. Parse a CAMT file and print the results to the console:

   ```bash
   python cli.py --type camt --input path/to/camt/file.xml
   ```

   Using the test data:

   ```bash
   python ./kktools/cli.py --type camt --input ./tests/test_data/camt.053.001.02.xml
   ```

2. Parse a CAMT file and save the results to a CSV file:

   ```bash
   python cli.py --type camt --input path/to/camt/file.xml --output path/to/output/file.csv
   ```

   Using the test data:

   ```bash
   python ./kktools/cli.py --type camt --input ./tests/test_data/camt.053.001.02.xml --output ./tests/test_data/file.csv
   ```
