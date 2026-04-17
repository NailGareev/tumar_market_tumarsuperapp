from __future__ import annotations

from typing import Any

import requests
from flask import Blueprint, jsonify, request

from storage import (
    create_shop_account,
    get_product,
    get_shop,
    get_shop_offers,
    list_products_short,
    list_shops,
    upsert_shop_offer,
)

seller_bp = Blueprint("seller", __name__)
RANKING_URL = "http://localhost:8090/rank/seller"


def rank_seller_offers(offers: list[dict[str, Any]]) -> list[dict[str, Any]]:
    try:
        response = requests.post(RANKING_URL, json={"offers": offers}, timeout=0.6)
        response.raise_for_status()
        return response.json().get("offers", offers)
    except Exception:
        return sorted(offers, key=lambda x: (x.get("delivery_days", 99), -x.get("stock", 0), x["price"]))


@seller_bp.post("/api/seller/register")
def register_seller() -> Any:
    payload = request.get_json(force=True)
    name = str(payload.get("name", "")).strip()
    city = str(payload.get("city", "")).strip()
    if not name or not city:
        return jsonify({"error": "name and city are required"}), 400

    return jsonify(create_shop_account(name, city)), 201


@seller_bp.get("/api/seller/list")
def seller_list() -> Any:
    return jsonify(list_shops())


@seller_bp.get("/api/seller/<int:seller_id>/offers")
def seller_offers(seller_id: int) -> Any:
    seller = get_shop(seller_id)
    if not seller:
        return jsonify({"error": "Seller not found"}), 404

    offers = rank_seller_offers(get_shop_offers(seller_id))
    return jsonify({"seller": seller, "offers": offers})


@seller_bp.post("/api/seller/<int:seller_id>/offers")
def upsert_offer(seller_id: int) -> Any:
    payload = request.get_json(force=True)
    required = ["product_id", "price", "stock", "delivery_days", "warranty_months"]
    if any(field not in payload for field in required):
        return jsonify({"error": f"required fields: {', '.join(required)}"}), 400

    if not get_shop(seller_id):
        return jsonify({"error": "Seller not found"}), 404

    product_id = int(payload["product_id"])
    if not get_product(product_id):
        return jsonify({"error": "Product not found"}), 404

    updated = upsert_shop_offer(seller_id, payload)
    return jsonify({"status": "ok", "updated": updated})


@seller_bp.get("/api/product/list")
def product_list() -> Any:
    return jsonify(list_products_short())
