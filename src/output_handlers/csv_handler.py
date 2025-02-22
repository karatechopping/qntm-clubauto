import csv
import os
from datetime import datetime


class CSVHandler:
    def write_csv(self, data, output_fields, timestamp):
        filename = f"report_data_{timestamp}.csv"
        try:
            with open(filename, mode="w", newline="", encoding="utf-8") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=output_fields)
                writer.writeheader()

                # Debug print to see what we're getting
                print(f"Number of records received: {len(data)}")
                print(f"First record sample: {next(iter(data))}")

                for row in data:
                    filtered_row = {
                        field: row.get(field, "") for field in output_fields
                    }
                    writer.writerow(filtered_row)

            print(f"Data successfully written to {filename}")
            return filename

        except IOError as e:
            print(f"Error writing to CSV file: {e}")
            raise
