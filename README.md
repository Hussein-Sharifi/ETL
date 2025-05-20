# Automated Financial Data ETL Pipeline

Built a modular ETL pipeline that automates the extraction and processing of historical stock prices and company financial statements (income, balance sheet, and cash flow) using a public API. The pipeline computes key financial indicators, organized into profitability, leverage, and liquidity categories, in PostgreSQL. All raw and processed data, including calculated metrics, are stored in PostgreSQL tables and exported as CSV files for external use or downstream analysis.

- Data Source: All financial data is collected from the Financial Modelling Prep (FMP) API, which aggregates filings from the U.S. SEC.

- Indicators: Financial indicators are computed in SQL using standardized formulas (see Indicator Formulas, in progress).

- Export Format: Processed data is output in a tidy long format, structured for compatibility with Power BI dashboards or other analytical tools.

- Data Traceability: Each financial statement entry includes a reference to the original SEC filing via the finalLink field, enabling manual verification of reported figures.

- Automation: the ETL script is designed to allow updating stock/statement data using scheduled tasks. This allows user to update dashboards with new data automatically. (in progress)

---

## Table of Contents

1. [Project Structure](#project-structure)  
2. [Getting Started](#getting-started)  
   1. [Using Conda (Recommended)](#using-conda-recommended)  
   2. [Without Conda (Using pip)](#without-conda-using-pip)  
   3. [Configuration](#configuration)  
   4. [Running the ETL Script](#running-the-etl-script)  
   5. [Extract and Transform (Optional)](#extract-and-transform-optional)  
3. [License & Data Usage](#license--data-usage)

---

## Project Structure

```
Project_Root
│   .gitignore
│   environment.yml
│   README.md
│
├───config
│       default_endpoints.json
│       example_env.txt
│
├───data
│   ├───processed
│   └───raw
│
├───outputs
│   
├───scripts
│       config.py
│       extract.py
│       FA_io.py
│       fmp_client.py
│       parser.py
│       sql_transforms.py
│       sql_utils.py
│       transform.py
│       utils.py
│       ETL.py
│
└───tests
        test_extract.txt
        test_extract.yaml
```



## Getting Started

Clone the repository:

```bash
git clone https://github.com/Hussein-Sharifi/ETL
```

To ensure compatibility, it’s recommended to use a clean Conda environment.

#### Using Conda (Recommended)

From the project root directory, create the environment:

```bash
conda env create -f environment.yml
```

Once installed, activate the environment:

```bash
conda activate FAenv
```

#### Without Conda (Using pip)

If you prefer not to use Conda, install the required dependencies using pip:

```bash
pip install -r requirements.txt
```

#### Configuration

1. Open the `config` folder and edit `example_env.txt`.
2. Fill in your FMP API key and PostgreSQL credentials.
3. Rename the file to `.env`.

---


## Running the ETL Script

The main pipeline script is `ETL.py`. It accepts several arguments to customize behavior.

#### Supported Arguments

- `--manual`: Indicates arguments will be passed directly in the CLI.
- `--config`: Path to a YAML file with pre-defined arguments.
- `--symbols`: Space-separated list of stock symbols (e.g., `AAPL MSFT GOOG`).
- `--requests`: Type of data to fetch (`stock`, `statement`, or `all`). Currently, only `all` is supported.
- `--queries`: space-separated API query parameters in the format:
  - `"from=YYYY-MM-DD"`
  - `"to=YYYY-MM-DD"`
  - `"period=annual|quarterly"` (Note: quarterly data requires an FMP subscription)
  - `"limit=<integer>"`
- `--save_to`: Folder name for saving raw and processed data. Also used as a prefix for SQL tables.
- `--timestamp`: Boolean flag to append timestamps to filenames. This argument will also append new data to SQL tables instead of overwriting them (useful for scheduled tasks).

#### Example (Manual Arguments)

```
python scripts/ETL.py --manual --symbols AAPL MSFT --requests all --queries "from=2025-04-01" "to=2025-05-01" "period=annual" "limit=1" --save_to foldername --timestamp
```

#### Example (YAML Config)

1. Edit `tests/test_extract.yaml` with your desired arguments.
2. Run the script:

```
python scripts/ETL.py --config tests/test_extract.yaml
```

#### What the Script Does

- Fetches raw data from the FMP API and saves it to `data/raw/<foldername>`
- Processes data into wide-format DataFrames
- Uploads wide-format data to PostgreSQL and generates indicator tables:
  - `<foldername>_profitability`
  - `<foldername>_leverage`
  - `<foldername>_liquidity`
- Converts indicator tables into tidy long format using pandas
- Replaces the wide-format tables in PostgreSQL with the tidy versions:
  - `<foldername>_stocks`
  - `<foldername>_tidy` (contains original statements)
  - `<foldername>_indicators`
- Saves the three tidy tables as CSV files in `data/processed/<foldername>`


---

## Extract and Transform (Optional)

- To **only extract** raw data (no transformation), use `extract.py` with the same argument structure.
- To **only transform** existing raw data, use `transform.py` with the same arguments (except `--timestamp` is not supported here).

---


## License & Data Usage

This project uses data provided by the Financial Modeling Prep (FMP) public API. All data is used strictly for educational purposes and is not redistributed.  
Source code, models, and visualizations are shared under fair use for learning and demonstration only.
