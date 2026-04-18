const sellerSelect = document.getElementById("seller-select");
const productSelect = document.getElementById("product-select");
const sellerOffers = document.getElementById("seller-offers");
const searchOffer = document.getElementById("search-offer");

const sellerName = document.getElementById("seller-name");
const sellerCity = document.getElementById("seller-city");
const registerResult = document.getElementById("register-result");

const offerPrice = document.getElementById("offer-price");
const offerStock = document.getElementById("offer-stock");
const offerDelivery = document.getElementById("offer-delivery");
const offerWarranty = document.getElementById("offer-warranty");

let currentOffers = [];

function formatKzt(value) {
  return new Intl.NumberFormat("ru-RU").format(value) + " ₸";
}

function switchPage(name) {
  document.querySelectorAll(".page").forEach((page) => page.classList.remove("active"));
  document.querySelectorAll(".side-link").forEach((button) => button.classList.remove("active"));

  document.getElementById(`page-${name}`).classList.add("active");
  const activeButton = document.querySelector(`.side-link[data-page='${name}']`);
  if (activeButton) activeButton.classList.add("active");
}

document.querySelectorAll(".side-link").forEach((button) => {
  button.addEventListener("click", () => switchPage(button.dataset.page));
});
document.querySelector("[data-open-add]").addEventListener("click", () => switchPage("add"));
document.querySelector("[data-open-products]").addEventListener("click", () => switchPage("products"));

function renderOffers() {
  const query = searchOffer.value.trim().toLowerCase();
  const filtered = currentOffers.filter((offer) => offer.product_title.toLowerCase().includes(query));

  sellerOffers.innerHTML = filtered.length
    ? filtered.map((offer) => `
      <tr>
        <td>${offer.product_title}</td>
        <td>${formatKzt(offer.price)}</td>
        <td>RP1</td>
        <td>${offer.stock}</td>
      </tr>
    `).join("")
    : `<tr><td colspan="4" class="muted">Нет подходящих товаров.</td></tr>`;
}

async function loadLists() {
  const sellers = await (await fetch("/api/seller/list")).json();
  const products = await (await fetch("/api/product/list")).json();

  sellerSelect.innerHTML = sellers.map((seller) => `<option value="${seller.id}">${seller.name} (${seller.city})</option>`).join("");
  productSelect.innerHTML = products.map((product) => `<option value="${product.id}">${product.title}</option>`).join("");

  if (sellers.length) {
    await loadSellerOffers(sellers[0].id);
  }
}

async function loadSellerOffers(sellerId) {
  const response = await fetch(`/api/seller/${sellerId}/offers`);
  const payload = await response.json();

  if (!response.ok) {
    currentOffers = [];
    sellerOffers.innerHTML = `<tr><td colspan="4" class="muted">Ошибка: ${payload.error}</td></tr>`;
    return;
  }

  currentOffers = payload.offers;
  renderOffers();
}

sellerSelect.addEventListener("change", () => loadSellerOffers(sellerSelect.value));
searchOffer.addEventListener("input", renderOffers);

document.getElementById("register-seller").addEventListener("click", async () => {
  const response = await fetch("/api/seller/register", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name: sellerName.value.trim(), city: sellerCity.value.trim() }),
  });

  const payload = await response.json();
  registerResult.textContent = response.ok ? `Создан продавец: ID ${payload.id}` : `Ошибка: ${payload.error}`;

  if (response.ok) {
    await loadLists();
  }
});

document.getElementById("save-offer").addEventListener("click", async () => {
  const sellerId = sellerSelect.value;
  const body = {
    product_id: Number(productSelect.value),
    price: Number(offerPrice.value),
    stock: Number(offerStock.value),
    delivery_days: Number(offerDelivery.value),
    warranty_months: Number(offerWarranty.value),
  };

  const response = await fetch(`/api/seller/${sellerId}/offers`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  const payload = await response.json();
  if (!response.ok) {
    alert(payload.error);
    return;
  }

  await loadSellerOffers(sellerId);
  alert(payload.updated ? "Оффер обновлен" : "Оффер добавлен");
});

loadLists();
