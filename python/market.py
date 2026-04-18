from __future__ import annotations

from typing import Any

import requests
from flask import Blueprint, jsonify

from storage import get_product, get_product_offers, get_products_with_stats

market_bp = Blueprint("market", __name__)
RANKING_URL = "http://localhost:8090/rank/market"


def rank_market_offers(offers: list[dict[str, Any]]) -> list[dict[str, Any]]:
    try:
        response = requests.post(RANKING_URL, json={"offers": offers}, timeout=0.6)
        response.raise_for_status()
        return response.json().get("offers", offers)
    except Exception:
        return sorted(offers, key=lambda x: (x["price"], -x.get("seller_rating", 0), x.get("delivery_days", 99)))


@market_bp.get("/api/market/products")
def market_products() -> Any:
    return jsonify(get_products_with_stats())


@market_bp.get("/api/market/products/<int:product_id>")
def market_product_card(product_id: int) -> Any:
    product = get_product(product_id)
    if not product:
        return jsonify({"error": "Product not found"}), 404

    offers = get_product_offers(product_id)
    return jsonify({"product": product, "offers": rank_market_offers(offers)})
