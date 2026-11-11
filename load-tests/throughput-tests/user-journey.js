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
    // Plain DB writes, no argon2 or AI calls, so these should sit near the feed
    'http_req_duration{name:like}': ['p(95)<500'],
    'http_req_duration{name:reply}': ['p(95)<500'],
  },
};

// Every request in this script sends a JSON body
const params = { headers: { 'Content-Type': 'application/json' } };

// JSON header plus the access token, for routes behind @jwt_required()
function authParams(token, name) {
  return {
    headers: { ...params.headers, Authorization: `Bearer ${token}` },
    tags: { name },
  };
}

function login(email, password, name) {
  const res = http.post(
    `${BASE}/api/login`,
    JSON.stringify({ email, password }),
    { ...params, tags: { name } },
  );
  if (res.status !== 200) {
    throw new Error(`${name} failed: ${res.status} ${res.body} (check ${email} by hand)`);
  }
  return res.json('access_token');
}

function deleteAccount(token, password, email) {
  const res = http.del(
    `${BASE}/api/account`,
    JSON.stringify({ password }),
    authParams(token, 'delete-account'),
  );
  if (res.status !== 200) {
    throw new Error(`delete failed: ${res.status} ${res.body} (delete ${email} by hand)`);
  }
}

export function setup() {
  // Likes/replies go on an existing post you own: -e POST_ID=<id>.
  // No new post means no Claude call and no fake content on the site.
  // Deleting the k6 user in teardown removes its likes and replies everywhere.
  const postId = Number(__ENV.POST_ID);
  if (!postId) {
    throw new Error('set -e POST_ID=<id of a post you own> before running');
  }

  const email = `k6-${Date.now()}@realiti.dev`;
  const password = `k6-${Date.now()}`;
  const signupRes = http.post(
    `${BASE}/api/signup`,
    JSON.stringify({ email, password, first_name: 'k6Test', last_name: 'k6Test' }),
    { ...params, tags: { name: 'signup' } },
  );
  if (signupRes.status !== 201) {
    throw new Error(`signup failed: ${signupRes.status} ${signupRes.body}`);
  }

  // One login for the whole run: the run is ~2 min, tokens last 15 min.
  // Logging in every iteration would make this an argon2 test again.
  const token = login(email, password, 'setup-login');

  return { email, password, token, postId };
}

export default function (data) {
  // Like toggles, so this flips on and off each iteration instead of piling up rows
  const likeRes = http.post(
    `${BASE}/api/like`,
    JSON.stringify({ postId: data.postId }),
    authParams(data.token, 'like'),
  );
  check(likeRes, {
    'like status 200': (r) => r.status === 200,
  });

  sleep(1);

  const replyRes = http.post(
    `${BASE}/api/reply`,
    JSON.stringify({ postId: data.postId, reply_text: 'k6 load test reply' }),
    authParams(data.token, 'reply'),
  );
  check(replyRes, {
    'reply status 200': (r) => r.status === 200,
  });

  sleep(1);
}

// Runs once after all VUs finish: deleting the user also deletes its likes
// and replies on the target post (auth_routes.py delete cascade)
export function teardown(data) {
  // Fresh login in case the setup token is close to expiring
  const token = login(data.email, data.password, 'teardown-login');
  deleteAccount(token, data.password, data.email);
}
