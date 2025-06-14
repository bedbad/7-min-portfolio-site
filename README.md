# Resume Request HTTPS Server

A production-ready HTTPS web server that collects email addresses for resume requests.

## Installation

1. Install the package using uv:
```bash
uv pip install .
```

2. Generate SSL certificates (for production, use a proper certificate authority):
```bash
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365
```

## Running in Production

The server is configured to run with Gunicorn, which provides:
- Multiple worker processes
- Process management
- Production-grade logging
- SSL/TLS support

To run the server using uv:

```bash
uv run gunicorn "server:create_app()" --config pyproject.toml
```

Or using the installed script:

```bash
uv run resume-server
```

The server will start on https://0.0.0.0:8443

## Features

- HTTPS secure connection
- Production-grade server (Gunicorn)
- Multiple worker processes
- Proper logging with rotation
- Simple email collection form
- Asynchronous request handling
- Modern UI with responsive design
- Client-side form validation
- Error handling and logging

## Production Considerations

1. SSL Certificates:
   - Use proper SSL certificates from a trusted certificate authority
   - Keep certificates secure and regularly updated

2. Security:
   - Implement rate limiting
   - Add CSRF protection
   - Configure proper security headers
   - Use secure cookie settings

3. Monitoring:
   - Set up proper monitoring and alerting
   - Monitor server resources
   - Set up error tracking

4. Email Sending:
   - Implement proper email sending functionality
   - Use a reliable email service provider
   - Handle email sending failures gracefully

5. Backup:
   - Regularly backup logs and data
   - Have a disaster recovery plan

## Logging

Logs are written to `app.log` with rotation (10MB per file, keeping 5 backup files).
Access and error logs are also handled by Gunicorn.
