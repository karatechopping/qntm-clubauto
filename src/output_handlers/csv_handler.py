import csv
import os


class CSVHandler:
    def __init__(self, reverse_mapping):
        """
        Initialize the CSVHandler with the reverse mapping (GHL -> Daxko).
        :param reverse_mapping: A dictionary that maps GHL fields to Daxko fields
                                for use in the second CSV header row.
        """
        self.reverse_mapping = reverse_mapping

    def write_csv(self, transformed_data, timestamp):
        """
        Write transformed data to a CSV file while excluding certain fields.
        :param transformed_data: The transformed data.
        :param timestamp: Timestamp string for naming the CSV file.
        :return: Path to the created CSV file.
        """
        # Exclude these fields from the CSV (e.g., "membership_type")
        excluded_fields = {"membership_type"}

        # Get fieldnames by filtering out excluded fields
        all_fieldnames = transformed_data[0].keys() if transformed_data else []
        fieldnames = [field for field in all_fieldnames if field not in excluded_fields]

        filename = f"transformed_data_{timestamp}.csv"

        try:
            with open(filename, mode="w", newline="", encoding="utf-8") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                # Write GHL header row (row 1)
                writer.writeheader()

                # Write reverse mapping header row (row 2)
                reverse_headers = {
                    ghl_field: self.reverse_mapping.get(ghl_field, ghl_field)
                    for ghl_field in fieldnames
                }
                writer.writerow(reverse_headers)

                # Write all transformed data rows
                for row in transformed_data:
                    # Exclude unwanted fields from the row
                    filtered_row = {
                        k: v for k, v in row.items() if k not in excluded_fields
                    }
                    writer.writerow(filtered_row)

                print(f"Data successfully written to {filename}")
                return filename

        except ValueError as e:
            print(f"Error: {e}")
            raise

        except IOError as e:
            print(f"Error writing CSV file: {e}")
            raise
