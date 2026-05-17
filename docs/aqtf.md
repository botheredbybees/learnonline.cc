# AQTF Integration

## What is AQTF?

The Australian Quality Training Framework defines the structure of nationally recognised vocational training. Data is published at [training.gov.au](https://training.gov.au) and accessible via a SOAP API.

## Data Hierarchy

```
Training Package (e.g. MSF — Furnishing)
  ├── Qualification (e.g. MSF30122 — Cert III in Cabinet Making)
  ├── Skillset
  └── Unit of Competency (e.g. MSFFI2001 — Install floor coverings)
        ├── Element (broad competency areas, e.g. "1. Prepare for installation")
        │     └── Performance Criteria (specific observable actions)
        ├── Knowledge Evidence (what the student must know — maps to M3 Scenario Cards)
        ├── Performance Evidence (what the student must do)
        └── Required Skills (underpinning skills and knowledge)
```

## TGA SOAP API

Credentials (public read-only, no account needed):
- Username: `WebService.Read`
- Password: `Asdf098`
- Endpoint: `https://ws.sandbox.training.gov.au/Deewr.Tga.Webservices/TrainingComponentServiceV12.svc`

Client code: `backend/services/tga/client.py`

## Syncing Data

From the admin UI: **Admin → TGA Sync → select training packages → Import**.

From the command line:
```bash
python backend/scripts/tga_utils.py parse --unit MSFFI2001
python backend/scripts/tga_utils.py process-local   # process downloaded XML files
```

XML files can be downloaded from [training.gov.au](https://training.gov.au) manually and placed in `tgaWebServiceKit-2021-12-01/` (not in git).

## Database Tables

| Table | Description |
|-------|-------------|
| `training_packages` | Top-level packages (MSF, BSB, etc.) |
| `qualifications` | Certificates, Diplomas |
| `skillsets` | Industry skillsets |
| `units` | Units of competency |
| `unit_elements` | Elements within a unit |
| `unit_performance_criteria` | Performance criteria within an element |
| `unit_critical_aspects` | Knowledge Evidence items (M3 Scenario Cards) |
| `unit_required_skills` | Underpinning skills and knowledge |
