# India Stock Symbols

Automated daily aggregation of Indian stock symbols (NSE & BSE) in JSON and TXT formats.

## Data Structure

All data is located in the `data/` directory:

```
data/
├── nse/
│   ├── equity/
│   │   ├── tickers.json       # NSE Equity symbols
│   │   ├── tickers.txt
│   │   └── full_tickers.json  # Detailed info
│   └── etf/
│       ├── tickers.json       # NSE ETF symbols
│       └── ...
├── bse/
│   └── equity/
│       ├── tickers.json       # BSE symbols
│       └── ...
└── all/
    ├── tickers.json           # Combined unique symbols
    └── tickers.txt
```

## Updates

- **Frequency**: Daily at 00:00 UTC.
- **Source**: Aggregated from IIFL Open Data (Unified Scrip Master).
- **Automation**: GitHub Actions workflow.

## Usage

- **JSON**: Array of strings (e.g., `["RELIANCE.NS", "TCS.NS"]`).
- **TXT**: Newline-separated list.

_Note: `.NS` suffix denotes NSE, `.BO` suffix denotes BSE._

## Local Development

To run the update script locally:

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Run the script:
   ```bash
   python scripts/update_tickers.py
   ```
