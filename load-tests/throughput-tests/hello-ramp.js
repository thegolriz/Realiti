import http from 'k6/http';
import { check, sleep } from 'k6';
const BASE = __ENV.BASE_URL || 'http://localhost:5001';
export const options = {
  stages: [
    { duration: '1m', target: 10 }, // ramp up to 10 VUs
    { duration: '1m', target: 10 }, // hold at 10 (baseline)
    { duration: '1m30s', target: 25 }, // ramp up to 25 VUs
    { duration: '1m', target: 25 }, // hold at peak
    { duration: '30s', target: 0 }, // ramp down
  ],
  thresholds: {
    http_req_failed: ['rate<0.01'], // http errors should be less than 1%
    http_req_duration: ['p(95)<200'], // 95% of requests should be below 200ms
  },
};


export default function() {
  // Make a GET request to the target URL
  const res = http.get(`${BASE}/api/hello`);
  check(res, {
    'is status 200': (r) => r.status === 200,
  });


  // Sleep for 1 second to simulate real-world usage
  sleep(1);
}
