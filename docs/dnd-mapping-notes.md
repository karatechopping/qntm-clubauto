# DND (Do Not Disturb) Mapping Notes

## Potential Daxko to GHL DND Mappings

### Relevant Daxko Fields
- `OptOutStatus`: (0=No, 1=Yes)
- `DeliveryMethod`: (none, email, mail)
- `Status`: Member status
- `UserGroupStatus`: Group status

### GHL DND Structure
DND can be set:
- Globally (`dnd: true/false`)
- Per channel (Email, SMS, Call, etc.)
- With custom messages and codes

### Future Implementation Ideas
1. Map `OptOutStatus=1` to Email DND
2. Use `DeliveryMethod=none` for additional restrictions
3. Consider member status for automated communication rules



## Source Data Schemas

### Daxko Relevant Fields
{
    "OptOutStatus": {
        "example": {
            "user": {
                "optOutStatus": "1"
            }
        },
        "options": {
            "0": "Opt-out Status: No",
            "1": "Opt-out Status: Yes"
        }
    },
    "DeliveryMethod": {
        "example": {
            "user": {
                "deliveryMethod": ["none"]
            }
        },
        "options": {
            "none": "None",
            "email": "Email",
            "mail": "Mail"
        }
    }
}

### GHL DND Schema
{
    "dnd": true,
    "dndSettings": {
        "Call": {
            "status": "active",
            "message": "string",
            "code": "string"
        },
        "Email": {
            "status": "active",
            "message": "string",
            "code": "string"
        },
        "SMS": {
            "status": "active",
            "message": "string",
            "code": "string"
        },
        "WhatsApp": {
            "status": "active",
            "message": "string",
            "code": "string"
        },
        "GMB": {
            "status": "active",
            "message": "string",
            "code": "string"
        },
        "FB": {
            "status": "active",
            "message": "string",
            "code": "string"
        }
    },
    "inboundDndSettings": {
        "all": {
            "status": "active",
            "message": "string"
        }
    }
}

## Potential Mappings

### Direct Mappings
1. If Daxko `OptOutStatus = 1`:
{
    "dnd": true,
    "dndSettings": {
        "Email": {
            "status": "active",
            "message": "Member opted out via Daxko",
            "code": "DAXKO_OPTOUT"
        }
    }
}

2. If Daxko `DeliveryMethod = none`:
{
    "dnd": false,
    "dndSettings": {
        "Email": {
            "status": "active",
            "message": "Member prefers no email delivery",
            "code": "DAXKO_NO_EMAIL"
        }
    }
}

## TODO
- [ ] Decide on message templates for each channel
- [ ] Define channel-specific rules based on Daxko status
- [ ] Create status-based automation rules
- [ ] Determine if we need global DND based on combination of Daxko fields
- [ ] Define handling for other channels (SMS, Call, etc.)
