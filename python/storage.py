from __future__ import annotations

from pathlib import Path
from typing import Any

import pymysql
from pymysql.cursors import DictCursor
from pymysql.err import OperationalError

DEFAULT_SETTINGS = {
    "DB_HOST": "127.0.0.1",
    "DB_PORT": "3306",
    "DB_USER": "root",
    "DB_PASSWORD": "",
    "DB_NAME": "tumar_market",
}

SETTINGS_FILE = Path(__file__).resolve().parent.parent / "settings.txt"


def _load_settings() -> dict[str, str]:
    values = DEFAULT_SETTINGS.copy()

    if not SETTINGS_FILE.exists():
        SETTINGS_FILE.write_text(
            "\n".join([
                "# MySQL settings",
                "DB_HOST=127.0.0.1",
                "DB_PORT=3306",
                "DB_USER=root",
                "DB_PASSWORD=",
                "DB_NAME=tumar_market",
                "",
            ]),
            encoding="utf-8",
        )
        return values

    for line in SETTINGS_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if key in values:
            if key != "DB_PASSWORD" and value == "":
                continue
            values[key] = value

    return values


SETTINGS = _load_settings()
DB_HOST = SETTINGS["DB_HOST"]
DB_PORT = int(SETTINGS["DB_PORT"])
DB_USER = SETTINGS["DB_USER"]
DB_PASSWORD = SETTINGS["DB_PASSWORD"]
DB_NAME = SETTINGS["DB_NAME"]


def _server_connect() -> pymysql.connections.Connection:
    return pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        autocommit=True,
        cursorclass=DictCursor,
        charset="utf8mb4",
    )


def _db_connect() -> pymysql.connections.Connection:
    return pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        autocommit=True,
        cursorclass=DictCursor,
        charset="utf8mb4",
    )


def init_db() -> None:
    try:
        with _server_connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    f"CREATE DATABASE IF NOT EXISTS {DB_NAME} "
                    "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
                )

        with _db_connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS accounts (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        login VARCHAR(120) NOT NULL UNIQUE,
                        role VARCHAR(50) NOT NULL DEFAULT 'seller',
                        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                    """
                )
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS shops (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        account_id INT NOT NULL,
                        name VARCHAR(255) NOT NULL,
                        city VARCHAR(120) NOT NULL,
                        rating DECIMAL(3,2) NOT NULL DEFAULT 5.00,
                        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        CONSTRAINT fk_shops_account FOREIGN KEY (account_id) REFERENCES accounts(id)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                    """
                )
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS products (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        title VARCHAR(255) NOT NULL,
                        category VARCHAR(120) NOT NULL,
                        description TEXT NOT NULL,
                        image TEXT NOT NULL
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                    """
                )
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS offers (
                        product_id INT NOT NULL,
                        shop_id INT NOT NULL,
                        price INT NOT NULL,
                        stock INT NOT NULL,
                        delivery_days INT NOT NULL,
                        warranty_months INT NOT NULL,
                        PRIMARY KEY (product_id, shop_id),
                        CONSTRAINT fk_offers_product FOREIGN KEY (product_id) REFERENCES products(id),
                        CONSTRAINT fk_offers_shop FOREIGN KEY (shop_id) REFERENCES shops(id)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                    """
                )

                cursor.execute("SELECT COUNT(*) AS count FROM products")
                if cursor.fetchone()["count"] == 0:
                    _seed_db(cursor)
    except OperationalError as error:
        raise RuntimeError(
            f"MySQL connection failed: {error}. Check settings in {SETTINGS_FILE}."
        ) from error


