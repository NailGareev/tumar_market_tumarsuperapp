from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

DB_FILE = Path(__file__).resolve().parent / "data" / "market.db"


def _connect() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_FILE)
    connection.row_factory = sqlite3.Row
    return connection


def init_db() -> None:
    DB_FILE.parent.mkdir(parents=True, exist_ok=True)

    with _connect() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                login TEXT NOT NULL UNIQUE,
                role TEXT NOT NULL DEFAULT 'seller',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS shops (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                city TEXT NOT NULL,
                rating REAL NOT NULL DEFAULT 5.0,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(account_id) REFERENCES accounts(id)
            );

            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                category TEXT NOT NULL,
                description TEXT NOT NULL,
                image TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS offers (
                product_id INTEGER NOT NULL,
                shop_id INTEGER NOT NULL,
                price INTEGER NOT NULL,
                stock INTEGER NOT NULL,
                delivery_days INTEGER NOT NULL,
                warranty_months INTEGER NOT NULL,
                PRIMARY KEY (product_id, shop_id),
                FOREIGN KEY(product_id) REFERENCES products(id),
                FOREIGN KEY(shop_id) REFERENCES shops(id)
            );
            """
        )

        count = conn.execute("SELECT COUNT(*) AS count FROM products").fetchone()["count"]
        if count == 0:
            _seed_db(conn)


def _seed_db(conn: sqlite3.Connection) -> None:
    conn.execute("INSERT INTO accounts (login, role) VALUES (?, ?)", ("techhub_owner", "seller"))
    conn.execute("INSERT INTO accounts (login, role) VALUES (?, ?)", ("mobilecity_owner", "seller"))

    conn.execute(
        "INSERT INTO shops (account_id, name, city, rating) VALUES (?, ?, ?, ?)",
        (1, "TechHub", "Алматы", 4.8),
    )
    conn.execute(
        "INSERT INTO shops (account_id, name, city, rating) VALUES (?, ?, ?, ?)",
        (2, "MobileCity", "Астана", 4.6),
    )

    conn.execute(
        "INSERT INTO products (title, category, description, image) VALUES (?, ?, ?, ?)",
        (
            "Смартфон Samsung Galaxy S24 256GB",
            "Смартфоны",
            "Флагманский смартфон с AMOLED экраном и мощной камерой.",
            "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=1200",
        ),
    )
    conn.execute(
        "INSERT INTO products (title, category, description, image) VALUES (?, ?, ?, ?)",
        (
            "Ноутбук Lenovo ThinkBook 14",
            "Ноутбуки",
            "Универсальный ноутбук для работы и учебы.",
            "https://images.unsplash.com/photo-1517336714739-489689fd1ca8?w=1200",
        ),
    )

    conn.execute(
        "INSERT INTO offers (product_id, shop_id, price, stock, delivery_days, warranty_months) VALUES (?, ?, ?, ?, ?, ?)",
        (1, 1, 389990, 7, 1, 12),
    )
    conn.execute(
        "INSERT INTO offers (product_id, shop_id, price, stock, delivery_days, warranty_months) VALUES (?, ?, ?, ?, ?, ?)",
        (1, 2, 394900, 12, 2, 12),
    )
    conn.execute(
        "INSERT INTO offers (product_id, shop_id, price, stock, delivery_days, warranty_months) VALUES (?, ?, ?, ?, ?, ?)",
        (2, 2, 329990, 4, 2, 24),
    )


def get_products_with_stats() -> list[dict[str, Any]]:
    with _connect() as conn:
        rows = conn.execute(
            """
            SELECT
                p.id,
                p.title,
                p.category,
                p.description,
                p.image,
                MIN(o.price) AS min_price,
                COUNT(o.product_id) AS offer_count,
                COUNT(DISTINCT o.shop_id) AS seller_count
            FROM products p
            LEFT JOIN offers o ON o.product_id = p.id
            GROUP BY p.id
            ORDER BY p.id
            """
        ).fetchall()
        return [dict(row) for row in rows]


def get_product(product_id: int) -> dict[str, Any] | None:
    with _connect() as conn:
        row = conn.execute(
            "SELECT id, title, category, description, image FROM products WHERE id = ?",
            (product_id,),
        ).fetchone()
        return dict(row) if row else None


def get_product_offers(product_id: int) -> list[dict[str, Any]]:
    with _connect() as conn:
        rows = conn.execute(
            """
            SELECT
                o.product_id,
                o.shop_id AS seller_id,
                o.price,
                o.stock,
                o.delivery_days,
                o.warranty_months,
                s.name AS seller_name,
                s.city AS seller_city,
                s.rating AS seller_rating
            FROM offers o
            JOIN shops s ON s.id = o.shop_id
            WHERE o.product_id = ?
            """,
            (product_id,),
        ).fetchall()
        return [dict(row) for row in rows]


def create_shop_account(name: str, city: str) -> dict[str, Any]:
    login_base = "".join(ch for ch in name.lower() if ch.isalnum()) or "seller"

    with _connect() as conn:
        existing_count = conn.execute(
            "SELECT COUNT(*) AS count FROM accounts WHERE login LIKE ?",
            (f"{login_base}%",),
        ).fetchone()["count"]
        login = f"{login_base}{existing_count + 1}"

        cursor = conn.execute(
            "INSERT INTO accounts (login, role) VALUES (?, 'seller')",
            (login,),
        )
        account_id = cursor.lastrowid

        shop_cursor = conn.execute(
            "INSERT INTO shops (account_id, name, city, rating) VALUES (?, ?, ?, ?)",
            (account_id, name, city, 5.0),
        )
        shop_id = shop_cursor.lastrowid

        return {"id": shop_id, "account_id": account_id, "login": login, "name": name, "city": city, "rating": 5.0}


def list_shops() -> list[dict[str, Any]]:
    with _connect() as conn:
        rows = conn.execute("SELECT id, name, city, rating FROM shops ORDER BY id").fetchall()
        return [dict(row) for row in rows]


def get_shop(shop_id: int) -> dict[str, Any] | None:
    with _connect() as conn:
        row = conn.execute("SELECT id, name, city, rating FROM shops WHERE id = ?", (shop_id,)).fetchone()
        return dict(row) if row else None


def get_shop_offers(shop_id: int) -> list[dict[str, Any]]:
    with _connect() as conn:
        rows = conn.execute(
            """
            SELECT
                o.product_id,
                o.shop_id AS seller_id,
                p.title AS product_title,
                o.price,
                o.stock,
                o.delivery_days,
                o.warranty_months
            FROM offers o
            JOIN products p ON p.id = o.product_id
            WHERE o.shop_id = ?
            """,
            (shop_id,),
        ).fetchall()
        return [dict(row) for row in rows]


def upsert_shop_offer(shop_id: int, payload: dict[str, Any]) -> bool:
    product_id = int(payload["product_id"])
    price = int(payload["price"])
    stock = int(payload["stock"])
    delivery_days = int(payload["delivery_days"])
    warranty_months = int(payload["warranty_months"])

    with _connect() as conn:
        existing = conn.execute(
            "SELECT 1 FROM offers WHERE product_id = ? AND shop_id = ?",
            (product_id, shop_id),
        ).fetchone()

        if existing:
            conn.execute(
                """
                UPDATE offers
                SET price = ?, stock = ?, delivery_days = ?, warranty_months = ?
                WHERE product_id = ? AND shop_id = ?
                """,
                (price, stock, delivery_days, warranty_months, product_id, shop_id),
            )
            return True

        conn.execute(
            """
            INSERT INTO offers (product_id, shop_id, price, stock, delivery_days, warranty_months)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (product_id, shop_id, price, stock, delivery_days, warranty_months),
        )
        return False


def list_products_short() -> list[dict[str, Any]]:
    with _connect() as conn:
        rows = conn.execute("SELECT id, title FROM products ORDER BY id").fetchall()
        return [dict(row) for row in rows]
