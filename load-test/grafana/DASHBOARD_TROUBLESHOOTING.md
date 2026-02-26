# Dashboard Configuration Issue - Resolution

## Problem

Virtual Users panel shows "No Data" even though data exists in InfluxDB.

## Root Cause

**Time Range Mismatch**: Grafana's default time range doesn't include when the test ran.

## Data Location Confirmed

- **Database**: `k6` in InfluxDB
- **Measurement**: `vus`
- **Data exists at**: `2026-02-10 12:07:40 UTC` (19:07:40 +07:00 local time)
- **Data points**: 122 records
- **Query works**: `SELECT mean("value") FROM "vus"` returns data when time range is correct

## Solution

### Option 1: Manual Time Range (Recommended)

1. Open Grafana: <http://ec2-43-210-23-187.ap-southeast-7.compute.amazonaws.com:3000>
2. Login: `admin` / `Sup@erSecretP@ssw03d`
3. Open "k6 Load Testing Results" dashboard
4. Click **time picker** (top right - looks like a clock icon)
5. Select **"Absolute time range"**
6. Enter:
   - **From**: `2026-02-10 12:05:00`
   - **To**: `2026-02-10 12:15:00`
   - **Timezone**: UTC
7. Click **"Apply time range"**
8. Click **Refresh** button (circular arrow)

### Option 2: Relative Time Range

If you just ran a test within the last hour:

1. Click time picker
2. Select **"Last 1 hour"** or **"Last 30 minutes"**
3. Click Refresh

### Option 3: Auto-refresh During Test

For real-time monitoring while test is running:

1. Set time range to **"Last 5 minutes"**
2. Enable auto-refresh: Click refresh dropdown → Select **"5s"** or **"10s"**
3. Run your load test
4. Watch metrics appear in real-time

## Verification

After setting the correct time range, you should see:

| Panel | Expected Data |
|-------|---------------|
| Virtual Users | Line graph showing VUs: 1 → 30 → 10 → 0 |
| Requests per Second | ~24 req/s |
| Errors Per Second | 0 (empty/flat line is correct!) |
| Checks Per Second | Multiple colored lines for different checks |
| http_req_duration | Latency metrics over time |

## Technical Details

### InfluxDB Query (works correctly)

```sql
SELECT mean("value") FROM "vus" 
WHERE time > '2026-02-10T12:05:00Z' AND time < '2026-02-10T12:15:00Z' 
GROUP BY time(1s)
```

### Dashboard Configuration (verified correct)

- **Datasource**: InfluxDB (<http://influxdb:8086>)
- **Database**: k6
- **Measurement**: vus
- **Field**: value
- **Aggregation**: mean()
- **Group by**: time($__interval)

## Why This Happens

1. **Grafana defaults** to "Last 6 hours" or "Last 24 hours"
2. **Load tests are short** (2-3 minutes)
3. **Time zones** can cause confusion (UTC vs local time)
4. **Auto-refresh disabled** by default

## Best Practice for Future Tests

**Before running a test:**

1. Open Grafana dashboard
2. Set time range to "Last 5 minutes"
3. Enable auto-refresh (5s or 10s)
4. Run your load test
5. Watch metrics populate in real-time

**After test completes:**

1. Disable auto-refresh
2. Adjust time range to cover the exact test duration
3. Take screenshots or export data if needed

## Still Not Working?

If you've set the correct time range and still see no data:

1. **Verify data exists**:

   ```bash
   ssh -i load-test/key/rosa-bastion-key.pem ec2-user@ec2-43-210-23-187.ap-southeast-7.compute.amazonaws.com \
     "podman exec k6-influxdb influx -database k6 -execute 'SELECT COUNT(*) FROM vus'"
   ```

2. **Check Grafana datasource**:
   - Go to Configuration → Data Sources
   - Click "InfluxDB"
   - Click "Save & Test"
   - Should show "Data source is working"

3. **Check browser console**:
   - Open browser DevTools (F12)
   - Look for errors in Console tab
   - Check Network tab for failed requests

4. **Restart Grafana**:

   ```bash
   ssh -i load-test/key/rosa-bastion-key.pem ec2-user@ec2-43-210-23-187.ap-southeast-7.compute.amazonaws.com \
     "podman restart k6-grafana"
   ```
