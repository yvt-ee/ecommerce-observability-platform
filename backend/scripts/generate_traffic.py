"""
Hits the running API repeatedly so there's something interesting to look
at in Grafana (request rate, latency, error rate, requests by endpoint).

Usage:
    python scripts/generate_traffic.py
    python scripts/generate_traffic.py --base-url http://localhost:8000 --requests 300 --error-rate 0.05
"""
import argparse
import random
import time

import requests


def run(base_url: str, num_requests: int, error_rate: float, delay_seconds: float) -> None:
    products = requests.get(f"{base_url}/api/products", timeout=5).json()
    product_ids = [p["id"] for p in products]
    # An id guaranteed not to exist, used to deliberately generate 404s so
    # the "error rate" panel has something nonzero to show.
    invalid_product_id = max(product_ids, default=0) + 999

    ok = errors = 0
    for i in range(num_requests):
        action = random.choices(
            population=["browse", "order", "orders", "analytics", "bad_order"],
            weights=[0.35, 0.30, 0.15, 0.10, error_rate],
            k=1,
        )[0]

        try:
            if action == "browse":
                requests.get(f"{base_url}/api/products", timeout=5)
            elif action == "order":
                product_id = random.choice(product_ids)
                requests.post(
                    f"{base_url}/api/orders",
                    json={"product_id": product_id, "quantity": random.randint(1, 3)},
                    timeout=5,
                )
            elif action == "orders":
                requests.get(f"{base_url}/api/orders", timeout=5)
            elif action == "analytics":
                requests.get(f"{base_url}/api/analytics", timeout=5)
            elif action == "bad_order":
                requests.post(
                    f"{base_url}/api/orders",
                    json={"product_id": invalid_product_id, "quantity": 1},
                    timeout=5,
                )
            ok += 1
        except requests.RequestException as exc:
            errors += 1
            print(f"[{i}] request failed: {exc}")

        time.sleep(delay_seconds)

    print(f"Done. {ok} requests sent, {errors} client-side failures.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://localhost:8000")
    parser.add_argument("--requests", type=int, default=200, dest="num_requests")
    parser.add_argument("--error-rate", type=float, default=0.08, help="Fraction of requests that deliberately 404")
    parser.add_argument("--delay", type=float, default=0.15, dest="delay_seconds", help="Seconds between requests")
    args = parser.parse_args()

    run(args.base_url, args.num_requests, args.error_rate, args.delay_seconds)


if __name__ == "__main__":
    main()
