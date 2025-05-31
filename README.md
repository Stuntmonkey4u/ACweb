# AzerothCore Account Management API & Frontend

This project provides a FastAPI backend and a React frontend for managing AzerothCore user accounts, focusing on LAN-first usability with optional online features.

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Running the Application](#running-the-application)
- [Configuration (Environment Variables)](#configuration-environment-variables)
- [Offline vs. Online Functionality](#offline-vs-online-functionality)
- [Key Dependencies](#key-dependencies)
- [API Endpoints](#api-endpoints)
- [Contributing](#contributing)

## Features

*   **User Account Management:** Register, login, change password.
*   **Email Verification (Online-Only):** Accounts can be marked as verified if an email is successfully sent and the user clicks the verification link.
*   **TOTP-based 2FA (Offline-Capable):** Secure your account with Time-based One-Time Passwords. Secrets are stored in a local auxiliary SQLite database.
*   **Offline-Friendly CAPTCHA:** Math-based CAPTCHA to protect registration and password reset endpoints, fully functional offline.
*   **Rate Limiting:** Protects key authentication and utility endpoints. Uses Redis for distributed rate limiting if available, with an in-memory fallback per instance.
*   **Password Reset Request:** (Currently offline handling, email sending for reset link is TBD).
*   **Dockerized:** Easy setup with Docker Compose.
*   **LAN-First Focus:** Core features are designed to work without internet access.

## Architecture

*   **Backend:** FastAPI (Python)
    *   MySQL Database: Stores main account data (e.g., `ac_auth.account`).
    *   SQLite Database: Stores auxiliary data for features like 2FA secrets and CAPTCHA challenges (`app_data.sqlite` by default).
*   **Frontend:** React (Vite)
*   **Containerization:** Docker and Docker Compose.

## Getting Started

### Prerequisites

*   Docker and Docker Compose
*   A running MySQL server accessible to the backend (or use the one included in `docker-compose.yml`).
*   Node.js and npm/yarn if you plan to modify frontend code directly.

### Running the Application

1.  **Clone the repository.**
2.  **Configure Environment Variables:**
    *   Create a `.env` file in the `backend/` directory by copying from `.env.example` (if provided) or by using the list in the [Configuration](#configuration-environment-variables) section below.
    *   Update the MySQL connection details (`DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`, `DB_PORT`) in `backend/.env` to point to your AzerothCore `ac_auth` database. If using the provided `docker-compose.yml`'s MySQL service, the defaults might work but ensure the database `ac_auth` exists.
3.  **Run with Docker Compose:**
    ```bash
    docker-compose up --build
    ```
4.  **Access:**
    *   Frontend: `http://localhost:3000` (or your configured port)
    *   Backend API Docs: `http://localhost:8000/docs` (or your configured port)

The auxiliary SQLite database (e.g., `backend/app_data.sqlite`) will be created automatically on startup if it doesn't exist. Database tables for both MySQL (if `init_db` is effective) and SQLite will also be created/updated.

## Configuration (Environment Variables)

Create a `.env` file in the `backend/` directory. Example:

```env
# Main Database (MySQL)
DB_HOST=localhost
DB_USER=acore
DB_PASSWORD=acore
DB_NAME=ac_auth
DB_PORT=3306

# JWT Settings
SECRET_KEY=your_super_secret_key_please_change_this_for_production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440 # 24 hours

# Auxiliary Database (SQLite)
AUX_DB_NAME="app_data.sqlite"

# Application Settings
APP_NAME="AzerothCore Manager" # Used for TOTP issuer name
FRONTEND_URL="http://localhost:3000" # For constructing email verification links

# --- Optional Features ---

# Email Service (for Email Verification - Online Mode)
# If these are not set, email verification emails will not be sent.
SMTP_HOST=
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=
SMTP_SENDER_EMAIL=
EMAIL_VERIFICATION_URL_LIFESPAN_SECONDS=3600 # 1 hour

# Rate Limiting Storage (Redis - Optional)
# If REDIS_HOST is not set, rate limiting falls back to in-memory per instance.
REDIS_HOST=
REDIS_PORT=6379

# Rate Limiting Behavior
RATE_LIMIT_ENABLED=True # Set to False to disable all rate limits
RATE_LIMIT_DEFAULT="100/minute"
RATE_LIMIT_LOGIN="20/minute"
RATE_LIMIT_REGISTER="10/hour"
RATE_LIMIT_PASSWORD_RESET="10/hour"
RATE_LIMIT_VERIFY_EMAIL_CONFIRM="20/minute" # For /verify-email endpoint (token confirmation)
RATE_LIMIT_2FA_SETUP="10/hour"
RATE_LIMIT_2FA_ENABLE_DISABLE="10/minute"
RATE_LIMIT_CAPTCHA_GENERATE="60/minute"
```

**Notes:**

*   `SECRET_KEY`: **CRITICAL** for security. Generate a strong, random key for production.
*   `SMTP_HOST`, `SMTP_PORT`, etc.: Only required if you want to enable email verification. The application remains functional for core account management and 2FA setup/login without these.
*   `REDIS_HOST`: If you have a Redis server, providing its host here will enable more robust, distributed rate limiting. Otherwise, rate limits are per-instance and reset on restart.

## Offline vs. Online Functionality

*   **Core Account Management (Login, Register, Password Change):** Fully offline capable.
*   **Email Verification:**
    *   **Online:** If SMTP settings are configured and the server can connect to the SMTP host, verification emails will be sent.
    *   **Offline:** If SMTP is not configured or the server is offline, emails are not sent. Accounts can still be created and used but will remain in an "unverified" email status.
*   **TOTP-based 2FA:** Fully offline capable. Secrets are stored in the local auxiliary SQLite database.
*   **CAPTCHA:** Fully offline capable. Challenges are managed in the local auxiliary SQLite database.
*   **Rate Limiting:**
    *   **With Redis:** If `REDIS_HOST` is configured and the Redis server is reachable, rate limits are shared across all instances (if scaled) and persist.
    *   **Without Redis (In-Memory Fallback):** Rate limits are tracked in memory for each instance of the backend. Limits do not persist across restarts and are not shared between multiple instances.

## Key Dependencies

### Backend

*   **FastAPI:** Modern, fast web framework for building APIs.
*   **SQLAlchemy:** SQL toolkit and Object Relational Mapper (ORM).
*   **Pydantic:** Data validation and settings management.
*   **MySQL Connector (`mysqlclient` or `mysql-connector-python`):** For MySQL database interaction.
*   **Passlib & python-jose:** For password hashing and JWT handling.
*   **pyotp:** For generating and verifying TOTP codes (2FA).
*   **qrcode[pil]:** For generating QR codes for 2FA setup.
*   **slowapi & limits:** For rate limiting API endpoints.
*   **redis:** Python client for Redis (used by `slowapi` if configured).

A full list is in `backend/requirements.txt`.

### Frontend

*   **React:** JavaScript library for building user interfaces.
*   **Vite:** Fast frontend build tool.
*   **Tailwind CSS:** Utility-first CSS framework for styling.
*   **apiClient (custom):** Wrapper around `fetch` for API communication.

A full list is in `frontend/package.json` and can be installed via `npm install` or `yarn install`.

## API Endpoints

The main API endpoints are exposed under the `/api/auth/` prefix. Refer to the auto-generated OpenAPI documentation available at `/docs` on the running backend (e.g., `http://localhost:8000/docs`) for a detailed list of endpoints, request/response models, and testing capabilities.

Key new endpoints include:
*   `/api/auth/2fa/setup`
*   `/api/auth/2fa/enable`
*   `/api/auth/2fa/disable`
*   `/api/auth/captcha/generate`
*   `/api/auth/verify-email` (for confirming email after clicking link)

## Contributing

Contributions are welcome! Please follow standard fork-and-pull-request workflow. Ensure code is formatted, tested (if applicable), and adheres to the project's goals.
(Further contribution guidelines can be added here).
