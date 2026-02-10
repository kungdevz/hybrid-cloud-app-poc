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
scp -i load-test/key/rosa-bastion-key.pem -o StrictHostKeyChecking=no \
    load-test/docker-compose.yml \
    load-test/load_test.js \
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
    "export PATH=\$PATH:~/.local/bin && podman-compose run k6"
```

## 4. View Results

Access Grafana at:
<http://ec2-43-210-23-187.ap-southeast-7.compute.amazonaws.com:3000>

- **User**: `admin`
- **Password**: `password`

## 5. View Logs

```bash
ssh -i load-test/key/rosa-bastion-key.pem ec2-user@ec2-43-210-23-187.ap-southeast-7.compute.amazonaws.com \
    "export PATH=\$PATH:~/.local/bin && podman-compose logs -f"
```
