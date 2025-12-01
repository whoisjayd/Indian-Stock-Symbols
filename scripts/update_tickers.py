import os
import csv
import json
import time
import requests
import logging
import sys
from pathlib import Path
from io import StringIO
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# Constants
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
TIMEOUT = 60
MAX_RETRIES = 3
DELAY = 2

BASE_DIR = Path(os.environ.get("GITHUB_WORKSPACE", "."))

# Single source for all data
IIFL_URL = "http://content.indiainfoline.com/IIFLTT/Scripmaster.csv"

CONFIG = [
    {
        "key": "nse_equity",
        "dir": "nse/equity",
        "suffix": ".NS",
        "filter": lambda row: row['Exch'] == 'N' and row['ExchType'] == 'C' and row['AllowedToTrade'] == 'Y' and row['Series'] in ['EQ', 'BE', 'BZ', 'SM', 'ST'],
        "ticker_col": "Name",
        "include_in_all": True
    },
    {
        "key": "nse_etf",
        "dir": "nse/etf",
        "suffix": ".NS",
        "filter": lambda row: row['Exch'] == 'N' and row['ExchType'] == 'C' and 'ETF' in str(row.get('Name', '')).upper() and row['AllowedToTrade'] == 'Y',
        "ticker_col": "Name",
        "include_in_all": False
    },
    {
        "key": "bse_equity",
        "dir": "bse/equity",
        "suffix": ".BO",
        "filter": lambda row: row['Exch'] == 'B' and row['ExchType'] == 'C' and row['AllowedToTrade'] == 'Y' and (row['Scripcode'].startswith('5') or row['Scripcode'].startswith('2')),
        "ticker_col": "Scripcode",
        "include_in_all": True
    }
]


def get_session() -> requests.Session:
    """Creates a requests session with default headers."""
    s = requests.Session()
    s.headers.update({
        "User-Agent": USER_AGENT
    })
    return s


def download_csv(session: requests.Session, url: str) -> str:
    """Downloads CSV content from the given URL with retry logic."""
    for attempt in range(MAX_RETRIES):
        try:
            response = session.get(url, timeout=TIMEOUT)
            response.raise_for_status()
            response.encoding = 'utf-8'
            return response.text
        except requests.RequestException as e:
            logger.warning(f"Attempt {attempt + 1} failed for {url}: {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(DELAY)
            else:
                logger.error(f"Max retries reached for {url}")
                raise


def clean_ticker(ticker: Any) -> str:
    """Cleans the ticker symbol by removing whitespace and quotes."""
    return str(ticker).strip().replace('"', '').replace("'", "")


def process_data(csv_text: str) -> List[str]:
    """Processes the CSV text and generates ticker files based on CONFIG."""
    f = StringIO(csv_text)
    reader = csv.DictReader(f)
    rows = list(reader)

    logger.info(f"Total rows fetched: {len(rows)}")

    all_india_tickers = []

    # Ensure data directory exists
    data_dir = BASE_DIR / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    for config in CONFIG:
        logger.info(f"Processing {config['key']}...")

        out_dir = BASE_DIR / "data" / config['dir']
        out_dir.mkdir(parents=True, exist_ok=True)

        # Filter data
        filtered_rows = [row for row in rows if config['filter'](row)]

        # Generate Full Tickers JSON
        full_json_path = out_dir / "full_tickers.json"
        with open(full_json_path, 'w', encoding='utf-8') as f:
            json.dump(filtered_rows, f, ensure_ascii=False, indent=2)

        # Extract Tickers
        tickers = []
        for row in filtered_rows:
            raw_ticker = row[config['ticker_col']]
            ticker = clean_ticker(raw_ticker)
            if ticker:
                tickers.append(f"{ticker}{config['suffix']}")

        # Sort and Unique
        tickers = sorted(list(set(tickers)))

        # Write files
        with open(out_dir / "tickers.txt", 'w', encoding='utf-8') as f:
            f.write("\n".join(tickers))
            f.write("\n")

        with open(out_dir / "tickers.json", 'w', encoding='utf-8') as f:
            json.dump(tickers, f, indent=2)

        if config['include_in_all']:
            all_india_tickers.extend(tickers)

    return all_india_tickers


def main():
    print("Script starting...", flush=True)
    try:
        session = get_session()

        logger.info("Downloading Scrip Master...")
        csv_text = download_csv(session, IIFL_URL)

        if not csv_text:
            logger.error("Downloaded CSV is empty")
            exit(1)

        all_india_tickers = process_data(csv_text)

        # Process 'all' category
        logger.info("Processing all_india_tickers...")
        all_dir = BASE_DIR / "data" / "all"
        all_dir.mkdir(parents=True, exist_ok=True)

        all_india_tickers = sorted(list(set(all_india_tickers)))

        with open(all_dir / "tickers.txt", 'w', encoding='utf-8') as f:
            f.write("\n".join(all_india_tickers))
            f.write("\n")

        with open(all_dir / "tickers.json", 'w', encoding='utf-8') as f:
            json.dump(all_india_tickers, f, indent=2)

        logger.info("Update completed successfully.")

    except Exception as e:
        logger.error(f"Script failed: {e}")
        exit(1)


if __name__ == "__main__":
    main()
