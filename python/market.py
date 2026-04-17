from __future__ import annotations

from typing import Any

import requests
from flask import Blueprint, jsonify

from storage import read_store

market_bp = Blueprint("market", __name__)
RANKING_URL = "http://localhost:8090/rank/market"


def attach_seller(offer: dict[str, Any], sellers: list[dict[str, Any]]) -> dict[str, Any]:
    seller_map = {s["id"]: s for s in sellers}
    seller = seller_map.get(offer["seller_id"], {})
    return {
        **offer,
        "seller_name": seller.get("name", "Неизвестный продавец"),
        "seller_city": seller.get("city", "—"),
        "seller_rating": seller.get("rating", 0),
    }


def rank_market_offers(offers: list[dict[str, Any]]) -> list[dict[str, Any]]:
    try:
        response = requests.post(RANKING_URL, json={"offers": offers}, timeout=0.6)
        response.raise_for_status()
        return response.json().get("offers", offers)
    except Exception:
        return sorted(offers, key=lambda x: (x["price"], -x.get("seller_rating", 0), x.get("delivery_days", 99)))


@market_bp.get("/api/market/products")
def market_products() -> Any:
    data = read_store()
    offers = data["offers"]

    min_prices: dict[int, int] = {}
    for offer in offers:
        product_id = offer["product_id"]
        min_prices[product_id] = min(min_prices.get(product_id, offer["price"]), offer["price"])

    items = []
    for product in data["products"]:
        product_offers = [o for o in offers if o["product_id"] == product["id"]]
        items.append({
            **product,
            "min_price": min_prices.get(product["id"]),
            "offer_count": len(product_offers),
            "seller_count": len({o["seller_id"] for o in product_offers}),
        })

    return jsonify(items)


@market_bp.get("/api/market/products/<int:product_id>")
def market_product_card(product_id: int) -> Any:
    data = read_store()
    product = next((p for p in data["products"] if p["id"] == product_id), None)
    if not product:
        return jsonify({"error": "Product not found"}), 404

    offers = [
        attach_seller(offer, data["sellers"])
        for offer in data["offers"]
        if offer["product_id"] == product_id
    ]
    return jsonify({"product": product, "offers": rank_market_offers(offers)})
