import http from "k6/http";
import { check, sleep } from "k6";

export const options = {
  vus: 20,
  duration: "30s",
  thresholds: {
    http_req_failed: ["rate<0.05"],
    http_req_duration: ["p(95)<500"],
  },
};

export default function () {
  const response = http.get("http://traefik/api/items", {
    headers: {
      Host: __ENV.APP_DOMAIN || "localhost",
      "X-API-KEY": __ENV.API_KEY || "demo-key",
    },
  });
  check(response, { "API responds": (result) => result.status === 200 });
  sleep(1);
}import http from "k6/http";
import { check, sleep } from "k6";

export const options = {
  vus: 20,
  duration: "30s",
  thresholds: {
    http_req_failed: ["rate<0.05"],
    http_req_duration: ["p(95)<500"],
  },
};

export default function () {
  const response = http.get("http://traefik/api/items", {
    headers: {
      Host: __ENV.APP_DOMAIN || "localhost",
      "X-API-KEY": __ENV.API_KEY || "demo-key",
    },
  });
  check(response, { "API responds": (result) => result.status === 200 });
  sleep(1);
}
