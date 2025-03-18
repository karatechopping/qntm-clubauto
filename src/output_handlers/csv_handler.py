# src/output_handlers/csv_handler.py
import csv
import os
import logging

class CSVHandler:
    def __init__(self, reverse_mapping):
        """
        Initialize the CSVHandler with the reverse mapping (GHL -> Daxko).
        :param reverse_mapping: A dictionary that maps GHL fields to Daxko fields
                                for use in the second CSV header row.
        """
        self.logger = logging.getLogger(__name__)
        self.reverse_mapping = reverse_mapping

        # Create csv directory if it doesn't exist
        if not os.path.exists('csv'):
            os.makedirs('csv')
            self.logger.info("Created 'csv' directory")

    def write_csv(self, data_dict, timestamp):
        """
        Write transformed data to CSV files, separating valid and invalid records.
        :param data_dict: Dictionary containing 'valid' and 'invalid' record lists
        :param timestamp: Timestamp string for naming the CSV files
        :return: List of written file paths
        """
        valid_filename = f"transformed_data_{timestamp}.csv"
        invalid_filename = f"invalid_data_{timestamp}.csv"

        files_written = []

        # Process valid records
        if data_dict['valid']:
            valid_file = self._write_single_csv(data_dict['valid'], valid_filename)
            files_written.append(valid_file)

        # Process invalid records
        if data_dict['invalid']:
            invalid_file = self._write_single_csv(data_dict['invalid'], invalid_filename)
            files_written.append(invalid_file)

        return files_written

    def _write_single_csv(self, transformed_data, filename):
        """
        Helper method to write a single CSV file.
        """
        # Create full filepath in csv directory
        filepath = os.path.join('csv', filename)

        # Exclude these fields from the CSV
        excluded_fields = {"membership_type"} | {
            k
            for k in (transformed_data[0].keys() if transformed_data else [])
            if k.endswith("_id")
        }

        # Get fieldnames by filtering out excluded fields
        all_fieldnames = transformed_data[0].keys() if transformed_data else []
        fieldnames = [field for field in all_fieldnames if field not in excluded_fields]

        try:
            with open(filepath, mode="w", newline="", encoding="utf-8") as csvfile:
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

                self.logger.info(f"Data successfully written to {filepath}")
                return filepath

        except ValueError as e:
            self.logger.error(f"Error: {e}")
            raise

        except IOError as e:
            self.logger.error(f"Error writing CSV file: {e}")
            raise
