from datetime import datetime
from src.data_fetcher import DataFetcher
from src.output_handlers.csv_handler import CSVHandler
from src.output_handlers.email_handler import EmailHandler
import sys
import os


# Define input and output field mappings
input_fields = [
    # Basic contact info
    "FirstName",
    "LastName",
    "Email",
    # Phone fields
    "PhoneCell",
    "PhoneHome",
    "PhoneWork",
    # Address fields
    "StreetAddress",
    "City",
    "State",
    "Zip",
    # Membership fields
    "UserGroupName",
    "Status",
    "SystemId",
    # Other fields
    "Gender",
    "OptOutStatus",
    "DeliveryMethod",
]

field_mappings = {
    # Basic contact info
    "FirstName": "firstName",
    "LastName": "lastName",
    "Email": "email",
    # Phone mappings
    "PhoneCell": "phone",
    "PhoneHome": "homePhone",
    "PhoneWork": "workPhone",
    "PhoneCell": "cellPhone",
    # Address mappings
    "StreetAddress": "address1",
    "City": "city",
    "State": "state",
    "Zip": "postal_code",
    # Membership mappings
    "UserGroupName": "membership_type",
    "Status": "member_activeinactive",
    "Status": "member_status",
    "SystemId": "member_number",
    # Other fields
    "Gender": "gender",
    "OptOutStatus": "--OptOutStatus",
    "DeliveryMethod": "--DeliveryMethod",
}

# Define output fields using mapped names
output_fields = list(field_mappings.values())


def main():
    # Generate timestamp once at the start
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")

    # Initialize handlers
    fetcher = DataFetcher()
    csv_handler = CSVHandler()
    email_handler = EmailHandler()

    try:
        # Get access token and fetch data
        data = fetcher.get_data(input_fields)
        if data.get("data"):
            print(f"Successfully fetched {len(data['data'])} records")

            # Write to CSV using timestamp and output_fields
            csv_path = csv_handler.write_csv(
                data["data"], output_fields, timestamp, field_mappings
            )
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
