from colorama import Fore, Style, init
from dotenv import load_dotenv
import os
import requests
import pandas as pd
import re
from sqlalchemy import create_engine, text

init(autoreset=True) #? Only for text colors
load_dotenv() #? Load variables from .env file

# Load API key 
API_KEY = os.getenv("POLYGON_API_KEY")
LIMIT   = os.getenv("TICKER_LIMIT")  

def convert_time(val):
    if val is None:
        return None
    # Polygon format: 2025-09-18T06:05:34.656751435Z
    match = re.match(r'(\d{4}-\d{2}-\d{2})T(\d{2}:\d{2}:\d{2}\.\d+)(Z)?', val)
    if match:
        # Assemble to PostgreSQL format: YYYY-MM-DD HH:MM:SS.ffffff
        return f"{match.group(1)} {match.group(2)}"
    return val  # return original if not matching Polygon format

# Function to fetch tickers with pagination
def fetch_tickers(key, limit):
    # verify key and limit
    if not key: 
        raise ValueError("API Key not found. Please set POLYGON_API_KEY in your .env file.")
    if not limit or not limit.isdigit() or int(limit) <= 0:
        raise ValueError("Invalid limit value. Please set a positive integer for TICKER_LIMIT in your .env file.")

    #! DEBUG: API key is present...
    print(Fore.GREEN + "API Key loaded successfully." + Style.RESET_ALL)

    # Init variables
    tickers = []
    url     = f"https://api.polygon.io/v3/reference/tickers?market=stocks&active=true&order=asc&limit={limit}&sort=ticker&apiKey={key}"

    # Fetch data with pagination
    while url:
        try:
            response = requests.get(url)                      #? Make GET request
            response.raise_for_status()                       #? Raise error for bad responses
            data = response.json()                            #? Parse JSON response
            tickers.extend(data.get("results", []))           #? Add new tickers to list
            url = data.get("next_url") + f"&apiKey={key}"     #? Update URL for next request or None if not available

        except requests.exceptions.RequestException as e:
            print(Fore.RED + f"CONNEXION ERROR : {e}")
            break
    

    return tickers

# Export DataFrame to various formats based on configuration
#! MAKE SURE TO CONFIGURE .env FILE
def export_data(df):
    # Helper to ensure directory exists
    def ensure_dir(path):
        if not os.path.exists(path):
            os.makedirs(path)

    # export to CSV
    if os.getenv("EXPORT_CSV") == "True":
        csv_name = os.getenv("CSV_NAME", "ticker_list")
        csv_dir = os.getenv("CSV_DIR", "csv")
        ensure_dir(csv_dir)
        numFile = 0
        while os.path.exists(os.path.join(csv_dir, f'{csv_name}{numFile or ""}.csv')):
            numFile += 1
        out_path = os.path.join(csv_dir, f"{csv_name}{numFile if numFile > 0 else ''}.csv")
        df.to_csv(out_path, index=False)
        print(Fore.GREEN + f"Exported to {out_path}" + Style.RESET_ALL)
    
    # export to JSON
    if os.getenv("EXPORT_JSON") == "True":
        json_name = os.getenv("JSON_NAME", "ticker_list")
        json_dir = os.getenv("JSON_DIR", "json")
        ensure_dir(json_dir)
        numFile = 0
        while os.path.exists(os.path.join(json_dir, f'{json_name}{numFile or ""}.json')):
            numFile += 1
        out_path = os.path.join(json_dir, f"{json_name}{numFile if numFile > 0 else ''}.json")
        df.to_json(out_path, index=False)
        print(Fore.GREEN + f"Exported to {out_path}" + Style.RESET_ALL)
    
    # export to Excel
    if os.getenv("EXPORT_EXCEL") == "True":
        excel_name = os.getenv("EXCEL_NAME", "ticker_list")
        excel_dir = os.getenv("EXCEL_DIR", "excel")
        ensure_dir(excel_dir)
        numFile = 0
        while os.path.exists(os.path.join(excel_dir, f'{excel_name}{numFile or ""}.xlsx')):
            numFile += 1
        out_path = os.path.join(excel_dir, f"{excel_name}{numFile if numFile > 0 else ''}.xlsx")
        df.to_excel(out_path, index=False)
        print(Fore.GREEN + f"Exported to {out_path}" + Style.RESET_ALL)
    
    #TODO: postgres
    if os.getenv("EXPORT_POSTGRES") == "True":
        # Load Postgres connection details from .env
        user     = os.getenv("POSTGRES_USER")
        password = os.getenv("POSTGRES_PASSWORD")
        host     = os.getenv("POSTGRES_HOST")
        port     = os.getenv("POSTGRES_PORT")
        db_name  = os.getenv("POSTGRES_DB")


        postgres_url = f'postgresql://{user}:{password}@{host}:{port}/{db_name}'
        if not postgres_url:
            print(Fore.RED + "ERROR: Info provided in .env file, regarding postgreSQL, is incomplete." + Style.RESET_ALL)
            return

        engine = create_engine(postgres_url)
        with engine.connect() as conn:
            df.to_sql("tickers", conn, if_exists="append", index=False)
            print(Fore.GREEN + "Data exported to PostgreSQL database successfully." + Style.RESET_ALL)

# Main execution
def main():
    try:
        # Fetch tickers from API
        tickers = fetch_tickers(API_KEY, LIMIT)

        # Print results
        print(Fore.GREEN + f"Fetched {len(tickers)} tickers.\n")

        # Create DataFrame
        df = pd.DataFrame(tickers)

        #? date conversion to suit PostgreSQL format
        df['last_updated_utc'] = df['last_updated_utc'].apply(convert_time)
        
        #! DEBUG: Print first few rows of the DataFrame
        print(df.head())  

        # Convert to data frame and export to various formats
        export_data(df)

    except ValueError as e:
        print(Fore.RED + f"ERROR: {e}")

if __name__ == "__main__":
    main()