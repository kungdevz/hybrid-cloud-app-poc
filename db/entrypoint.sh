#!/bin/bash

# Start SQL Server in the background
/opt/mssql/bin/sqlservr &

# Wait for SQL Server to be ready
echo "Waiting for SQL Server to start..."
sleep 30

# Run the initialization script using the available sqlcmd
echo "Running initialization script..."
for i in {1..10}; do
    /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P 'c2E6U2VjcmV0I1Bhc3MxMjM=' -C -i /usr/config/init.sql 2>/dev/null && break
    echo "Attempt $i failed, retrying in 5 seconds..."
    sleep 5
done

echo "Database initialization complete."

# Keep the container running
wait
