# Security Policy

## Supported Versions

The following versions of the Crowd Management System are currently being supported with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability within this project, please send an email to [INSERT CONTACT EMAIL] instead of using the issue tracker.

All security vulnerabilities will be promptly addressed.

Please do not publicly disclose the vulnerability until it has been addressed by the team.

## Security Considerations

This application processes video feeds from cameras and stores detection data locally. The following security considerations should be noted:

1. **Data Storage**: All detection data is stored locally in an SQLite database. Ensure proper file permissions are set on the database file.

2. **Camera Access**: The application requires access to camera devices. Only grant camera permissions to trusted versions of the application.

3. **Network Access**: The application does not require network access for basic functionality. Any network requests are only made for optional features like cloud integration.

4. **Local Execution**: The application runs entirely locally and does not transmit data to external servers by default.

## Best Practices

To ensure the security of your installation:

1. Download the application only from official sources
2. Verify the integrity of downloaded files when possible
3. Keep your system and dependencies up to date
4. Regularly review camera permissions
5. Protect the database file with appropriate file system permissions