def _seed_db(cursor: DictCursor) -> None:
    cursor.execute("INSERT INTO accounts (login, role) VALUES (%s, %s)", ("techhub_owner", "seller"))
    cursor.execute("INSERT INTO accounts (login, role) VALUES (%s, %s)", ("mobilecity_owner", "seller"))

    cursor.execute(
        "INSERT INTO shops (account_id, name, city, rating) VALUES (%s, %s, %s, %s)",
        (1, "TechHub", "Алматы", 4.8),
    )
    cursor.execute(
        "INSERT INTO shops (account_id, name, city, rating) VALUES (%s, %s, %s, %s)",
        (2, "MobileCity", "Астана", 4.6),
    )

    cursor.execute(
        "INSERT INTO products (title, category, description, image) VALUES (%s, %s, %s, %s)",
        (
            "Смартфон Samsung Galaxy S24 256GB",
            "Смартфоны",
            "Флагманский смартфон с AMOLED экраном и мощной камерой.",
            "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=1200",
        ),
    )
    cursor.execute(
        "INSERT INTO products (title, category, description, image) VALUES (%s, %s, %s, %s)",
        (
            "Ноутбук Lenovo ThinkBook 14",
            "Ноутбуки",
            "Универсальный ноутбук для работы и учебы.",
            "https://images.unsplash.com/photo-1517336714739-489689fd1ca8?w=1200",
        ),
    )

    cursor.execute(
        "INSERT INTO offers (product_id, shop_id, price, stock, delivery_days, warranty_months) VALUES (%s, %s, %s, %s, %s, %s)",
        (1, 1, 389990, 7, 1, 12),
    )
    cursor.execute(
        "INSERT INTO offers (product_id, shop_id, price, stock, delivery_days, warranty_months) VALUES (%s, %s, %s, %s, %s, %s)",
        (1, 2, 394900, 12, 2, 12),
    )
    cursor.execute(
        "INSERT INTO offers (product_id, shop_id, price, stock, delivery_days, warranty_months) VALUES (%s, %s, %s, %s, %s, %s)",
        (2, 2, 329990, 4, 2, 24),
    )


def get_products_with_stats() -> list[dict[str, Any]]:
    with _db_connect() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
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
            )
            return list(cursor.fetchall())


def get_product(product_id: int) -> dict[str, Any] | None:
    with _db_connect() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT id, title, category, description, image FROM products WHERE id = %s",
                (product_id,),
            )
            return cursor.fetchone()


def get_product_offers(product_id: int) -> list[dict[str, Any]]:
    with _db_connect() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
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
                WHERE o.product_id = %s
                """,
                (product_id,),
            )
            return list(cursor.fetchall())


def create_shop_account(name: str, city: str) -> dict[str, Any]:
    login_base = "".join(char for char in name.lower() if char.isalnum()) or "seller"

    with _db_connect() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) AS count FROM accounts WHERE login LIKE %s", (f"{login_base}%",))
            login = f"{login_base}{cursor.fetchone()['count'] + 1}"

            cursor.execute("INSERT INTO accounts (login, role) VALUES (%s, 'seller')", (login,))
            account_id = cursor.lastrowid

            cursor.execute(
                "INSERT INTO shops (account_id, name, city, rating) VALUES (%s, %s, %s, %s)",
                (account_id, name, city, 5.0),
            )
            shop_id = cursor.lastrowid

            return {
                "id": shop_id,
                "account_id": account_id,
                "login": login,
                "name": name,
                "city": city,
                "rating": 5.0,
            }


def list_shops() -> list[dict[str, Any]]:
    with _db_connect() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, name, city, rating FROM shops ORDER BY id")
            return list(cursor.fetchall())


def get_shop(shop_id: int) -> dict[str, Any] | None:
    with _db_connect() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, name, city, rating FROM shops WHERE id = %s", (shop_id,))
            return cursor.fetchone()


def get_shop_offers(shop_id: int) -> list[dict[str, Any]]:
    with _db_connect() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
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
                WHERE o.shop_id = %s
                """,
                (shop_id,),
            )
            return list(cursor.fetchall())


def upsert_shop_offer(shop_id: int, payload: dict[str, Any]) -> bool:
    product_id = int(payload["product_id"])
    price = int(payload["price"])
    stock = int(payload["stock"])
    delivery_days = int(payload["delivery_days"])
    warranty_months = int(payload["warranty_months"])

    with _db_connect() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT 1 FROM offers WHERE product_id = %s AND shop_id = %s",
                (product_id, shop_id),
            )
            exists = cursor.fetchone() is not None

            if exists:
                cursor.execute(
                    """
                    UPDATE offers
                    SET price = %s, stock = %s, delivery_days = %s, warranty_months = %s
                    WHERE product_id = %s AND shop_id = %s
                    """,
                    (price, stock, delivery_days, warranty_months, product_id, shop_id),
                )
                return True

            cursor.execute(
                """
                INSERT INTO offers (product_id, shop_id, price, stock, delivery_days, warranty_months)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (product_id, shop_id, price, stock, delivery_days, warranty_months),
            )
            return False


def list_products_short() -> list[dict[str, Any]]:
    with _db_connect() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, title FROM products ORDER BY id")
            return list(cursor.fetchall())
