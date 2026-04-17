const productsContainer = document.getElementById("products");
const detail = document.getElementById("detail");

function formatKzt(value) {
  return new Intl.NumberFormat("ru-RU").format(value) + " ₸";
}

async function loadProducts() {
  const response = await fetch("/api/market/products");
  const items = await response.json();
  productsContainer.innerHTML = "";

  items.forEach((item) => {
    const node = document.createElement("article");
    node.className = "product";
    node.innerHTML = `
      <img src="${item.image}" alt="${item.title}">
      <h3>${item.title}</h3>
      <div class="muted">${item.category}</div>
      <div class="price">от ${formatKzt(item.min_price || 0)}</div>
      <div class="muted">Продавцов: ${item.seller_count}</div>
      <button data-id="${item.id}">Открыть карточку</button>
    `;

    node.querySelector("button").addEventListener("click", () => openCard(item.id));
    productsContainer.appendChild(node);
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
        Цена: <strong>${formatKzt(offer.price)}</strong>, остаток: ${offer.stock}, доставка: ${offer.delivery_days} дн.
      </div>
    `).join("")}
  `;
  detail.scrollIntoView({ behavior: "smooth" });
}

loadProducts();
