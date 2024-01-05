# Spacemesh Rewards Export Script

## Overview
This script is designed to export Spacemesh crypto transactions, specifically rewards, into a CSV format for use with Excel or with tax software. It queries a full Spacemesh node's SQLite database for transaction data and supports different CSV output formats. The script is self-contained, with no external dependencies, and does not require a virtual environment.

## Features
- Fetches reward transactions from a Spacemesh `state.sql` database.
- Converts transactions into CSV format.
- Supports different CSV formats: `tokentax`, `cointracker`, and `generic` (default).
- Customizable to include transactions within a specified date range.
- Command-line interface for easy use and integration.

## Requirements
- Python 3.x
- Access to Spacemesh's `state.sql` SQLite database file.

## Usage

### Command Line Arguments
- `coinbase`: Coinbase address in bech32 format (required).
- `--start_date`: Start date (inclusive), in `YYYY-MM-DD` format (optional).
- `--end_date`: End date (inclusive), in `YYYY-MM-DD` format (optional).
- `--db_path`: Path to the SQLite database file (required).
- `--output_file`: Path to output CSV file. If not specified, outputs to `stdout` (optional).
- `--csv_format`: Format of the CSV file, `cointracker`, `tokentax` or `generic`. Default is `generic` (optional).

### Examples

#### Windows
```sh
python script.py sm1qv... --db_path "C:\Users\[YourUsername]\AppData\Roaming\Spacemesh\node-data\7c8cef2b\state.sql" --output_file "C:\path\to\output.csv"
```

#### Linux
```sh
python3 script.py sm1qv... --db_path ~/.spacemesh/node-data/7c8cef2b/state.sql --output_file /path/to/output.csv
```

#### MacOS
```sh
python3 script.py sm1qv... --db_path ~/Library/Application\ Support/Spacemesh/node-data/7c8cef2b/state.sql --output_file /path/to/output.csv
```

Replace `sm1qv...` with your actual coinbase address in bech32 format. Adjust the `--db_path` and `--output_file` paths based on your system and preferences.

## Output Formats
- `generic`: Simplified format with only Layer, RewardAmount, and Date columns. This is the default.
- `tokentax`: This format can be parsed automatically by TokenTax.
- `cointracker`: This format can be parsed automatically by CoinTracker.

To select a format, use the `--csv_format` argument, for example, `--csv_format tokentax`.

## Notes
- Ensure that the path to the `state.sql` file is correct and accessible.
- The script's behavior and paths may vary based on the Spacemesh version and system configuration.

## License
This code is released under the MIT license. See the `LICENSE` file for details.