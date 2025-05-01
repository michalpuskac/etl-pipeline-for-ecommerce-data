# ETL Pipeline for E-commerce Data

![status](https://img.shields.io/badge/status-work--in--progress-yellow)

🚧 **Project Status:** Currently in development  
✅ **Completed:** Extract and Transform phases implemented  
🔄 **Next Steps:** Implement Load phase and SQL-based analytics  
🎯 **Target:** Fully functional ETL pipeline with reporting by end of **May 2025**

## 📄 Description

This project implements a simple ETL (Extract, Transform, Load) pipeline to process data from the public [DummyJSON](https://dummyjson.com/) API. The goal is to download data about users, products, and carts, transform it using Pandas, and prepare it for loading into a relational database (Load phase to be implemented). The project serves as a portfolio demonstration of ETL principles and working with tools like Python, Pandas, and SQLAlchemy (planned) for a portfolio.

## ⚙️ Features

* **Extract:** Downloads data (users, products, carts) from the DummyJSON API with implemented retry logic for increased reliability. **Saves** raw data in JSON format.
* **Transform:** **Loads** raw data, uses the Pandas library for **cleaning**, **transformation**, and data preparation:
    * Selection of relevant columns.
    * Renaming columns (e.g., to snake_case).
    * Data type conversion (numbers, dates, strings).
    * Handling nested data (normalization of carts into `carts` and `cart_items` tables).
    * Processing product reviews list (extracting comments, calculating review count).
    * Duplicate removal.
* **Load:** *(Planned)* Loading of transformed data into an SQL database PostgreSQL using SQLAlchemy.
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
│   ├── load.py               # Module for loading data into DB (planned)
│   ├── logging_setup.py      # Helper module for logging setup
│   └── transform.py          # Module for data transformation using Pandas
├── config.py                 # Configuration file (API, paths, logging)
├── main.py                   # Main script to run the ETL pipeline
├── poetry.lock
├── pyproject.toml
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

The script will execute the Extract and Transform phases and log its progress to the console and the logs/etl_pipeline.log file.

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

3. **Load:** *(Planned)*

* (Planned) This phase will load the transformed DataFrames.
* It will connect to the target SQL database (e.g., SQLite/PostgreSQL) using SQLAlchemy.
* It will load the data into the corresponding tables (see Database Schema below) using df.to_sql().

### Logging
The pipeline logs information about its progress:

* Console: Messages from INFO level upwards are displayed (main pipeline steps).
* File: All logs from DEBUG level upwards are saved to logs/etl_pipeline.log. It contains detailed information for debugging.

### 🚀 Planned Features & Enhancements

The current implementation focuses on building a reliable and modular ETL pipeline. The following features are planned to expand its capabilities and demonstrate end-to-end data engineering workflows:

- 🗃 **Load Phase:** Implement loading of transformed data into a relational SQL database using SQLAlchemy.
- ✅ **Testing:** Add unit and/or integration tests using `pytest` to ensure pipeline reliability.
- 🔄 **Orchestration:** Introduce pipeline scheduling and orchestration using a tool like Apache Airflow.
- ⚠️ **Error Handling:** Improve fault tolerance and step-level error recovery mechanisms.
- 🌐 **Data Sources:** Add additional APIs or datasets to enrich the pipeline.
- 🧪 **.env Management:** Secure sensitive configuration (e.g., DB credentials) using environment variables.
- 💬 **Text Analysis:** Apply sentiment analysis (using NLTK or TextBlob) on product review data.

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
