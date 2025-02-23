field_mappings = {
    # Basic contact info
    "FirstName": "firstName",
    "LastName": "lastName",
    "Email": "email",

    # Phone mappings
    "PhoneCell": "phone",          # Primary phone in GHL
    "PhoneHome": "homePhone",
    "PhoneWork": "workPhone",
    "PhoneCell": "cellPhone",      # NOTE: PhoneCell used twice - as primary and cell

    # Address mappings
    "StreetAddress": "address1",
    "City": "city",
    "State": "state",
    "Zip": "postal_code",
    # NOTE: Daxko doesn't seem to have country field - might need to hardcode

    # Membership mappings
    "UserGroupName": "membership_type",    # From Daxko userGroup section
    "Status": "member_activeinactive",     # NOTE: Status used twice - might need logic
    "Status": "member_status",             # NOTE: Same Daxko field, different GHL field
    "SystemId": "member_number",           # Best match for member number?

    # Other fields
    "Gender": "gender",
    "OptOutStatus": "optOutStatus"
}
