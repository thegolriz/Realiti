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
    // Per-endpoint p95, using the name tags on each request. Prod hello p95
    // was ~91ms (mostly network), so these leave room for each endpoint's
    // own DB work: the feed runs several queries per post (N+1).
    'http_req_duration{name:feed}': ['p(95)<500'],
    'http_req_duration{name:replies}': ['p(95)<300'],
    'http_req_duration{name:tags}': ['p(95)<200'],
  },
};


export default function() {
  // Load the public feed, like an anonymous visitor opening the site
  const feedRes = http.get(`${BASE}/api/post`, { tags: { name: 'feed' } });
  check(feedRes, {
    'is status 200': (r) => r.status === 200,
    'is body json array': (r) => r.status === 200 && Array.isArray(r.json()),
  });

  // Only parse on success: a 429/502 body isn't JSON and .json() would throw
  if (feedRes.status === 200) {
    const posts = feedRes.json();
    if (posts.length > 0) {
      const post = posts[Math.floor(Math.random() * posts.length)];

      // "Reading the feed" before opening a post's comments
      sleep(1);

      // Every post id is a different URL; the name tag groups them as one endpoint
      const repliesRes = http.get(`${BASE}/api/replies/${post.id}`, {
        tags: { name: 'replies' },
      });
      check(repliesRes, {
        'replies status 200': (r) => r.status === 200,
        // An empty [] is a valid answer for a post with no replies
        'replies is json array': (r) =>
          r.status === 200 && Array.isArray(r.json()),
      });
    }
  }

  // The filter list the page loads
  const tagsRes = http.get(`${BASE}/api/tags`, { tags: { name: 'tags' } });
  check(tagsRes, {
    'tags status 200': (r) => r.status === 200,
    'tags is json array': (r) => r.status === 200 && Array.isArray(r.json()),
  });


  // Sleep for 1 second to simulate real-world usage
  sleep(1);
}
