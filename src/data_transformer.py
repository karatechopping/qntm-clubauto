# src/data_transformer.py

# NOTE - WE END UP WITH membership_type and membership_type_1 which are identical.
# We will be adding logic around this in future so for now, just leave it.
# membership_type is excluded from the CSV


class DataTransformer:
    def __init__(self, field_mappings):
        """
        Initialize the DataTransformer with field mappings.
        :param field_mappings: Combined mappings for standard and custom GHL fields.
        """
        self.field_mappings = field_mappings

    def transform_data(self, raw_data):
        """Transform raw Daxko data into a standardized format."""
        # Group raw data by SystemId to handle duplicates
        grouped_data = {}

        for record in raw_data:
            member_id = record.get("SystemId")
            if not member_id:
                continue

            if member_id not in grouped_data:
                # Initialize new member record with 5 empty membership type slots
                grouped_data[member_id] = {
                    "record": record,
                    "membership_types": [""]
                    * 5,  # Always create 5 membership type slots
                }

            # Add membership type, filling the next available slot
            membership_type = record.get("UserGroupName")
            if membership_type:
                for i in range(5):
                    if grouped_data[member_id]["membership_types"][i] == "":
                        grouped_data[member_id]["membership_types"][i] = membership_type
                        break

        # Transform grouped data into final format
        transformed_data = []

        for member_data in grouped_data.values():
            record = member_data["record"]
            transformed_record = {}

            # Apply all field mappings (both standard and custom)
            for daxko_field, mapping in self.field_mappings.items():
                # Get the value from the record
                value = record.get(daxko_field, "")

                # Handle different mapping types
                if isinstance(mapping, str):
                    # Simple string mapping
                    transformed_record[mapping] = value
                elif isinstance(mapping, list):
                    # Multiple mappings for the same field
                    for map_item in mapping:
                        if isinstance(map_item, str):
                            transformed_record[map_item] = value
                        elif isinstance(map_item, dict):
                            transformed_record[map_item["ghl_field"]] = value
                elif isinstance(mapping, dict):
                    # Single custom field mapping
                    transformed_record[mapping["ghl_field"]] = value

            # Add the 5 membership type fields
            for i in range(5):
                transformed_record[f"membership_type_{i + 1}"] = member_data[
                    "membership_types"
                ][i]

            transformed_data.append(transformed_record)

        return transformed_data
