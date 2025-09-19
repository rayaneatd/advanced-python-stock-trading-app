# REST API Extractor Documentation

## Overview
This script fetches stock tickers from the Polygon.io API using pagination and saves the results to CSV, JSON, Excel, and PostgreSQL. It uses environment variables for configuration and displays colored output for better readability.

## Steps Used 
1. **Environment Setup**
   - Loads environment variables from a `.env` file using `python-dotenv`:
     ```python
     from dotenv import load_dotenv
     load_dotenv()
     ```
   - Initializes colored terminal output with `colorama`:
     ```python
     from colorama import Fore, Style, init
     init(autoreset=True)
     ```
2. **API Key and Limit Validation**
   - Checks if the API key and ticker limit are set and valid:
     ```python
     API_KEY = os.getenv("POLYGON_API_KEY")
     LIMIT = os.getenv("TICKER_LIMIT")
     if not key:
         raise ValueError("API Key not found. Please set POLYGON_API_KEY in your .env file.")
     ```
3. **Fetching Data with Pagination**
   - Sends requests to the Polygon.io API and follows pagination using the `next_url` field:
     ```python
     while url:
         response = requests.get(url)
         data = response.json()
         tickers.extend(data.get("results", []))
         url = data.get("next_url") + f"&apiKey={key}"
     ```
   - Handles network errors gracefully and prints connection issues in red:
     ```python
     except requests.exceptions.RequestException as e:
         print(Fore.RED + f"CONNEXION ERROR : {e}")
         break
     ```
4. **Data Processing**
   - Collects all tickers in a list and converts to a pandas DataFrame:
     ```python
     df = pd.DataFrame(tickers)
     ```
   - Converts date fields to PostgreSQL-compatible format:
     ```python
     df['last_updated_utc'] = df['last_updated_utc'].apply(convert_time)
     ```
5. **Data Export**
   - Exports the DataFrame to CSV, JSON, Excel, and PostgreSQL, creating directories if needed:
     ```python
     def ensure_dir(path):
         if not os.path.exists(path):
             os.makedirs(path)
     df.to_csv(out_path, index=False)
     df.to_json(out_path, index=False)
     df.to_excel(out_path, index=False)
     df.to_sql("tickers", conn, if_exists="append", index=False)
     ```
   - Uses environment variables to control export formats and file names.
6. **User Feedback**
   - Prints status and error messages in color for clarity:
     ```python
     print(Fore.GREEN + f"Exported to {out_path}" + Style.RESET_ALL)
     print(Fore.RED + f"ERROR: {e}")
     ```

## Best Practices Used
- **Environment Variables:** Sensitive data (API keys, DB credentials) and configuration are stored securely in a `.env` file.
- **Error Handling:** The script checks for missing or invalid configuration and handles network errors gracefully.
- **Pagination:** Efficiently retrieves all data by following the API's pagination links.
- **Date Conversion:** Converts API date formats to PostgreSQL-compatible timestamps using regex.
- **Directory Management:** Automatically creates export directories if they do not exist.
- **Code Readability:** Uses clear variable names, concise comments, and colored output for better user experience.
- **Data Export:** Saves results in standard formats (CSV, JSON, Excel) and supports direct export to PostgreSQL.

## Requirements
- Python 3
- `requests`, `colorama`, `python-dotenv`, `pandas`, `openpyxl`, `sqlalchemy` (install via `pip`)

## Usage
1. Create a `.env` file with your `POLYGON_API_KEY`, `TICKER_LIMIT`, and export options (see script for details).
2. Run the script: `python script.py`
3. Check the generated files in the respective directories (e.g., `csv/`, `json/`, `excel/`).
4. If enabled, data will also be exported to your PostgreSQL database.
