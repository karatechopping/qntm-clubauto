from src.data_fetcher import DataFetcher
from src.output_handlers.csv_handler import CSVHandler


def main():
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

    fetcher = DataFetcher()
    csv_handler = CSVHandler()

    try:
        data = fetcher.get_data()
        if data.get("data"):
            print(f"Total records fetched: {len(data['data'])}")
            csv_file = csv_handler.write_to_csv(data["data"], output_fields)
            print(f"CSV file created: {csv_file}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
