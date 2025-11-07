#!/bin/bash
set -e
set -u

check_docker() {
    if ! docker info > /dev/null 2>&1; then
        echo "[ERROR] Docker is not running. Please start Docker first."
        exit 1
    fi
}

update_caddyfile() {
    if [ -f "settings.env" ]; then
        source settings.env
        if [ -z "${DOMAIN_NAME:-}" ]; then
            echo "[ERROR] The DOMAIN_NAME isn't set in the settings.env file. Please follow the instructions in the README.md to set the DOMAIN_NAME."
            exit 1
        fi
    else
        echo "[ERROR] The settings.env file was not found. Please follow the instructions in the README.md to create the settings.env file."
        exit 1
    fi
    sed "s/development-assistant\.yourdomain\.com/${DOMAIN_NAME}/g" Caddyfile.template > Caddyfile
    echo "[OK] Updated Caddyfile with domain: ${DOMAIN_NAME}"
}

start_containers() {
    if [ -f "secrets.env" ]; then
        # shellcheck disable=SC1091
        source secrets.env
    fi
    docker builder prune -f
    docker-compose build --no-cache
    if [ -z "$LLM_API_KEY" ]; then
        echo "[INFO] LLM_API_KEY not set — starting with the self-hosted LLM service..."
        docker compose --profile no-llm-api-key up --build -d
    else
        echo "[INFO] LLM_API_KEY detected — starting without the self-hosted LLM service..."
        docker compose up --build -d
    fi
}

main() {
    check_docker
    update_caddyfile
    start_containers
    echo "[DONE] Containers are up and running."
}

main