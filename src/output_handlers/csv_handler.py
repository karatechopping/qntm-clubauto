# src/output_handlers/csv_handler.py
import csv
from datetime import datetime


class CSVHandler:
    def write_to_csv(self, data, output_fields, filename=None):
        """
        Writes the fetched data to a CSV file.
        """
        if filename is None:
            filename = f"report_data_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.csv"

        try:
            with open(filename, mode="w", newline="", encoding="utf-8") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=output_fields)
                writer.writeheader()
                for row in data:
                    # Ensure that each row contains all the output fields
                    # If a field is missing in a row, it will be written as empty
                    writer.writerow(
                        {field: row.get(field, "") for field in output_fields}
                    )
            print(f"Data successfully written to {filename}")
            return filename
        except IOError as e:
            print(f"Error writing to CSV file: {e}")
            raise
