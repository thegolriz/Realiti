import http from 'k6/http';
import { check, sleep } from 'k6';
const BASE = __ENV.BASE_URL || 'http://localhost:5001';
export const options = {
  stages: [
    { duration: '30s', target: 5 }, // ramp up to 5 VUs
    { duration: '30s', target: 10 }, // ramp up to 10 VUs
    { duration: '45s', target: 10 }, // hold at peak
    { duration: '15s', target: 0 }, // ramp down
  ],
  thresholds: {
    http_req_failed: ['rate<0.01'], // http errors should be less than 1%
    // Login hashes with argon2 so expectation is a slower run
    'http_req_duration{name:login}': ['p(95)<800'],
  },
};

// Every request in this script sends a JSON body
const params = { headers: { 'Content-Type': 'application/json' } };

export function setup() {
  const email = `k6-${Date.now()}@realiti.dev`;
  const password = `k6-${Date.now()}`;
  const fName = 'k6Test';
  const lName = 'k6Test';
  const signupRes = http.post(
    `${BASE}/api/signup`,
    JSON.stringify({ email: email, password: password, first_name: fName, last_name: lName }),
    { ...params, tags: { name: 'signup' } },
  );
  check(signupRes, {
    'signup status 201': (r) => r.status === 201,
  });
  if (signupRes.status !== 201) {
    throw new Error(`signup failed: ${signupRes.status} ${signupRes.body}`);
  }
  // This object becomes `data` in the default function and in teardown()
  return { email, password };
}

export default function(data) {
  // Log in as the test user that setup() created
  const loginRes = http.post(
    `${BASE}/api/login`,
    JSON.stringify({ email: data.email, password: data.password }),
    { ...params, tags: { name: 'login' } },
  );
  check(loginRes, {
    'login status 200': (r) => r.status === 200,
    'has access_token': (r) => r.status === 200 && !!r.json('access_token'),
  });

  sleep(1);
}

// Runs once after all VUs finish: remove the k6 test user from the DB
export function teardown(data) {
  // Fresh login: VU tokens don't come back here, and an old one could expire
  const loginRes = http.post(
    `${BASE}/api/login`,
    JSON.stringify({ email: data.email, password: data.password }),
    // Own name so this login isn't counted in the 'login' threshold
    { ...params, tags: { name: 'teardown-login' } },
  );
  if (loginRes.status !== 200) {
    throw new Error(
      `teardown login failed: ${loginRes.status} ${loginRes.body} (delete ${data.email} by hand)`,
    );
  }
  const token = loginRes.json('access_token');

  // Delete the account: password in the body, access token in the Authorization header
  const deleteRes = http.del(
    `${BASE}/api/account`,
    JSON.stringify({ password: data.password }),
    {
      // Build a new headers object: keep Content-Type, add the token
      headers: { ...params.headers, Authorization: `Bearer ${token}` },
      tags: { name: 'delete-account' },
    },
  );
  if (deleteRes.status !== 200) {
    throw new Error(
      `teardown delete failed: ${deleteRes.status} ${deleteRes.body} (delete ${data.email} by hand)`,
    );
  }
}
