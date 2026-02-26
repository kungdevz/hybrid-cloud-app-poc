---
description: Run load test on EC2 Bastion
---

# Run Load Test on EC2 Bastion

## Prerequisites

- SSH Key: `load-test/key/rosa-bastion-key.pem`
- EC2 Host: `ec2-43-210-23-187.ap-southeast-7.compute.amazonaws.com`

## 1. Deploy Load Test Config

Refreshes the docker-compose configuration on the bastion.

// turbo

```bash
scp -i load-test/key/rosa-bastion-key.pem -o StrictHostKeyChecking=no -r \
    load-test/docker-compose.yml \
    load-test/load_test.js \
    load-test/grafana \
    ec2-user@ec2-43-210-23-187.ap-southeast-7.compute.amazonaws.com:~/ \
    && echo "Files uploaded successfully"
```

## 2. Start Services (Remote)

Starts InfluxDB, Grafana, and K6 on the EC2 instance.

// turbo

```bash
ssh -i load-test/key/rosa-bastion-key.pem ec2-user@ec2-43-210-23-187.ap-southeast-7.compute.amazonaws.com \
    "export PATH=\$PATH:~/.local/bin && podman-compose down && podman-compose up -d"
```

## 3. Run Load Test (Remote)

Executes the K6 load test inside the container network.

// turbo

```bash
ssh -i load-test/key/rosa-bastion-key.pem ec2-user@ec2-43-210-23-187.ap-southeast-7.compute.amazonaws.com \
    "export PATH=\$PATH:~/.local/bin && \
     podman run --rm --network host \
     -e BASE_URL='http://app-route-ks-hybrid-cloud-poc.apps.rosa.r0r7f1m1d7w4r0m.en6d.p3.openshiftapps.com' \
     -v ~/load_test.js:/script.js:ro,z \
     grafana/k6 run --out influxdb=http://127.0.0.1:8086/k6 /script.js"
```

## 4. View Results

Access Grafana at:
<http://ec2-43-210-23-187.ap-southeast-7.compute.amazonaws.com:3000>

- **User**: `admin`
- **Password**: read from GF_SECURITY_ADMIN_PASSWORD in docker-compose.yml

### Important: Set Time Range

If you see "No Data" on dashboard panels:

1. Click the **time picker** (top right corner)
2. Select **"Last 15 minutes"** or **"Last 1 hour"**
3. Or use **"Absolute time range"** and select when you ran the test
4. Click **Refresh** icon

The dashboard shows: Virtual Users, Requests/sec, Errors/sec, Checks/sec, and http_req_duration over time.

See `load-test/grafana/GRAFANA_GUIDE.md` for detailed troubleshooting.

## 5. View Logs

```bash
ssh -i load-test/key/rosa-bastion-key.pem ec2-user@ec2-43-210-23-187.ap-southeast-7.compute.amazonaws.com \
    "export PATH=\$PATH:~/.local/bin && podman-compose logs -f"
```
