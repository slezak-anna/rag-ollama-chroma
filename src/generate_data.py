from src.config import settings


DOCUMENTS = {
    "password_policy_2026.md": """---
doc_id: password_policy_2026
title: Password and Account Policy
doc_type: policy
status: active
version: 2.1
year: 2026
system: IAM
audience: all_employees
owner: IT Security
effective_from: 2026-01-01
---

# Password and Account Policy

## Rules for regular employees

A regular employee password must have at least 12 characters. The password should contain lowercase letters, uppercase letters, digits, and special characters.

A regular employee password must be changed every 90 days.

Employees must not share passwords with other people. Passwords must not be written on paper near the workstation or sent through chat applications.

## Rules for administrators

Administrator accounts are privileged accounts. An administrator password must have at least 16 characters.

Multi-factor authentication, also called MFA, is required for administrator accounts at every login.

An administrator password must be changed every 60 days.

Administrators must not use the same password in production systems and test systems.

## Password reset

A user password reset is performed through the self-service portal.

The password reset confirmation code is valid for 10 minutes. After this time, the user must start the reset procedure again.

## Account lockout

After five failed login attempts, a regular user account is locked for 15 minutes.

Administrator account lockout must be reviewed by the Security Operations Center before the account is restored.
""",

    "password_policy_2024_archived.md": """---
doc_id: password_policy_2024_archived
title: Archived Password Policy
doc_type: policy
status: archived
version: 1.4
year: 2024
system: IAM
audience: all_employees
owner: IT Security
effective_from: 2024-01-01
---

# Archived Password Policy

## Historical password requirements

In 2024, a regular employee password had to contain at least 10 characters.

In 2024, passwords were changed every 120 days.

This document is archived and must not be used as the current source for 2026 rules.

## Historical administrator requirements

In 2024, administrator passwords had to contain at least 14 characters.

MFA was required only for remote administrator access.

This rule is no longer current.
""",

    "vpn_access_procedure_2026.md": """---
doc_id: vpn_access_procedure_2026
title: VPN Access Procedure
doc_type: procedure
status: active
version: 3.0
year: 2026
system: VPN
audience: all_employees
owner: IT Operations
effective_from: 2026-02-01
---

# VPN Access Procedure

## VPN requirements

VPN access requires an active company account and enabled MFA.

The user must use a company device or a device approved by the IT department.

The VPN connection is automatically disconnected after 8 hours of active session. A new connection requires MFA confirmation again.

## First VPN connection

To use VPN for the first time, the user should install the VPN client from the IT portal, log in with the company account, and confirm the login with MFA.

The VPN client must be updated before the first connection if the installed version is older than the version published in the IT portal.

## VPN troubleshooting

If the user cannot connect to VPN, the user should check the internet connection, MFA status, and whether the VPN client is up to date.

If the problem still occurs, the user should create a ticket for the Service Desk.

## Administrator VPN access

Administrators may access production systems only through VPN with MFA.

Administrative access is logged and stored for 180 days.

Administrators must not connect to production systems from personal devices.
""",

    "iam_error_catalog_2026.md": """---
doc_id: iam_error_catalog_2026
title: IAM Application Error Catalog
doc_type: technical
status: active
version: 1.8
year: 2026
system: IAM
audience: support
owner: Identity Team
effective_from: 2026-01-15
---

# IAM Application Error Catalog

## ERR_AUTH_401

ERR_AUTH_401 means that the authorization token is missing or invalid.

The user should log in again. If the error still occurs, the user should check device time synchronization and IAM service status.

Support agents should ask whether the error appears after a long idle session or immediately after login.

## ERR_AUTH_403

ERR_AUTH_403 means that the user is correctly logged in but does not have permission to perform the requested operation.

In this case, the user role should be verified in the IAM admin console.

## ERR_MFA_002

ERR_MFA_002 means that MFA verification failed.

The user should try again or reset the MFA method in the self-service portal.

If the error happens repeatedly, support should check whether the user's MFA device is still registered.

## ERR_VPN_118

ERR_VPN_118 means that the VPN client is outdated.

The user should download the latest VPN client from the IT portal.

This error is related to VPN client version, not to the user's IAM role.
""",

    "security_incident_procedure_2026.md": """---
doc_id: security_incident_procedure_2026
title: Security Incident Reporting Procedure
doc_type: procedure
status: active
version: 2.5
year: 2026
system: Security
audience: all_employees
owner: Security Operations Center
effective_from: 2026-01-01
---

# Security Incident Reporting Procedure

## Incident definition

A security incident is any event that may affect confidentiality, integrity, or availability of information.

Examples of incidents include unauthorized access, suspected data leak, malware, phishing, and loss of a company device.

## How to report an incident

A security incident must be reported immediately through the Security Incident Portal or by phone to the SOC team.

The report should include a description of the event, time of occurrence, affected system, and contact details of the reporting person.

## Response time

The SOC team classifies the incident within 30 minutes after receiving the report.

Critical incidents require immediate action after classification.

## Phishing

A suspicious email should be forwarded as an attachment to the SOC team.

The user should not click links or open attachments in a suspicious email.

If the user clicked a suspicious link, the user must report it as a security incident immediately.
""",

    "backup_retention_policy_2026.md": """---
doc_id: backup_retention_policy_2026
title: Backup and Data Retention Policy
doc_type: policy
status: active
version: 4.2
year: 2026
system: Backup
audience: infrastructure
owner: Infrastructure Team
effective_from: 2026-03-01
---

# Backup and Data Retention Policy

## Backup schedule

Backups of production systems are performed daily at 23:00.

Backups of test systems are performed once a week, on Sunday at 02:00.

## Data retention

Backups of production systems are stored for 90 days.

Monthly backups are stored for 12 months.

## Restore test

A backup restore test must be performed at least once per quarter.

The test result is documented in the change management system.

## Encryption

Backups are encrypted at rest and in transit.

The document does not specify a particular encryption algorithm.
""",

    "mfa_user_guide_2026.md": """---
doc_id: mfa_user_guide_2026
title: MFA User Guide
doc_type: guide
status: active
version: 1.3
year: 2026
system: IAM
audience: all_employees
owner: Identity Team
effective_from: 2026-01-10
---

# MFA User Guide

## What MFA is

Multi-factor authentication, called MFA, adds an additional verification step during login.

The company uses MFA to protect access to email, VPN, IAM, and administrator consoles.

## Resetting MFA

A user can reset MFA in the self-service portal after confirming identity with the password reset process.

If the user cannot access the self-service portal, the user must contact Service Desk.

## MFA for administrators

Administrators must use MFA at every login.

Administrators must use a company-approved MFA method. SMS-based MFA is not allowed for administrator accounts.

## Lost MFA device

If a user loses an MFA device, the user must report it to Service Desk immediately.

Service Desk verifies the user's identity before resetting the MFA method.
""",

    "service_desk_faq_2026.md": """---
doc_id: service_desk_faq_2026
title: Service Desk FAQ
doc_type: faq
status: active
version: 1.0
year: 2026
system: Support
audience: support
owner: Service Desk
effective_from: 2026-01-20
---

# Service Desk FAQ

## User cannot log in

If a user cannot log in, ask whether the password is expired, whether the account is locked, and whether MFA verification is working.

If the user sees ERR_AUTH_401, ask the user to log in again and check device time synchronization.

If the user sees ERR_AUTH_403, verify the user's role.

## User cannot connect to VPN

If a user cannot connect to VPN, check internet access, MFA status, and VPN client version.

If the user sees ERR_VPN_118, the VPN client is outdated and must be updated from the IT portal.

## User reports phishing

If a user reports phishing, ask whether the user clicked a link or opened an attachment.

If the user clicked a link, create a security incident immediately.

## User forgot password

If a user forgot the password, guide the user to the self-service portal.

The password reset confirmation code is valid for 10 minutes.
""",

    "access_request_policy_2026.md": """---
doc_id: access_request_policy_2026
title: Access Request Policy
doc_type: policy
status: active
version: 2.0
year: 2026
system: IAM
audience: managers
owner: Identity Team
effective_from: 2026-02-15
---

# Access Request Policy

## Standard access request

A standard access request must be submitted through the Access Portal.

The request must include the business justification, target system, requested role, and manager approval.

## Administrator access request

Administrator access requires manager approval and Security approval.

Administrator access is granted for a maximum of 90 days unless an exception is approved.

## Emergency access

Emergency access may be granted for incident response or urgent production support.

Emergency access expires after 24 hours and must be reviewed after use.
""",
}


def main() -> None:
    settings.DATA_RAW_DIR.mkdir(parents=True, exist_ok=True)

    for old_file in settings.DATA_RAW_DIR.glob("*.md"):
        old_file.unlink()

    for filename, content in DOCUMENTS.items():
        path = settings.DATA_RAW_DIR / filename
        path.write_text(content.strip() + "\n", encoding="utf-8")

    print(f"Generated {len(DOCUMENTS)} English documents in {settings.DATA_RAW_DIR}")


if __name__ == "__main__":
    main()