# clubauto
.
# Club Auto Data Integration

A Python application for syncing member data between Daxko and Go High Level (GHL), with CSV export and email notifications.

## Features
- Fetches member data from Daxko API
- Transforms data to match GHL field structure
- Outputs to:
  - CSV export with email notification
  - Direct GHL API integration

## Prerequisites
- Python 3.x
- Environment variables:
  - `CLIENT_SECRET` (Daxko API)
  - `GHL_API` (Go High Level API key)
  - `GHL_LOCATION` (Go High Level location ID)
  - Email configuration (for CSV reports)

## Installation
1. Clone the repository:
git clone https://github.com/karatechopping/clubauto.git
cd clubauto

2. Create and activate virtual environment:
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

3. Install dependencies:
pip install -r requirements.txt

## Processing Order
The application follows a strict processing sequence:

1. **Data Fetching** (DataFetcher)
   - Retrieves raw data from Daxko API
   - Uses pagination to handle large datasets

2. **Data Transformation** (DataTransformer)
   - Maps fields according to field_mappings configuration
   - Prepares standardized data format

3. **CSV Generation & Email** (CSVHandler + EmailHandler)
   - Creates CSV file with transformed data
   - Emails the CSV report

4. **GHL API Integration** (GHLHandler)
   - Processes contacts through GHL API
   - Handles rate limiting and error tracking

## Project Structure
clubauto/
├── src/
│   ├── __init__.py
│   ├── data_fetcher.py    # Daxko API integration
│   ├── data_transformer.py # Data mapping logic
│   └── output_handlers/
│       ├── csv_handler.py  # CSV generation
│       ├── email_handler.py # Email notifications
│       └── ghl_handler.py  # GHL API integration
├── main.py                # Main execution script
└── requirements.txt       # Project dependencies

## TODO
- [ ] Add processing option selector (1=CSV only, 2=API only, 3=both)
- [ ] Add error reporting and retries
- [ ] Add logging system
- [ ] Create configuration file for field mappings
- [ ] Add data validation checks
- [ ] Implement unit tests
- [ ] Add detailed API documentation
- [ ] Create deployment guide
- [ ] Add monitoring and metrics
- [ ] Add DND (Do Not Disturb) mapping documentation
- [ ] Test GHL API with test environment
- [ ] Add configuration for email templates
- [ ] Implement proper error handling for all API calls
- [ ] Add data sanitization for CSV exports
- [ ] What to do with the different member types
- [ ] Why is gender not coming through

## Field Mappings
Custom field mappings are configured in `main.py` to transform Daxko fields to GHL format. See field_mappings dictionary for current mapping structure.
