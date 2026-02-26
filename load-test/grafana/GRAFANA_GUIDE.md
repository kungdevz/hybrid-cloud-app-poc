# Grafana Dashboard Guide

## Accessing the Dashboard

**URL**: <http://ec2-43-210-23-187.ap-southeast-7.compute.amazonaws.com:3000>

**Credentials**:

- Username: `admin`
- Password: See `GF_SECURITY_ADMIN_PASSWORD` in `load-test/docker-compose.yml`

## Dashboard: k6 Load Testing Results

### Available Metrics

The dashboard displays the following metrics from k6 load tests:

#### Top Row (Time Series)

1. **Virtual Users** - Number of active virtual users over time
2. **Requests per Second** - HTTP request rate
3. **Errors Per Second** - Failed requests over time
4. **Checks Per Second** - Assertion/validation checks

#### Summary Stats

- **http_req_duration** - Request latency (mean, max, min, p95, p99)
- **http_req_blocked** - Time spent blocked before request
- **http_req_connecting** - Connection establishment time
- **iterations** - Test iterations completed

### Troubleshooting Missing Data

If you see "No Data" on panels:

#### 1. Check Time Range

- Click the **time picker** (top right)
- Select "Last 5 minutes" or "Last 15 minutes"
- Or use "Absolute time range" and select the time when you ran the test

#### 2. Verify Data in InfluxDB

SSH to EC2 and run:

```bash
podman exec k6-influxdb influx -database k6 -execute 'SHOW MEASUREMENTS'
podman exec k6-influxdb influx -database k6 -execute 'SELECT * FROM vus LIMIT 10'
```

#### 3. Refresh Dashboard

- Click the **refresh icon** (top right)
- Or set auto-refresh to "5s"

#### 4. Check Datasource

- Go to **Configuration** → **Data Sources**
- Verify "InfluxDB" is configured:
  - URL: `http://influxdb:8086` (or `http://k6-influxdb:8086`)
  - Database: `k6`
  - Click "Save & Test"

### Common Issues

| Issue | Solution |
|-------|----------|
| "No Data" on all panels | Check time range, verify test ran successfully |
| Some panels empty | Specific metrics might not be generated (e.g., no errors = no data in "Errors Per Second") |
| Dashboard not loading | Verify Grafana container is running: `podman ps` |
| Can't connect to Grafana | Check port 3000 is exposed and firewall allows access |

### Metrics Reference

| Measurement | Description |
|-------------|-------------|
| `vus` | Virtual users (concurrent connections) |
| `vus_max` | Maximum VUs allocated |
| `http_reqs` | Total HTTP requests |
| `http_req_duration` | Request duration (latency) |
| `http_req_failed` | Failed requests (boolean) |
| `checks` | k6 check assertions |
| `iterations` | Test iterations completed |
| `data_sent` | Bytes sent |
| `data_received` | Bytes received |

### Best Practices

1. **Run test before viewing**: Ensure k6 test has completed before checking dashboard
2. **Adjust time range**: Match the time range to when your test ran
3. **Use auto-refresh**: Set to "5s" or "10s" during active testing
4. **Save custom views**: Create your own dashboard variations for specific metrics
5. **Export data**: Use Grafana's export feature to save results as CSV/JSON

## Advanced: Custom Queries

To create custom panels, use InfluxQL queries like:

```sql
SELECT mean("value") FROM "http_req_duration" WHERE $timeFilter GROUP BY time($__interval)
SELECT sum("value") FROM "http_reqs" WHERE $timeFilter GROUP BY time(1s)
SELECT last("value") FROM "vus" WHERE $timeFilter
```

## Need Help?

- Check k6 documentation: <https://k6.io/docs/results-output/real-time/influxdb/>
- Grafana InfluxDB guide: <https://grafana.com/docs/grafana/latest/datasources/influxdb/>
