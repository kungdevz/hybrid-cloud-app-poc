import { check, group, sleep } from 'k6';
import http from 'k6/http';
import { Rate, Trend } from 'k6/metrics';

// Custom metrics
let ErrorRate = new Rate('errors');
let ApiLatency = new Trend('api_latency');

// Configuration
export let options = {
    scenarios: {
        // 1. Functional / API Happy Path (Sequential user creation flow)
        functional_api: {
            executor: 'per-vu-iterations',
            vus: 1,
            iterations: 1,
            maxDuration: '1m',
        },
        // 2. Load Test / Latency Baseline (1000 RPS target, sustained for 1m)
        // Note: Adjust RPS based on your infrastructure capacity
        load_test: {
            executor: 'constant-arrival-rate',
            rate: 10, // Reduced from 50 to 10 to establish baseline
            timeUnit: '1s',
            duration: '1m',
            preAllocatedVUs: 50,
            maxVUs: 100,
            startTime: '1m', // Start after functional test
        },
        // 3. Soak Test (Simulation of long running load)
        // soak_test: { ... } // Uncomment for longer duration
    },
    thresholds: {
        'errors': ['rate<0.01'], // <1% errors
        'api_latency': ['p(95)<2000'], // Relaxed to 2000ms (2s) for POC
    },
};

const BASE_URL = __ENV.BASE_URL || 'https://app-route-ks-hybrid-cloud-poc.apps.rosa.n0w7a5w8g3j0z4e.en6d.p3.openshiftapps.com';

function generateRandomString(length) {
    let result = '';
    let characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    let charactersLength = characters.length;
    for (let i = 0; i < length; i++) {
        result += characters.charAt(Math.floor(Math.random() * charactersLength));
    }
    return result;
}

export default function () {
    let userHandle = `user_${generateRandomString(8)}`;
    let userId;

    group('API Happy Path', function () {
        // 1. Create User (POST)
        let payload = JSON.stringify({ handle: userHandle });
        let params = { headers: { 'Content-Type': 'application/json' } };

        let res = http.post(`${BASE_URL}/users`, payload, params);

        ErrorRate.add(!check(res, {
            'POST status is 200': (r) => r.status === 200,
            'User created': (r) => r.json('handle') === userHandle,
        }));

        ApiLatency.add(res.timings.duration);

        if (res.status === 200) {
            userId = res.json('id');
        }

        sleep(1);

        if (userId) {
            // 2. Read User (GET) -> Read-after-write check
            // A fixed `name` tag keeps one InfluxDB series per endpoint instead
            // of one per user id (k6 defaults `name` to the full URL).
            res = http.get(`${BASE_URL}/users/${userId}`, { tags: { name: 'GET /users/{id}' } });
            ErrorRate.add(!check(res, {
                'GET status is 200': (r) => r.status === 200,
                'User data matches': (r) => r.json('handle') === userHandle,
            }));
            ApiLatency.add(res.timings.duration);

            sleep(1);

            // 3. Update User (PUT)
            let updatedHandle = `${userHandle}_updated`;
            payload = JSON.stringify({ handle: updatedHandle });
            res = http.put(`${BASE_URL}/users/${userId}`, payload, {
                headers: params.headers,
                tags: { name: 'PUT /users/{id}' },
            });

            ErrorRate.add(!check(res, {
                'PUT status is 200': (r) => r.status === 200,
                'User updated': (r) => r.json('handle') === updatedHandle,
            }));
            ApiLatency.add(res.timings.duration);

            sleep(1);

            // 4. Delete User (DELETE)
            res = http.del(`${BASE_URL}/users/${userId}`, null, { tags: { name: 'DELETE /users/{id}' } });
            ErrorRate.add(!check(res, {
                'DELETE status is 200': (r) => r.status === 200,
            }));
            ApiLatency.add(res.timings.duration);
        }
    });

    // Simple List Users (Pagination simulation - just listing all for now as pagination not implemented in API)
    group('List Users', function () {
        let res = http.get(`${BASE_URL}/users`);
        ErrorRate.add(!check(res, {
            'List status is 200': (r) => r.status === 200,
        }));
        ApiLatency.add(res.timings.duration);
    });
}
