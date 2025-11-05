#!/bin/bash
set -e
set -u

check_docker() {
    if ! docker info > /dev/null 2>&1; then
        echo "Docker is not running. Please start Docker first."
        exit 1
    fi
}

update_caddyfile() {
    if [ -f "settings.env" ]; then
        source settings.env
        if [ -z "${DOMAIN_NAME:-}" ]; then
            echo "The DOMAIN_NAME isn't set in the settings.env file. Please follow the instructions in the README.md to set the DOMAIN_NAME."
            exit 1
        fi
    else
        echo "The settings.env file was not found. Please follow the instructions in the README.md to create the settings.env file."
        exit 1
    fi
    sed "s/development-assistant\.yourdomain\.com/${DOMAIN_NAME}/g" Caddyfile.template > Caddyfile
}

start_containers() {
    docker builder prune -f
    docker-compose build --no-cache
    docker-compose up -d
}

main() {
    check_docker
    update_caddyfile
    start_containers
}

main