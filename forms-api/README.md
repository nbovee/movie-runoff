# Google Forms API Server

A Go server that interacts with the Google Forms API to manage and retrieve responses from two forms.

## Prerequisites

- Go 1.21 or higher
- Google Cloud Project with Forms API enabled
- Service Account credentials with appropriate permissions

## Setup

1. Clone the repository
2. Copy `.env.example` to `.env` and update with your credentials:
   ```bash
   cp .env.example .env
   ```
3. Update the `.env` file with:
   - Path to your Google service account credentials JSON file
   - Your form IDs

4. Install dependencies:
   ```bash
   go mod download
   ```

5. Run the server:
   ```bash
   go run main.go
   ```

The server will start on port 8080.

## API Endpoints

### Get Form Responses
```
GET /forms/:formId/responses
```
Retrieves all responses for a specific form.

## Authentication

This application uses Google service account authentication. You'll need to:

1. Create a Google Cloud Project
2. Enable the Google Forms API
3. Create a service account and download the credentials JSON
4. Set the path to your credentials in the `.env` file

## Security Notes

- Never commit your `.env` file or credentials to version control
- Keep your service account credentials secure
- Follow the principle of least privilege when setting up service account permissions 