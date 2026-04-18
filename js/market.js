const categoryGrid = document.getElementById("category-grid");
const productsGrid = document.getElementById("products-grid");
const detail = document.getElementById("detail");

const categories = [
  { title: "Телефоны и гаджеты", image: "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=600" },
  { title: "Бытовая техника", image: "https://images.unsplash.com/photo-1586201375761-83865001e31c?w=600" },
  { title: "ТВ, Аудио, Видео", image: "https://images.unsplash.com/photo-1586717799252-bd134ad00e26?w=600" },
  { title: "Компьютеры", image: "https://images.unsplash.com/photo-1541807084-5c52b6b3adef?w=600" },
  { title: "Товары для дома", image: "https://images.unsplash.com/photo-1583845112239-97ef1341b271?w=600" },
  { title: "Красота и здоровье", image: "https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?w=600" },
  { title: "Детские товары", image: "https://images.unsplash.com/photo-1515488042361-ee00e0ddd4e4?w=600" },
  { title: "Аптека", image: "https://images.unsplash.com/photo-1587854692152-cbe660dbde88?w=600" },
  { title: "Одежда", image: "https://images.unsplash.com/photo-1445205170230-053b83016050?w=600" },
  { title: "Автотовары", image: "https://images.unsplash.com/photo-1487754180451-c456f719a1fc?w=600" }
];

function formatKzt(value) {
  return new Intl.NumberFormat("ru-RU").format(value) + " ₸";
}

function renderCategories() {
  categoryGrid.innerHTML = categories
    .map(
      (category) => `
        <article class="category-card">
          <h3>${category.title}</h3>
          <img src="${category.image}" alt="${category.title}" />
        </article>
      `
    )
    .join("");
}

async function loadProducts() {
  const response = await fetch("/api/market/products");
  const items = await response.json();
  productsGrid.innerHTML = "";

  items.forEach((item) => {
    const card = document.createElement("article");
    card.className = "product-card";
    card.innerHTML = `
      <img src="${item.image}" alt="${item.title}">
      <div class="product-title">${item.title}</div>
      <div class="muted">${item.category}</div>
      <div class="price">от ${formatKzt(item.min_price || 0)}</div>
      <div class="muted">Офферов: ${item.offer_count} · Продавцов: ${item.seller_count}</div>
      <button class="open-btn" data-id="${item.id}">Открыть карточку</button>
    `;

    card.querySelector("button").addEventListener("click", () => openCard(item.id));
    productsGrid.appendChild(card);
  });
}

async function openCard(productId) {
  const response = await fetch(`/api/market/products/${productId}`);
  const payload = await response.json();

  detail.classList.remove("hidden");
  detail.innerHTML = `
    <h2>${payload.product.title}</h2>
    <p class="muted">${payload.product.description}</p>
    <h3>Предложения продавцов</h3>
    ${payload.offers.map((offer) => `
      <div class="offer">
        <strong>${offer.seller_name}</strong> (${offer.seller_city}), рейтинг ${offer.seller_rating}<br>
        Цена: <strong>${formatKzt(offer.price)}</strong>, остаток: ${offer.stock}, доставка: ${offer.delivery_days} дн., гарантия: ${offer.warranty_months} мес.
      </div>
    `).join("")}
  `;

  detail.scrollIntoView({ behavior: "smooth" });
}

renderCategories();
loadProducts();
