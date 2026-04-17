from __future__ import annotations

from typing import Any

import requests
from flask import Blueprint, jsonify, request

from storage import read_store, write_store

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

    data = read_store()
    new_id = max((s["id"] for s in data["sellers"]), default=0) + 1
    seller = {"id": new_id, "name": name, "city": city, "rating": 5.0}
    data["sellers"].append(seller)
    write_store(data)
    return jsonify(seller), 201


@seller_bp.get("/api/seller/list")
def list_sellers() -> Any:
    return jsonify(read_store()["sellers"])


@seller_bp.get("/api/seller/<int:seller_id>/offers")
def seller_offers(seller_id: int) -> Any:
    data = read_store()
    seller = next((s for s in data["sellers"] if s["id"] == seller_id), None)
    if not seller:
        return jsonify({"error": "Seller not found"}), 404

    products = {p["id"]: p for p in data["products"]}
    offers = [
        {
            **offer,
            "product_title": products.get(offer["product_id"], {}).get("title", "Unknown"),
        }
        for offer in data["offers"] if offer["seller_id"] == seller_id
    ]

    return jsonify({"seller": seller, "offers": rank_seller_offers(offers)})


@seller_bp.post("/api/seller/<int:seller_id>/offers")
def upsert_offer(seller_id: int) -> Any:
    payload = request.get_json(force=True)
    required = ["product_id", "price", "stock", "delivery_days", "warranty_months"]
    if any(field not in payload for field in required):
        return jsonify({"error": f"required fields: {', '.join(required)}"}), 400

    data = read_store()
    seller = next((s for s in data["sellers"] if s["id"] == seller_id), None)
    if not seller:
        return jsonify({"error": "Seller not found"}), 404

    product_id = int(payload["product_id"])
    product = next((p for p in data["products"] if p["id"] == product_id), None)
    if not product:
        return jsonify({"error": "Product not found"}), 404

    updated = False
    for offer in data["offers"]:
        if offer["seller_id"] == seller_id and offer["product_id"] == product_id:
            offer.update(
                price=int(payload["price"]),
                stock=int(payload["stock"]),
                delivery_days=int(payload["delivery_days"]),
                warranty_months=int(payload["warranty_months"]),
            )
            updated = True
            break

    if not updated:
        data["offers"].append(
            {
                "product_id": product_id,
                "seller_id": seller_id,
                "price": int(payload["price"]),
                "stock": int(payload["stock"]),
                "delivery_days": int(payload["delivery_days"]),
                "warranty_months": int(payload["warranty_months"]),
            }
        )

    write_store(data)
    return jsonify({"status": "ok", "updated": updated})


@seller_bp.get("/api/product/list")
def product_list() -> Any:
    products = [{"id": p["id"], "title": p["title"]} for p in read_store()["products"]]
    return jsonify(products)
