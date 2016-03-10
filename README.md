# pipe-to-sheet
Simple utility which reads CSV data via stdin and creates a Google Sheet containing that data.

This tool is still very much a work in progress.

## Usage
First, create a service account for Google Drive (https://developers.google.com/identity/protocols/OAuth2ServiceAccount#creatinganaccount).
Place service account credentials in `~/.gs/credentials.json`. Content should look like:

```
{
    "type": "service_account",
    "private_key_id": "...",
    "private_key": "...",
    "client_email": "...",
    "client_id": "...",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://accounts.google.com/o/oauth2/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "..."
}
```

Now you can use the gs.py utility like so:

`./prog-which-ouputs-csv > python gs.py`

A link to the generated Google Sheet will by printed once the utility is finished.
