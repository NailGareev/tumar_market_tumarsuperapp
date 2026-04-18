from __future__ import annotations

from pathlib import Path

from flask import Flask, send_from_directory

from market import market_bp
from seller import seller_bp
from storage import init_db

ROOT_DIR = Path(__file__).resolve().parent.parent
HTML_DIR = ROOT_DIR / "html"
CSS_DIR = ROOT_DIR / "css"
JS_DIR = ROOT_DIR / "js"

app = Flask(__name__)
init_db()
app.register_blueprint(market_bp)
app.register_blueprint(seller_bp)


@app.get("/")
def home() -> str:
    return send_from_directory(HTML_DIR, "market.html")


@app.get("/market")
def market_page() -> str:
    return send_from_directory(HTML_DIR, "market.html")


@app.get("/seller")
def seller_page() -> str:
    return send_from_directory(HTML_DIR, "seller.html")


@app.get("/css/<path:filename>")
def css_file(filename: str) -> str:
    return send_from_directory(CSS_DIR, filename)


@app.get("/js/<path:filename>")
def js_file(filename: str) -> str:
    return send_from_directory(JS_DIR, filename)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
