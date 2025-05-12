# ETL Pipeline for E-commerce Data

![status](https://img.shields.io/badge/status-work--in--progress-yellow)

🚧 **Project Status:** Currently in development  
✅ **Completed:** Extract and Transform phases implemented  
🔄 **Next Steps:** Implement Load phase and SQL-based analytics  
🎯 **Target:** Fully functional ETL pipeline with reporting by end of **May 2025**

## 📄 Description

This project implements a simple ETL (Extract, Transform, Load) pipeline to process data from the public [DummyJSON](https://dummyjson.com/) API. The goal is to download data about users, products, and carts, transform it using Pandas, and load it into a relational SQL database. The project serves as a demonstration of basic ETL principles and working with tools like Python, Pandas, and SQLAlchemy for a portfolio.

## ⚙️ Features

* **Extract:** Downloads data (users, products, carts) from the DummyJSON API with implemented retry logic for increased reliability. **Saves** raw data in JSON format.
* **Transform:** **Loads** raw data, uses the Pandas library for **cleaning**, **transformation**, and data preparation:
    * Selection of relevant columns.
    * Renaming columns (e.g., to snake_case).
    * Data type conversion (numbers, dates, strings).
    * Handling nested data (normalization of carts into `carts` and `cart_items` tables).
    * Processing product reviews list (extracting comments, calculating review count).
    * Duplicate removal.
* **Load:** Loads transformed data into an SQL database (SQLite by default, configured in `config.py`) using SQLAlchemy and Pandas `to_sql()` method. Tables are typically replaced on each run.
* **Logging:** **Records** the pipeline progress to the console (INFO level) and to a file (`logs/etl_pipeline.log`, DEBUG level) for easy monitoring and debugging. Configuration is centralized.
* **Configuration:** Allows setting API endpoints and file paths in `config.py`.

## 🗂 Project Structure
```
data-pipeline-eshop/
├── .gitignore
├── data/                     # Stored raw data from the API (JSON)
│   ├── carts_data.json
│   ├── products_data.json
│   └── users_data.json
├── logs/                     # Pipeline log files
│   └── etl_pipeline.log
├── src/                      # Source code for pipeline modules
│   ├── init.py
│   ├── extract.py            # Module for data extraction from API
│   ├── load.py               # Module for loading data into DB
│   ├── logging_setup.py      # Helper module for logging setup
│   └── transform.py          # Module for data transformation using Pandas
├── config.py                 # Configuration file (API, paths, logging)
├── main.py                   # Main script to run the ETL pipeline
├── poetry.lock
├── pyproject.toml
├── makefile
├── .gitlint
├── .pre-commit-config.yaml
└── README.md                 # This file
```

## ⚙️ Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/michalpuskac/etl-pipeline-for-ecommerce-data.git
    cd data-pipeline-eshop
    ```
2.  **Prerequisites:**
    * [Python 3.10+](https://www.python.org/downloads/) (or the version you are using)
    * [Poetry](https://python-poetry.org/) for dependency management
3.  **Install dependencies:**
    ```bash
    poetry install
    ```

    This will install all necessary libraries, including `pandas`, `requests`, and `sqlalchemy`.

## Configuration

The main configuration is located in the `config.py` file. You can modify:

* `API_ENDPOINTS`: URLs for data download.
* `DATA_DIR`: Path to the directory for storing raw JSON data.
* `LOG_DIR`: Path to the directory for storing log files.
* `LOGGING_CONFIG`: Detailed logging setup (levels, formatters, handlers).
* **(Later)** `DB_CONNECTION_STRING`: Connection string for the target database.

## ▶️ Usage

Run the complete ETL pipeline from the project root directory using the command:

```bash
python main.py
```

The script will execute the Extract, Transform, and Load phases. Progress is logged to the console and to the logs/etl_pipeline.log file. The data will be loaded into an SQLite database file located at data/ecommerce_pipeline.db (by default).

You can inspect the SQLite database using tools like [DB Browser for SQLite](https://sqlitebrowser.org/dl/).
---

### 🔍 ETL Process Details

1. **Extract:**

* The script iterates through the endpoints defined in config.API_ENDPOINTS.
* For each endpoint, it calls the Workspace_from_api function from src/extract.py, which downloads the data (with up to 3 retry attempts in case of errors).
* The downloaded data is saved as JSON files into the data/ directory using the save_to_json function.

2. **Transform:**

* The script iterates through the downloaded JSON files.
* It loads the data and uses the convert_list_to_dataframe function to convert the relevant part of the JSON (list of objects) into a Pandas DataFrame.
* It applies specific transformation functions (transform_users, transform_products, transform_carts) from src/transform.py:
    * Users: Column selection (user_id, first_name, ... specify), renaming, converting birth_date to datetime.
    * Products: Column selection (id, title, ... specify), renaming, type conversions (price, discount, rating, stock), duplicate removal, processing reviews (extracting comments/count - specify).
    * Carts: Normalization of data into two tables: carts (cart info - cart_id, user_id, totals) and cart_items (item info - cart_id, product_id, quantity, price...). Data type conversions.

The result is clean Pandas DataFrames ready for the Load phase.

3. **Load:**

* This phase takes the transformed Pandas DataFrames.
* It connects to the target SQL database (SQLite, as specified in config.py) using an SQLAlchemy engine created by create_db_engine from src/load.py.
* For each DataFrame, it calls load_dataframe_to_db which uses Pandas' to_sql() method to write the data.
* By default, if a table already exists, it is replaced (if_exists='replace'). The DataFrame index is not saved as a column.

### Logging
The pipeline logs information about its progress:

* Console: Messages from INFO level upwards are displayed (main pipeline steps).
* File: All logs from DEBUG level upwards are saved to logs/etl_pipeline.log. It contains detailed information for debugging.

### 🔍 Code Quality and Development Workflow

This project employs a suite of tools and a `Makefile` to ensure high code quality, consistency, and an efficient development process. These practices help in maintaining a clean, readable, and robust codebase.

### Tools Used:

* **Black:** An uncompromising Python code formatter that automatically reformats code to a consistent style.
* **Pylint:** A static code analysis tool that checks for errors, enforces coding standards, identifies code smells, and offers suggestions for refactoring.
* **isort:** A Python utility to sort imports alphabetically and automatically separate them into sections and by type.
* **dotenv-linter:** A tool to validate `.env` files, helping to prevent common errors in environment variable definitions.
* **Bandit:** A tool designed to find common security issues in Python code.
* **Gitlint (via pre-commit hook):** Enforces conventional commit message styles, ensuring commit messages are descriptive and follow a consistent format. This is typically run automatically before each commit if pre-commit hooks are set up.
* **Pre-commit Hooks:** The project is set up to use pre-commit hooks (configuration in `.pre-commit-config.yaml`) to automatically run selected checks (like Black, isort, Pylint, Gitlint, etc.) before each commit. This helps catch issues early and maintain code standards.

### Makefile Commands:

A `Makefile` is provided to simplify common development tasks. Key commands include:

* `make format`: Formats all Python code in the current directory and subdirectories using **Black**.
* `make lint`: Runs **Pylint** on all Python files in the current directory and subdirectories to check for code quality issues and style violations.
* `make isort`: Sorts and formats import statements in Python files using **isort**.
* `make dotenv`: Validates the `.env` file using **dotenv-linter**.
* `make security`: Scans the `src` directory for common security vulnerabilities using **Bandit**.
* `make check`: A convenience command that runs `format`, `isort`, `lint`, `dotenv`, and `security` tasks sequentially, providing a comprehensive check of the codebase.

To use these commands, simply run them from the root directory of the project, for example:
```bash
make check
```


### 🚀 Planned Features & Enhancements

The current implementation focuses on building a reliable and modular ETL pipeline. The following features and enhancements are planned to expand its capabilities and demonstrate more comprehensive end-to-end data engineering workflows:


-   🗃️ **Refine Load Phase & Database Schema:**
    * Implement explicit DDL (Data Definition Language) for table creation, defining precise data types, primary keys, foreign keys, `NOT NULL` constraints, and indexes.
    * Explore strategies for handling schema evolution and data integrity checks post-load.
-   ✅ **Testing:**
    * Add comprehensive unit tests (for individual functions) and integration tests (for pipeline segments) using `pytest` to ensure code reliability and data accuracy.
-   🔄 **Orchestration:**
    * Introduce pipeline scheduling, monitoring, and dependency management using a workflow orchestration tool like Apache Airflow.
-   ⚠️ **Advanced Error Handling & Fault Tolerance:**
    * Improve pipeline-level error handling with more granular logging, notifications (e.g., email alerts on failure), and implement step-level error recovery or retry mechanisms.
-   🌐 **Expand Data Sources & Transformations:**
    * Integrate additional APIs, files, or database sources to enrich the dataset.
    * Implement more complex data transformations, aggregations, or feature engineering based on potential analytical requirements.
-   🧪 **Secure Configuration Management:**
    * Manage sensitive configuration (especially database credentials for non-SQLite databases or production environments) securely using `.env` files and environment variables (e.g., using `python-dotenv`).
-   💬 **In-depth Text Analysis:**
    * Apply Natural Language Processing (NLP) techniques, such as sentiment analysis (e.g., using NLTK or TextBlob) and topic modeling, on the extracted product review comments for deeper customer insights.
-   📈 **Incremental Loading Strategies:**
    * Investigate and implement incremental loading techniques (e.g., based on timestamps, watermarks, or change data capture) to process only new or updated data, which is crucial for efficiency with larger or frequently changing datasets.


## 📄 License
This project is licensed under the MIT License. See the [LICENSE](https://github.com/michalpuskac/sql-data-warehouse-project/blob/main/LICENSE) file for details.


## 👨‍💻 Author - Michal Puškáč
This project is part of my portfolio, showcasing skills and concepts I learned. If you have any questions, feedback, or would like to collaborate, feel free to get in touch!


<div align="left">
   <a href="https://www.linkedin.com/in/michal-pu%C5%A1k%C3%A1%C4%8D-94b925179/">
    <img src="https://img.shields.io/badge/LinkedIn-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white" alt="LinkedIn Badge"/>
  </a>
  <a href="https://github.com/michalpuskac">
    <img src="https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white" alt="GitHub Badge"/>
  </a>
</div>
