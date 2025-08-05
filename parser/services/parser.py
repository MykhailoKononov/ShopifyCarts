import httpx
from typing import List

TARGET_SUM = 200.0
CONCURRENCY = 3
TIMEOUT = 10.0
DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/115.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "X-Requested-With": "XMLHttpRequest",
}


class ShopifyParser:
    def __init__(self, url: str):
        self.shop_url = url
        self.error_message = ""
        self.status = ""

    async def fetch_available_variants(self, client: httpx.AsyncClient) -> List[dict | None]:
        variants = []
        url = f"{self.shop_url}/products.json"
        try:
            resp = await client.get(
                url,
                params={"limit": 250, "page": 1},
                headers=DEFAULT_HEADERS,
                timeout=TIMEOUT
            )
            resp.raise_for_status()
        except httpx.HTTPStatusError as exc:
            self.error_message = f"Error fetching catalog | {exc.response.status_code}"
            return []
        except httpx.RequestError as exc:
            self.error_message = (
                f"Network error: {str(exc)}"
            )
            return []
        data = resp.json()
        products = data.get("products", [])
        if not products:
            self.error_message = f"No items found"
            self.status = "failed"
            return []
        for prod in products:
            for var in prod.get("variants", []):
                if var.get("available"):
                    variants.append({"id": var["id"], "price": float(var["price"])})
        self.error_message = ""
        self.status = "success"
        return variants

    async def add_to_cart(self, client: httpx.AsyncClient, item_id: int, qty: int = 1):
        url = f"{self.shop_url}/cart/add.js"
        payload = {"id": item_id, "quantity": qty}
        resp = await client.post(url, json=payload, timeout=TIMEOUT)
        resp.raise_for_status()
        price = resp.json().get("discounted_price", "original_price")
        return price / 100.0

    async def build_cart(self, client: httpx.AsyncClient) -> str:
        error_message = ""
        variants = await self.fetch_available_variants(client)
        if not variants:
            return ""

        variants.sort(key=lambda v: -v["price"])
        picked = []
        used_ids = set()

        total_price = 0.0

        idx = 0
        while total_price < TARGET_SUM and idx < len(variants):
            vid = variants[idx]["id"]
            if vid not in used_ids:
                price = await self.add_to_cart(client, vid, 1)
                total_price += price
                used_ids.add(vid)
                picked.append(vid)
            idx += 1

        pairs = ",".join(f"{vid}:1" for vid in picked)
        cart_url = f"{self.shop_url}/cart/{pairs}"

        return cart_url
