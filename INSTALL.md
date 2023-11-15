# Application Installation Guide

This guide will walk you through the process of setting up your application using Docker Compose.

## Prerequisites

Ensure that you have Docker and Docker Compose installed on your system. If you haven't installed them yet, you can follow the official Docker installation guide [here](https://docs.docker.com/compose/install/).

## Environment Configuration

1. Copy the `app/.env.template` file to create a new `.env` file.
2. Fill in the necessary information in the `.env` file.

## Application Setup

1. Navigate to the `corspat` directory in your terminal.
2. Run the following command to start the application: `docker compose -f "corspat\docker-compose.dev.yml" up -d --build`

Alternatively, you can use the "Right Button > Compose Up" option in your IDE if it supports Docker Compose.

## Database Setup

1. Create tables using the `app/sql/create_tables.sql` script.
