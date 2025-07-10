# QNTM Club Auto Data Integration

A Python application for syncing member data between Daxko and GoHighLevel (GHL), with CSV export and email notifications.

## Features

- Fetches member data from Daxko API
- Transforms data to match GHL field structure  
- Outputs to CSV export and/or direct GHL API integration
- Email notifications with CSV attachments
- Real-time webhook processing
- Rate limiting and error handling
- Automatic file cleanup

## Quick Start

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set environment variables**:
   ```bash
   export CLIENT_SECRET=your_daxko_client_secret
   export GHL_API=your_ghl_api_key
   export GHL_LOCATION=your_ghl_location_id
   ```

3. **Run the application**:
   ```bash
   # CSV export only (safe for testing)
   python main.py --run_csv=True --run_ghl=False --run_email=False --sample_size=10
   
   # Full sync to GHL
   python main.py --run_csv=True --run_ghl=True --run_email=False --sample_size=-1
   ```

## Usage Examples

### CSV Export Only
```bash
python main.py --run_csv=True --run_ghl=False --run_email=False --sample_size=10
```

### Sync Recent Changes (1 day back)
```bash
python main.py --run_csv=True --run_ghl=True --run_email=False --days_back=1
```

### Email Report with CSV
```bash
python main.py --run_csv=True --run_ghl=False --run_email=True --attach_csv=True
```

## Configuration

### Required Environment Variables

- `CLIENT_SECRET`: Daxko API client secret
- `GHL_API`: GoHighLevel API key  
- `GHL_LOCATION`: GoHighLevel location ID

### Optional Email Variables

- `SMTP_SERVER`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`
- `EMAIL_FROM`, `EMAIL_TO`

## Command Line Options

- `--run_csv`: Generate CSV files (True/False)
- `--run_ghl`: Sync to GoHighLevel (True/False)  
- `--run_email`: Send email reports (True/False)
- `--attach_csv`: Attach CSV to email (True/False)
- `--sample_size`: Limit records processed (-1 for all)
- `--days_back`: Process recent changes only (number of days)
- `--run_log`: Enable logging (True/False)

## Output Files

- **CSV files**: Stored in `csv/` directory
- **Log files**: Stored in `logs/` directory
- **Valid data**: `transformed_data_TIMESTAMP.csv`
- **Invalid data**: `invalid_data_TIMESTAMP.csv`

## Project Structure

```
qntm-clubauto/
├── main.py                 # Main execution script
├── src/
│   ├── data_fetcher.py     # Daxko API integration
│   ├── data_transformer.py # Data mapping and validation
│   ├── logger_config.py    # Logging configuration
│   └── output_handlers/
│       ├── csv_handler.py  # CSV generation
│       ├── email_handler.py # Email notifications
│       └── ghl_handler.py  # GHL API integration
├── webhook_handler.py      # Real-time webhook processing
├── run_cron.sh            # Production cron script
└── run_cron_days_back.sh  # Incremental sync script
```

## Safety Features

- Email/phone validation prevents invalid data
- Rate limiting respects API constraints
- Sample size limits for testing
- Automatic file cleanup
- Comprehensive logging
- Retry logic with exponential backoff

## Support

For issues or questions, check the logs in the `logs/` directory or run with `--sample_size=1` to test with minimal data.