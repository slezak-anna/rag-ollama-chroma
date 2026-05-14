from src.config import settings


DOCUMENTS = {
    "password_policy_2026.md": """---
doc_id: password_policy_2026
title: Password and User Account Policy
doc_type: policy
year: 2026
department: IT Security
---

# Password and User Account Policy

## Requirements for regular employees

A regular employee's password must be at least 12 characters long. The password should contain lowercase letters, uppercase letters, digits, and special characters. The user's password must be changed every 90 days.

An employee must not share their password with other people. The password must not be written on notes near the workstation or sent through messaging applications.

## Requirements for administrators

Administrator accounts are privileged accounts. An administrator's password must be at least 16 characters long. MFA is required for administrator accounts at every login.

An administrator's password must be changed every 60 days. An administrator must not use the same password in production and test systems.

## Password reset

A user's password is reset through the self-service portal. The confirmation code for password reset is valid for 10 minutes.
""",

    "vpn_access_procedure_2026.md": """---
doc_id: vpn_access_procedure_2026
title: VPN Access Procedure
doc_type: procedure
year: 2026
department: IT Operations
---

# VPN Access Procedure

## Conditions for using VPN

VPN access requires an active company account and enabled MFA. The user must use a company device or a device approved by the IT department.

The VPN connection is automatically disconnected after 8 hours of an active session. Reconnecting requires MFA confirmation again.

## VPN issues

If a user cannot connect to the VPN, they should check the internet connection, MFA status, and whether the VPN client is up to date. If the issue still occurs, a ticket should be submitted to the Service Desk.

## Administrator access through VPN

Administrators may access production systems only through VPN with MFA. Administrative access is logged and stored for 180 days.
""",

    "security_incident_procedure_2026.md": """---
doc_id: security_incident_procedure_2026
title: Security Incident Reporting Procedure
doc_type: procedure
year: 2026
department: Security
---

# Security Incident Reporting Procedure

## Definition of an incident

A security incident is any event that may compromise the confidentiality, integrity, or availability of information. Examples of incidents include unauthorized access, suspected data leakage, malware, phishing, and loss of a company device.

## How to report an incident

An incident must be reported immediately through the Security Incident Portal form or by phone to the SOC team. The report should include a description of the event, the time it occurred, the affected system, and the details of the reporting person.

## Response time

The SOC team classifies the report within 30 minutes of receiving it. Critical incidents require immediate action after classification.
""",

    "backup_retention_2026.md": """---
doc_id: backup_retention_2026
title: Backup and Data Retention Policy
doc_type: policy
year: 2026
department: Infrastructure
---

# Backup and Data Retention Policy

## Backup schedule

Backups of production systems are performed daily at 23:00. Backups of test systems are performed once a week, on Sunday at 02:00.

## Data retention

Backups of production systems are stored for 90 days. Monthly backups are stored for 12 months.

## Restore test

A backup restore test must be performed at least once per quarter. The test result is documented in the change management system.

## Encryption

Backups are encrypted at rest and in transit. The document does not specify a particular encryption algorithm.
""",

    "iam_application_errors_2026.md": """---
doc_id: iam_application_errors_2026
title: IAM Application Error Catalog
doc_type: technical
year: 2026
department: Identity
---

# IAM Application Error Catalog

## ERR_AUTH_401

ERR_AUTH_401 means that a valid authorization token is missing. The user should log in again. If the error still occurs, the device time synchronization and IAM service status should be checked.

## ERR_AUTH_403

ERR_AUTH_403 means that the user is correctly logged in but does not have permission to perform the given operation. In this case, the user's role should be verified.

## ERR_MFA_002

ERR_MFA_002 means a failed MFA verification. The user should try again or reset the MFA method in the self-service portal.

## ERR_VPN_118

ERR_VPN_118 means that the VPN client is outdated. The user should download the latest version of the VPN client from the IT portal.
""",

    "password_policy_2024.md": """---
doc_id: password_policy_2024
title: Old Password Policy
doc_type: policy
year: 2024
department: IT Security
---

# Old Password Policy

## Historical requirements

In 2024, a regular employee's password had to be at least 10 characters long. The password was changed every 120 days.

This document is a historical version and should not be used as the current source of rules for 2026.
""",
}


def main() -> None:
    settings.DATA_RAW_DIR.mkdir(parents=True, exist_ok=True)

    for filename, content in DOCUMENTS.items():
        path = settings.DATA_RAW_DIR / filename
        path.write_text(content.strip() + "\n", encoding="utf-8")

    print(f"Created {len(DOCUMENTS)} documents in: {settings.DATA_RAW_DIR}")


if __name__ == "__main__":
    main()