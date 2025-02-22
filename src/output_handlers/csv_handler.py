import csv
import os
from datetime import datetime


class CSVHandler:
    def write_csv(self, data, output_fields, timestamp, field_mappings):
        filename = f"report_data_{timestamp}.csv"
        try:
            with open(filename, mode="w", newline="", encoding="utf-8") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=output_fields)
                writer.writeheader()

                for row in data:
                    # Map the fields using the field_mappings dictionary
                    mapped_row = {
                        field_mappings[key]: value
                        for key, value in row.items()
                        if key in field_mappings
                    }
                    writer.writerow(mapped_row)

            print(f"Data successfully written to {filename}")
            return filename

        except IOError as e:
            print(f"Error writing to CSV file: {e}")
            raise
