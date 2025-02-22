from datetime import datetime
from src.data_fetcher import DataFetcher
from src.output_handlers.csv_handler import CSVHandler
from src.output_handlers.email_handler import EmailHandler
import sys
import os

# Define output fields
output_fields = [
    "FirstName",
    "LastName",
    "Email",
    "PhoneCell",
    "Gender",
    "Status",
    "OptOutStatus",
]


def main():
    # Generate timestamp once at the start
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")

    # Initialize handlers
    fetcher = DataFetcher()
    csv_handler = CSVHandler()
    email_handler = EmailHandler()

    try:
        # Get access token and fetch data
        data = fetcher.get_data()
        if data.get("data"):
            print(f"Successfully fetched {len(data['data'])} records")

            # Write to CSV using timestamp and output_fields
            csv_path = csv_handler.write_csv(data["data"], output_fields, timestamp)
            print(f"Data written to {csv_path}")

            # Send email with same timestamp
            email_handler.send_report(csv_path, timestamp)

        else:
            print("No data returned from API")
            sys.exit(1)

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
