# Financial Analysis ETL Pipeline with Quantum Stock Analysis

This project is an end-to-end ETL pipeline that:

- Extracts stock market data (stock prices, income statements, balance sheets, and cashflows) from the [Financial Modeling Prep API](https://site.financialmodelingprep.com/),
- Transforms and loads the data into a PostgreSQL database,
- Performs financial computations and generates key indicators,
- Exports the processed data to Excel and updates a Power BI dashboard.

---

## Table of Contents

1. [Project Structure](#project-structure)  
2. [Getting Started](#getting-started)  
    1. [Using Conda (Recommended)](#using-conda-recommended)  
    2. [Without Conda (Using pip)](#without-conda-using-pip)  
    3. [Configuration](#configuration)
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
│       .env
│       default_endpoints.json
│       example_env.txt
│
├───data
│   ├───processed
│   └───raw
│
├───outputs
│   ├───figures
│   ├───models
│   └───tables
├───scripts
│   │   config.py
│   │   extract_data.py
│   │   FA_io.py
│   │   fmp_client.py
│   │   parser.py
│   │   sql_transforms.py
│   │   sql_utils.py
│   │   transform_data.py
│   └─ utils.py
│
│
└───tests
        test_extract.txt
        test_extract.yaml
```

## Getting Started
To ensure compatibility, it is recommended to create a clean Conda environment.


### Using Conda (Recommended)
To recreate Conda environment, navigate to the project root directory in your terminal and run:

```
conda env create -f environment.yml
```

Follow through with the installation, then run

```
conda activate FAenv
```

### Without Conda (Using pip)
If you prefer not to use Conda, install dependencies using pip:

```
pip install -r requirements.txt
```

### Configuration

## License & Data Usage
This project utilizes data from Financial Modeling Prep through their public API. Data is used for educational purposes only and is not redistributed. Models, visualizations, and source code are shared under fair use for learning and demonstration.
