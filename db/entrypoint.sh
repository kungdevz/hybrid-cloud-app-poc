#!/bin/bash

# Start SQL Server in the background
/opt/mssql/bin/sqlservr &

# Wait for SQL Server to be ready
echo "Waiting for SQL Server to start..."
sleep 30

# Run the initialization script
echo "Running initialization script..."
/opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P 'c2E6U2VjcmV0I1Bhc3MxMjM=' -C -i /usr/config/init.sql

echo "Database initialization complete."

# Keep the container running
wait
