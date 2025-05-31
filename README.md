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
- [Admin Functionality (GM Level Based)](#admin-functionality-gm-level-based)
- [Client Download Page Feature](#client-download-page-feature)
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
*   **Basic Admin Panel:** User listing and account banning/unbanning. Admin status is based on the in-game `gmlevel`.
*   **Client Download Page:** Provides authenticated users with links to download game clients, with placeholder LAN detection.
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
3.  **Initial Admin Setup (Manual):**
    *   After the first user is registered, you may need to manually set their GM level to 3 or higher to access the admin panel. See the [Admin Functionality (GM Level Based)](#admin-functionality-gm-level-based) section for details.
4.  **Run with Docker Compose:**
    ```bash
    docker-compose up --build
    ```
5.  **Access:**
    *   Frontend: `http://localhost:3000` (or your configured port)
    *   Backend API Docs: `http://localhost:8000/docs` (or your configured port)

The auxiliary SQLite database (e.g., `backend/app_data.sqlite`) will be created automatically on startup if it doesn't exist. Database tables for both MySQL (if `init_db` is effective) and SQLite will also be created/updated. The application now uses the standard `gmlevel` field from the `account` table for admin privileges. Ensure your database schema is up to date.

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

# Client Download URLs (Optional)
# Provide direct download links for your game client.
LAN_DOWNLOAD_URL="http://lan-fileserver/wow_client.zip" # Example: Accessible only on your LAN
PUBLIC_DOWNLOAD_URL="https://public-mirror.example.com/wow_client.zip" # Example: Accessible from the internet
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

## Admin Functionality (GM Level Based)

The application uses the standard AzerothCore `gmlevel` for determining administrator privileges for the web panel.

*   **Admin Role:** Access to admin functionalities in this web application is granted to users who have an `account.gmlevel` of 3 or higher. This aligns with common AzerothCore permission setups where GM level 3 corresponds to "Administrator".
*   **Initial Admin Setup:** The web application does not provide an interface to change GM levels. To set up your initial admin user for the web panel:
    1.  Register a new user through the standard registration page of this web application.
    2.  Modify this user's `gmlevel` in the `account` table directly in your MySQL database. For example, to make the user with ID `1` an admin:
        ```sql
        UPDATE account SET gmlevel = 3 WHERE id = 1;
        ```
    3.  Alternatively, if you have console access to your running AzerothCore server, you can use in-game commands:
        ```
        .account set gmlevel <account_username> 3
        ```
        Replace `<account_username>` with the username of the account.
*   **Admin Panel Features (Frontend):**
    *   Accessible via an "Admin Panel" link in the navbar for logged-in users with `gmlevel >= 3`.
    *   **User Listing:** View all registered users with details including ID, username, email, GM Level, locked status, and email verification status.
    *   **Ban/Unban Users:** Lock or unlock user accounts. Admins cannot ban themselves or other users with `gmlevel >= 3`.
*   **Admin API Endpoints:** Located under `/api/admin/`, these endpoints are protected and require the authenticated user to have a `gmlevel` of 3 or higher.

## Client Download Page Feature

*   A dedicated page (`/downloads`) for authenticated users to find links to download the World of Warcraft client.
*   The page displays download links based on the `LAN_DOWNLOAD_URL` and `PUBLIC_DOWNLOAD_URL` environment variables configured in the backend.
*   **LAN Detection (Placeholder):** The backend includes a basic mechanism to detect if the user's request is coming from a common private IP range (e.g., 192.168.x.x, 10.x.x.x). If detected and a `LAN_DOWNLOAD_URL` is set, this URL is presented as a prioritized option for potentially faster downloads. Otherwise, or in addition, the `PUBLIC_DOWNLOAD_URL` is shown.
*   If no download URLs are configured, a message indicating this will be displayed.

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
*   `/api/admin/users` (and sub-routes for ban/unban)
*   `/api/downloads/client-info`

## Contributing

Contributions are welcome! Please follow standard fork-and-pull-request workflow. Ensure code is formatted, tested (if applicable), and adheres to the project's goals.
(Further contribution guidelines can be added here).
