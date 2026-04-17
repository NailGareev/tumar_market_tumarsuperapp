# Tumar SuperApp Market (Kaspi-like MVP)

Проект хранит **все данные в SQLite базе**: товары, аккаунты продавцов, магазины и офферы.

## Что важно

- При первом запуске Python-приложения база создается автоматически: `python/data/market.db`.
- Также автоматически создаются таблицы и демо-данные (если база пустая).

## Структура

- `html/market.html` — страница витрины.
- `html/seller.html` — страница кабинета продавца.
- `css/market.css` — стили витрины.
- `css/seller.css` — стили кабинета.
- `python/app.py` — Flask-приложение и инициализация БД на старте.
- `python/market.py` — API витрины/карточки товара.
- `python/seller.py` — API кабинета продавца.
- `python/storage.py` — слой SQLite (создание БД, CRUD, сидирование).
- `go/main.go` — Go-сервис ранжирования.
- `go/market_rank.go` — ранжирование офферов для витрины.
- `go/seller_rank.go` — ранжирование офферов в кабинете продавца.

## Запуск

### 1) Go сервис

```bash
cd go
go run .
```

Сервис: `http://localhost:8090`.

### 2) Python API + веб

```bash
cd python
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Сайт: `http://localhost:8000/market`

## Основные URL

- `GET /market` — витрина товаров.
- `GET /seller` — кабинет продавца.
- `GET /api/market/products`
- `GET /api/market/products/<product_id>`
- `POST /api/seller/register`
- `GET /api/seller/list`
- `GET /api/seller/<seller_id>/offers`
- `POST /api/seller/<seller_id>/offers`
