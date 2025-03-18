from datetime import datetime
from src.data_fetcher import DataFetcher
from src.data_transformer import DataTransformer
from src.output_handlers.csv_handler import CSVHandler
from src.output_handlers.email_handler import EmailHandler
from src.output_handlers.ghl_handler import GHLHandler

# Define the mappings (Daxko -> GHL)
field_mappings = {
    # Standard GHL fields
    "FirstName": "firstName",
    "LastName": "lastName",
    "Email": "email",
    "PhoneCell": [
        "phone",
        {"ghl_field": "cellPhone", "ghl_id": "OzwZRpooGyR8Ayrc84u4"},
    ],
    "StreetAddress": "address1",
    "City": "city",
    "State": "state",
    "Gender": "gender",
    "Zip": ["postalCode", {"ghl_field": "zip", "ghl_id": "TAD26hyktLxWKZa9tOUS"}],
    "PhoneHome": {"ghl_field": "homePhone", "ghl_id": "SCniAw3rl6DU6SH90OJi"},
    "PhoneWork": {"ghl_field": "workPhone", "ghl_id": "vFOXH73DDi9WOabRLsNp"},
    "UserGroupName": {"ghl_field": "membership_type", "ghl_id": "e2f0o6TtMCkoKvLipmrs"},
    "Status": [
        {"ghl_field": "member_activeinactive", "ghl_id": "a42q57p3xl4uSYKThK5C"},
        {"ghl_field": "member_status", "ghl_id": "zsoJAoVViTFLHqgexbLl"},
    ],
    "SystemId": {"ghl_field": "member_number", "ghl_id": "cewzf3ASjgkju43LCaB0"},
    "OptOutStatus": {"ghl_field": "opt_out_status", "ghl_id": "7SXK1pY4CNzPyFndQOAv"},
    "DeliveryMethod": {
        "ghl_field": "delivery_method",
        "ghl_id": "NX3D1NYKLdDmOJYwGlgb",
    },
}

# Generate input_fields for fetcher
input_fields = list(field_mappings.keys())

# Create reverse mapping for CSV row 2
def create_reverse_mapping(field_mappings):
    reverse_map = {}
    for daxko_field, ghl_mapping in field_mappings.items():
        if isinstance(ghl_mapping, str):
            reverse_map[ghl_mapping] = daxko_field
        elif isinstance(ghl_mapping, list):
            # Handle multiple mappings
            for mapping in ghl_mapping:
                if isinstance(mapping, str):
                    reverse_map[mapping] = daxko_field
                elif isinstance(mapping, dict):
                    reverse_map[mapping["ghl_field"]] = daxko_field
        elif isinstance(ghl_mapping, dict):
            reverse_map[ghl_mapping["ghl_field"]] = daxko_field
    return reverse_map

def main():
    print("Starting main function...")
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    print(f"Timestamp created: {timestamp}")

    # Initialize components
    print("Initializing components...")
    fetcher = DataFetcher()
    transformer = DataTransformer(field_mappings)
    csv_handler = CSVHandler(create_reverse_mapping(field_mappings))
    email_handler = EmailHandler()
    ghl_handler = GHLHandler()
    print("Components initialized")

    try:
        # Step 1: Fetch raw data from Daxko
        print("Fetching data from Daxko API...")
        raw_data = fetcher.get_data(input_fields)

        if raw_data.get("data"):
            print(f"Successfully fetched {len(raw_data['data'])} records")

            # Step 2: Transform the data
            print("Transforming data...")
            transformed_data = transformer.transform_data(raw_data["data"])
            print(f"Transformed {len(transformed_data['valid'])} valid contacts")
            print(f"Found {len(transformed_data['invalid'])} invalid contacts")

            # Step 3: Write to CSV
            print("Writing data to CSV...")
            csv_files = csv_handler.write_csv(transformed_data, timestamp)
            print(f"CSV files created: {csv_files}")

            # Step 4: Send email
            print("Sending email with CSV attachments...")
            email_handler.send_report(csv_files, timestamp)
            print("Email sent successfully")

            # Step 5: Update GHL via API (only valid contacts)
            print("Processing contacts in GHL...")
            ghl_results = ghl_handler.process_contacts(transformed_data['valid'])
            print("GHL processing complete")

        else:
            print("No data fetched from the API.")

    except Exception as e:
        print(f"Error during process: {e}")
        raise

if __name__ == "__main__":
    print("Script starting...")
    main()
    print("Script completed")
