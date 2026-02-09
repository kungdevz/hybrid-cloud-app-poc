# Hybrid Cloud App POC - Load Testing on AWS EC2

This guide describes how to run the k6 load test on an Amazon Linux 2023 (or similar) EC2 instance using Podman Compose.

## Prerequisites

- An EC2 instance (Amazon Linux 2023 recommended) with internet access.
- SSH access to the instance.

## Installation Steps

1. **Connect to your EC2 instance:**

   ```bash
   ssh -i <key.pem> ec2-user@<ec2-public-ip>
   ```

2. **Install Podman:**

   ```bash
   sudo dnf install -y podman
   ```

3. **Install Podman Compose:**
   Podman Compose can be installed via pip (Python package manager).

   ```bash
   sudo dnf install -y python3-pip
   pip3 install podman-compose
   ```

   *Note: Ensure `~/.local/bin` is in your PATH.*

4. **Verify Installation:**

   ```bash
   podman version
   podman-compose --version
   ```

## Running the Load Test

1. **Upload the test files:**
   Copy `docker-compose.yml` and `load_test.js` to the EC2 instance.

   ```bash
   # From your local machine
   scp -i <key.pem> load-test/docker-compose.yml load-test/load_test.js ec2-user@<ec2-public-ip>:~/
   ```

2. **Run the test:**

   ```bash
   podman-compose up
   ```

3. **Customizing the Target URL:**
   You can override the `BASE_URL` environment variable if needed:

   ```bash
   BASE_URL=https://your-api-url.com podman-compose up
   ```

## Test Scenarios

The `load_test.js` script includes:

- **Functional API Check**: Validates Create, Read, Update, Delete operations for a single user.
- **Load Test**: Simulates 50 requests per second (RPS) for 1 minute (configurable in the script).

## output

Results will be displayed in the terminal. Look for:

- `http_reqs`: Total requests
- `http_req_duration`: Latency metrics (p95)
- `checks`: Success rate

## Monitoring Dashboard

The setup includes InfluxDB and Grafana for real-time visualization.

1. **Access Grafana:**
   Open `http://<ec2-public-ip>:3000` in your browser.

2. **View Dashboard:**
   - Go to **Dashboards** -> **Manage**.
   - Click on **k6 Load Testing Results**.
   - You should see real-time metrics populated as the test runs.
