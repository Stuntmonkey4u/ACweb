#!/bin/bash
set -e # Exit immediately if a command exits with a non-zero status.

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# --- Dependency Checks ---
echo "Checking dependencies..."

if command_exists git; then
    echo "Git: OK"
else
    echo "Error: Git is not installed. Please install Git and try again."
    exit 1
fi

if command_exists docker; then
    echo "Docker: OK"
else
    echo "Error: Docker is not installed. Please install Docker and try again."
    exit 1
fi

if command_exists docker-compose || command_exists docker compose; then
    # Check for docker compose v1 (docker-compose) or v2 (docker compose)
    echo "Docker Compose: OK"
else
    echo "Error: Docker Compose is not installed. Please install Docker Compose (v1 or v2) and try again."
    exit 1
fi
echo "All dependencies found."
echo ""

# --- .env File Setup ---
echo "Setting up configuration file..."
if [ -f .env ]; then
    echo ".env file already exists. Skipping creation."
    echo "Please ensure your .env file is correctly configured before proceeding."
else
    if [ -f .env.example ]; then
        cp .env.example .env
        echo ".env.example copied to .env"
    else
        echo "Error: .env.example not found! Cannot create .env file."
        echo "Please ensure .env.example is present in the project root."
        exit 1
    fi
fi
echo ""
echo "IMPORTANT: Please review and edit the .env file in the project root."
echo "You'll need to set your database credentials, SECRET_KEY, SMTP details (optional),"
echo "Redis settings (optional), and any other specific configurations for your setup."
echo ""
read -p "Press Enter to continue after you have edited the .env file..."
echo ""


# --- Docker Compose Build ---
echo "Building Docker images... This may take a few minutes."
if command_exists docker-compose; then
    docker-compose build
elif command_exists docker compose; then
    docker compose build
else
    echo "Error: Could not determine Docker Compose command." # Should have been caught by dependency check
    exit 1
fi
echo "Docker images built successfully."
echo ""

# --- Guidance for First Run and Admin Setup ---
echo "--- Setup Complete ---"
echo ""
echo "Next Steps:"
echo "1. Start the application using Docker Compose:"
echo "   If using Docker Compose v1: docker-compose up -d"
echo "   If using Docker Compose v2: docker compose up -d"
echo ""
echo "   On the first startup, the backend application will initialize the databases."
echo "   Wait a minute or two for the services to fully start."
echo ""
echo "2. Register your main administrator account through the web UI."
echo "   (Navigate to http://localhost:YOUR_FRONTEND_PORT or your configured domain)"
echo ""
echo "3. Manually set your admin user's GM level in the database."
echo "   You will need to connect to your MySQL database (e.g., using a tool like DBeaver, phpMyAdmin, or MySQL CLI)."
echo "   The default database name is 'ac_auth' (unless you changed it in .env)."
echo "   Run the following SQL command (replace 'YOUR_ADMIN_USERNAME_HERE' with the username you registered):"
echo "   ------------------------------------------------------------------"
echo "   USE ac_auth;"
echo "   UPDATE account SET gmlevel = 3 WHERE username = 'YOUR_ADMIN_USERNAME_HERE';"
echo "   ------------------------------------------------------------------"
echo "   Alternatively, if you have access to the game server console or can use in-game GM commands:"
echo "   .account set gmlevel YOUR_ADMIN_USERNAME_HERE 3"
echo ""
echo "4. Access the web application and log in with your admin account."
echo "   You should now have access to the Admin Panel."
echo ""

# --- Usage Instructions ---
echo "--- Application Management ---"
echo "To start the application (detached mode):"
echo "  docker-compose up -d  (or 'docker compose up -d' for v2)"
echo ""
echo "To stop the application:"
echo "  docker-compose down   (or 'docker compose down' for v2)"
echo ""
echo "To view logs for a specific service (e.g., backend):"
echo "  docker-compose logs -f backend (or 'docker compose logs -f backend' for v2)"
echo ""
echo "To rebuild images after code changes:"
echo "  docker-compose build  (or 'docker compose build' for v2)"
echo ""
echo "Installation script finished."
