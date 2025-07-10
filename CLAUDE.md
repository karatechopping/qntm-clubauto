# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a data synchronization system that fetches member data from Daxko (fitness management system) and syncs it to GoHighLevel (GHL) CRM. The application supports CSV export, email notifications, and real-time webhook processing.

## Common Commands

### Running the Application
```bash
# Full sync with CSV and GHL (production mode)
python main.py --run_csv=True --run_ghl=True --run_email=False --sample_size=-1

# CSV export only (testing mode)
python main.py --run_csv=True --run_ghl=False --run_email=False --sample_size=10

# Recent changes only (1 day back)
python main.py --run_csv=True --run_ghl=True --run_email=False --days_back=1

# Email report with CSV attachment
python main.py --run_csv=True --run_ghl=False --run_email=True --attach_csv=True
```

### Development Setup
```bash
# Create virtual environment
python -m venv myenv
source myenv/bin/activate  # Linux/Mac
# myenv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Run with logging disabled for testing
python main.py --run_csv=True --run_ghl=False --run_log=False --sample_size=5
```

### Testing
```bash
# Run with development dependencies
pytest  # if tests exist
black . # code formatting
flake8 . # linting
```

## Architecture

### Data Flow Pipeline
1. **DataFetcher** (`src/data_fetcher.py`): Authenticates with Daxko API and fetches member data
2. **DataTransformer** (`src/data_transformer.py`): Maps Daxko fields to GHL format using field_mappings
3. **Output Handlers** (`src/output_handlers/`):
   - **CSVHandler**: Generates CSV files with transformed data
   - **EmailHandler**: Sends email reports with optional CSV attachments
   - **GHLHandler**: Syncs contacts to GoHighLevel via API with rate limiting

### Key Components

#### Field Mappings (`main.py:20-97`)
Complex mapping system that handles:
- Standard GHL fields (firstName, lastName, email, phone)
- Custom GHL fields with IDs for advanced features
- Multiple phone number types (cell, home, work)
- Membership types (5 different categories)
- Status fields and system IDs

#### Rate Limiting (`src/output_handlers/ghl_handler.py`)
- Implements 100 requests per 10-second window
- Async processing with concurrent threads
- Automatic retry logic with exponential backoff
- Tracks daily and burst rate limits

#### Webhook Handler (`webhook_handler.py`)
Flask application for real-time Daxko updates:
- Receives webhook notifications
- Processes individual member updates
- Integrates with same transformation pipeline

### Environment Variables Required
```bash
# Daxko API
CLIENT_SECRET=your_daxko_client_secret

# GoHighLevel API
GHL_API=your_ghl_api_key
GHL_LOCATION=your_ghl_location_id

# Email configuration (if using email features)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
EMAIL_FROM=your_email@gmail.com
EMAIL_TO=recipient@example.com
```

### File Structure
```
src/
├── data_fetcher.py      # Daxko API integration with pagination
├── data_transformer.py  # Field mapping and validation logic
├── logger_config.py     # Centralized logging configuration
└── output_handlers/
    ├── csv_handler.py   # CSV generation with dual output format
    ├── email_handler.py # SMTP email with attachment support
    └── ghl_handler.py   # Async GHL API with rate limiting
```

## Development Notes

### Data Validation
- Email validation using regex patterns
- Phone number normalization (10+ digits required)
- Records must have valid email OR phone to be processed

### Logging
- Centralized logging in `src/logger_config.py`
- Logs stored in `logs/` directory with timestamps
- Automatic log file cleanup (keeps 10 most recent)

### CSV Output
- Generates two files: valid and invalid data
- Dual-header format for GHL import compatibility
- Automatic file cleanup (keeps 20 most recent)

### Deployment
- Production runs via cron jobs (`run_cron.sh`, `run_cron_days_back.sh`)
- Uses Python virtual environment at `/home/qntmfitlife/qntmapi/clubauto/myenv`
- Webhook server runs independently as Flask application

## Troubleshooting

### Common Issues
- Missing environment variables: Check `.env` file or system environment
- Rate limiting errors: GHL API limits are strictly enforced
- Data validation failures: Check email/phone format requirements
- Authentication failures: Verify Daxko CLIENT_SECRET is current

### Debug Commands
```bash
# Print environment variables
python print_env.py

# Test with small sample
python main.py --run_csv=True --run_ghl=False --sample_size=1

# Check logs
tail -f logs/process_$(date +%Y%m%d)*.log
```