@echo off
:: This script sets up Google Cloud authentication with necessary scopes for the Forms API
:: It uses the client.json credentials file and sets up application default credentials

gcloud auth application-default login ^
    --client-id-file=client.json ^
    --scopes=^
https://www.googleapis.com/auth/drive,^
https://www.googleapis.com/auth/drive.file,^
https://www.googleapis.com/auth/drive.readonly,^
https://www.googleapis.com/auth/forms.body,^
https://www.googleapis.com/auth/forms.body.readonly,^
https://www.googleapis.com/auth/forms.responses.readonly,^
https://www.googleapis.com/auth/cloud-platform
