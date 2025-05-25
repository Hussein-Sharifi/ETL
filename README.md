# Automated Financial Data ETL Pipeline

Built a modular ETL pipeline that automates the extraction and processing of historical stock prices and company financial statements (income, balance sheet, and cash flow) using a public API. The pipeline computes key financial indicators in PostgreSQL, organized into profitability, leverage, and liquidity categories. All raw and processed data, including calculated metrics, are stored in PostgreSQL tables and exported as CSV files for external use or downstream analysis. See test folder for example raw and processed outputs.

- Data Source: All financial data is collected from the Financial Modelling Prep (FMP) API, which aggregates filings from the U.S. SEC. This ETL's processes are built on FMP's free tier. 

- Indicators: Financial indicators are computed in SQL using standardized formulas (see [Indicator Formulas](#indicator-formulas)).

- Export Format: Processed data is output in a tidy long format, structured for compatibility with Power BI dashboards or other analytical tools.

- Data Traceability: Each financial statement entry includes a reference to the original SEC filings, enabling manual verification of reported figures. These are accessible via the finalLink field, available through raw and processed statement files.

- Automation: the ETL script is designed to allow updating stocks/statements data separately. This allows user to update dashboards with new data automatically by using scheduled tasks. 

---

## Table of Contents

1. [Project Structure](#project-structure)  
2. [Getting Started](#getting-started)  
   1. [Using Conda (Recommended)](#using-conda-recommended)  
   2. [Without Conda (Using pip)](#without-conda-using-pip)  
   3. [Configuration](#configuration)  
   4. [Running the ETL Script](#running-the-etl-script)  
   5. [Extract Only (Optional)](#extract-only-optional)  
3. [Indicator Formulas](#indicator-formulas)
4. [Indicator Customization](#indicator-customization)
5. [License & Data Usage](#license--data-usage)

---

## Project Structure

```
Project_Root
│   .gitignore
│   environment.yml
│   README.md
│   requirements.txt
│
├───config
│       default_endpoints.json
│       example_env.txt
│
├───data
│   ├───processed
│   └───raw
│
└───scripts
        config.py
        ETL.py
        extract.py
        FA_io.py
        fmp_client.py
        parser.py
        sql_transforms.py
        sql_utils.py
        transform.py
        utils.py
```



## Getting Started

Clone the repository:

```bash
git clone https://github.com/Hussein-Sharifi/ETL
```

To ensure compatibility, it’s recommended to use a clean Conda environment.

### 1. Using Conda (Recommended)

From the project root directory, create the environment:

```bash
conda env create -f environment.yml
```

Once installed, activate the environment:

```bash
conda activate FAenv
```

### 2. Without Conda (Using pip)

If you prefer not to use Conda, install the required dependencies using pip:

```bash
pip install -r requirements.txt
```

### Configuration

1. Open the `config` folder and edit `example_env.txt`.
2. Fill in your FMP API key and PostgreSQL credentials.
3. Rename the file to `.env`.

---


## Running the ETL Script

The main pipeline script is `ETL.py`. It accepts several arguments to customize behavior.

### Supported Arguments

- `--manual`: Indicates arguments will be passed directly in the CLI.
- `--config`: Path to a YAML file with pre-defined arguments.
- `--symbols`: Space-separated list of stock symbols (e.g., `AAPL MSFT GOOG`).
- `--requests`: Type of data to fetch (`stocks`, `statements`, or `all`).
- `--queries`: space-separated API query parameters in the format:
  - `"from=YYYY-MM-DD"`  (Beginning and ending period for fetching stocks)
  - `"to=YYYY-MM-DD"`
  - `"period=annual|quarterly"` (Note: quarterly statement data requires an FMP subscription)
  - `"limit=<integer>"`  (Number of statements to fetch)
- `--save_to`: Folder name for saving raw and processed data. Also used as a prefix for SQL tables.
- `--timestamp`: Boolean flag to append timestamps to filenames. This argument will also append new data to SQL tables instead of overwriting them (useful for scheduled tasks).

You need to specify whether arguments are passed manually or using config YAML file. i.e. these arguments are mutually exclusive. All other arguments are required except timestamp. Note that you should still pass all queries even if only processing stocks or statements.

#### 1. Example (Manual Arguments)

```
python scripts/ETL.py --manual --symbols AAPL MSFT --requests all --queries "from=2025-04-01" "to=2025-05-01" "period=annual" "limit=1" --save_to foldername --timestamp
```

#### 2. Example (YAML Config)

1. Edit `tests/test_extract.yaml` with your desired arguments.
2. Run the script:

```
python scripts/ETL.py --config <absolute_yaml_path>
```

### What the Script Does

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
- Saves the three tidy tables as CSV files in `dataprocessed/<foldername>`

### Extract Only (Optional)

- To only extract raw data (no transformation), use `extract.py` with the same argument structure.

---

## Indicator Formulas

#### Profitability Indicators

| Indicator                     | Formula                                                                 |
|------------------------------|-------------------------------------------------------------------------|
| Naive ROE                    | netIncome / totalEquity                                                 |
| Naive ROA                    | netIncome / totalAssets                                                 |
| Simplified ROIC              | (netIncome - dividendsPaid) / (totalDebt + totalEquity)                |
| Gross Profit Margin          | grossProfit / revenue                                                   |
| Operating Margin             | operatingIncome / revenue                                               |
| Operating Income Ratio       | operatingIncomeRatio                                                    |
| Net Profit Margin            | netIncome / revenue                                                     |
| EBITDA Margin                | ebitda / revenue                                                        |
| Earnings Per Share (EPS)     | eps                                                                     |
| Diluted Earnings Per Share   | epsdiluted                                                              |

#### Leverage Indicators

| Indicator                     | Formula                                                                 |
|------------------------------|-------------------------------------------------------------------------|
| Naive Debt-to-Equity         | totalDebt / totalEquity                                                 |
| Naive Equity Ratio           | totalEquity / totalAssets                                               |
| Naive Debt Ratio             | totalDebt / totalAssets                                                 |
| Naive Debt-to-Capital        | totalDebt / (totalDebt + totalEquity)                                   |
| Interest Coverage            | ebitda / interestExpense                                                |
| Net Debt to EBITDA           | (totalDebt - cashAndCashEquivalents) / ebitda                          |

#### Liquidity Indicators

| Indicator                          | Formula                                                                 |
|-----------------------------------|-------------------------------------------------------------------------|
| Current Ratio                     | totalCurrentAssets / totalCurrentLiabilities                            |
| Quick Ratio                       | (cashAndCashEquivalents + shortTermInvestments + accountsReceivables) / totalCurrentLiabilities |
| Cash Ratio                        | cashAndCashEquivalents / totalCurrentLiabilities                        |
| Operating Cash Flow to CapEx      | operatingCashFlow / ABS(capitalExpenditure)                             |
| Operating Cash Flow Ratio         | operatingCashFlow / totalCurrentLiabilities                             |

Note: Indicators labeled as "Naive" are typically averaged quarterly to produce more consistent and reliable results. However, accessing quarterly financial statements requires a subscription to FMP. To maintain broader usability of this ETL pipeline without imposing subscription constraints, I’ve chosen to use annual metrics instead. While these metrics may be less granular, they remain valuable for identifying trends and are clearly labeled to inform user discretion.

---

## Indicator Customization

If you would like to add any indicators of your own, you can easily do so by modifying the selection in scripts/sql_utils.py. Here is a list of metrics available through raw statements data:

| Metric 1 | Metric 2 | Metric 3 |
|----------|----------|----------|
| revenue    | costOfRevenue | grossProfit |
| grossProfitRatio | researchAndDevelopmentExpenses | generalAndAdministrativeExpenses |
| sellingAndMarketingExpenses | sellingGeneralAndAdministrativeExpenses | otherExpenses |
| operatingExpenses | costAndExpenses | interestIncome |
| interestExpense | depreciationAndAmortization | ebitda     |
| ebitdaratio | operatingIncome | operatingIncomeRatio |
| totalOtherIncomeExpensesNet | incomeBeforeTax | incomeBeforeTaxRatio |
| incomeTaxExpense | netIncome  | netIncomeRatio |
| eps        | epsdiluted | weightedAverageShsOut |
| weightedAverageShsOutDil | cashAndCashEquivalents | shortTermInvestments |
| cashAndShortTermInvestments | netReceivables | inventory  |
| otherCurrentAssets | totalCurrentAssets | propertyPlantEquipmentNet |
| goodwill   | intangibleAssets | goodwillAndIntangibleAssets |
| longTermInvestments | taxAssets  | otherNonCurrentAssets |
| totalNonCurrentAssets | otherAssets | totalAssets |
| accountPayables | shortTermDebt | taxPayables |
| deferredRevenue | otherCurrentLiabilities | totalCurrentLiabilities |
| longTermDebt | deferredRevenueNonCurrent | deferredTaxLiabilitiesNonCurrent |
| otherNonCurrentLiabilities | totalNonCurrentLiabilities | otherLiabilities |
| capitalLeaseObligations | totalLiabilities | preferredStock |
| commonStock | retainedEarnings | accumulatedOtherComprehensiveIncomeLoss |
| othertotalStockholdersEquity | totalStockholdersEquity | totalEquity |
| totalLiabilitiesAndStockholdersEquity | minorityInterest | totalLiabilitiesAndTotalEquity |
| totalInvestments | totalDebt  | netDebt    |
| deferredIncomeTax | stockBasedCompensation | changeInWorkingCapital |
| accountsReceivables | accountsPayables | otherWorkingCapital |
| otherNonCashItems | netCashProvidedByOperatingActivities | investmentsInPropertyPlantAndEquipment |
| acquisitionsNet | purchasesOfInvestments | salesMaturitiesOfInvestments |
| otherInvestingActivites | netCashUsedForInvestingActivites | debtRepayment |
| commonStockIssued | commonStockRepurchased | dividendsPaid |
| otherFinancingActivites | netCashUsedProvidedByFinancingActivities | effectOfForexChangesOnCash |
| netChangeInCash | cashAtEndOfPeriod | cashAtBeginningOfPeriod |
| operatingCashFlow | capitalExpenditure | freeCashFlow |

--- 

## License & Data Usage

This project uses data provided by the Financial Modeling Prep (FMP) public API. All data is used strictly for educational purposes and is not redistributed. Source code, models, and visualizations are shared under fair use for learning and demonstration only.
