import csv
import os
from datetime import datetime


class CSVHandler:
    def __init__(self, num_membership_types=5):
        self.num_membership_types = num_membership_types

    def write_csv(self, data, output_fields, timestamp, field_mappings):
        filename = f"report_data_{timestamp}.csv"

        # Create reverse mapping for Daxko headers
        reverse_mappings = {v: k for k, v in field_mappings.items()}

        # Modify output fields to include multiple membership types
        modified_output_fields = []
        for field in output_fields:
            if field == "membership_type":
                for i in range(1, self.num_membership_types + 1):
                    modified_output_fields.append(f"membership_type_{i}")
            else:
                modified_output_fields.append(field)

        try:
            with open(filename, mode="w", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)  # Use regular writer for custom headers

                # Write GHL headers (Row 1)
                writer.writerow(modified_output_fields)

                # Write Daxko headers (Row 2)
                daxko_headers = []
                for field in modified_output_fields:
                    if field.startswith("membership_type_"):
                        daxko_headers.append("UserGroupName")
                    else:
                        daxko_headers.append(reverse_mappings.get(field, field))
                writer.writerow(daxko_headers)

                # Switch to DictWriter for data rows
                dict_writer = csv.DictWriter(csvfile, fieldnames=modified_output_fields)

                # Group data by member ID
                grouped_data = {}
                for row in data:
                    member_id = row.get("SystemId")
                    if member_id not in grouped_data:
                        # Initialize new member record with empty membership types
                        mapped_row = {field: "" for field in modified_output_fields}
                        # Map non-membership fields
                        for key, value in row.items():
                            if key in field_mappings:
                                mapped_field = field_mappings[key]
                                if mapped_field != "membership_type":
                                    mapped_row[mapped_field] = value
                        # Add first membership type
                        mapped_row["membership_type_1"] = row.get("UserGroupName", "")
                        grouped_data[member_id] = {
                            "row": mapped_row,
                            "membership_count": 1,
                        }
                    else:
                        # Add additional membership type if count is within limit
                        count = grouped_data[member_id]["membership_count"]
                        if count < self.num_membership_types:
                            field_name = f"membership_type_{count + 1}"
                            grouped_data[member_id]["row"][field_name] = row.get(
                                "UserGroupName", ""
                            )
                            grouped_data[member_id]["membership_count"] += 1

                # Write combined data
                for member_data in grouped_data.values():
                    dict_writer.writerow(member_data["row"])

                print(f"Data successfully written to {filename}")
                return filename

        except IOError as e:
            print(f"Error writing to CSV file: {e}")
            raise
        except Exception as e:
            print(f"Unexpected error while writing CSV: {e}")
            raise
