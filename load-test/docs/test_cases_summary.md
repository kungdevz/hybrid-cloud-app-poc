# Hybrid Cloud POC Test Cases

Extracted from `docs/hybrid_cloud_test_cases.xlsx`

## 1. Cloud Test Cases (Scope: App Cluster / On-Cloud)

| ID | Type | Test Name | Steps | Expected Result | Acceptance Criteria |
|----|------|-----------|-------|-----------------|---------------------|
| 1 | Functional & API | API Happy Path | Call GET/POST/PUT/DELETE endpoints directly to DB | Response correct, status 200 | p95 ≤ 250ms, 0% error |
| 2 | Functional & API | Idempotency/Retry | Retry same request (Call GET/POST/PUT/DELETE) | No duplicate actions or inconsistent states | No duplicate records |
| 3 | Functional & API | Pagination/Filter | Query with pagination & filter on large dataset | Results correct and ordered | Correctness verified |
| 4 | Functional & API | Read-after-write | Write then immediately read | Latest data returned | No stale read |
| 5 | Functional & API | DB Read timeout | Inject query delay | Timeout handled, no cascade failure | Error < 2% |
| 6 | Network & TLS | Latency baseline | Load test 1k RPS | p95 ≤ 250ms | Latency OK |
| 7 | Network & TLS | Soak Test | Run 6h continuous load | No memory leak/conn leak | Stable |
| 8 | Network & TLS | TLS E2E | Verify TLS | TLS enforced | Pass |
| 9 | ALB | ALB Health Check | Stop service pods | LB removes unhealthy nodes | Detection ≤ 10s |
| 10 | ASG | AutoScaling (Scale Out) | Define new desired node | HPA/ASG scales | Scale-out OK and No Impact App |
| 11 | ASG | AutoScaling (Stress) | Stress traffic 10x | HPA/ASG scales | Scale-out OK |
| 12 | ASG | AZ Failure | Kill all nodes in 1 AZ | Service still 99.9% available | Pass |
| 13 | Monitor | Alarm Test | Simulate error spike | Alarm triggered | Pass |

## 2. Network Test Cases (Scope: LTM/GTM)

| ID | Type | Test Name | Steps | Expected Result |
|----|------|-----------|-------|-----------------|
| 1 | Load Balancer | Connection Limit LB | Create connection limit on F5 LTM (Onprem); Monitor URL Monitor on F5 GTM | Traffic load able transfer to cloud services after connection hit limit on prem |

## 3. Database Test Cases

*(No test cases defined in source file)*

---

# POC Test Suggestions

Based on the application current state (Python Flask + MSSQL on OpenShift), here is the recommended test scope for the POC:

### ✅ 1. Functional Verification (Priority: High)

*Covered by existing `verify_backend.py` and manual testing.*

- **API Happy Path**: Verify users can be created, read, updated, and deleted.
- **Read-after-write**: Confirm that updates are immediately visible (solved `id` update issue).

### 🚀 2. Scalability & Resilience (Priority: Medium)

*Requires configuring HPA and Load Testing tools (e.g., k6, locust).*

- **AutoScaling**:
  - Configure `HorizontalPodAutoscaler` for `python-app`.
  - Generate traffic to trigger scale-out.
  - Verify new pods handle traffic without errors.
- **ALB Health Check**:
  - Simulate app failure (e.g. `/health` returning 500 or killing pod).
  - Verify OpenShift Route/Service removes the endpoint.

### 🔒 3. Network & Security (Priority: Medium)

- **TLS E2E**: Verify Access via HTTPS (OpenShift Routes provide this by default).
- **connection Limit**: If On-Prem environment is available, test traffic spillover (Hybrid Cloud scenario).

### 📊 4. Monitoring (Priority: Low/Future)

- **Alarm Test**: Integration with Prometheus/Grafana (if available in the cluster) to trigger alerts on high 500 error rate.
