const sellerSelect = document.getElementById("seller-select");
const productSelect = document.getElementById("product-select");
const sellerOffers = document.getElementById("seller-offers");

const sellerName = document.getElementById("seller-name");
const sellerCity = document.getElementById("seller-city");
const registerResult = document.getElementById("register-result");

const offerPrice = document.getElementById("offer-price");
const offerStock = document.getElementById("offer-stock");
const offerDelivery = document.getElementById("offer-delivery");
const offerWarranty = document.getElementById("offer-warranty");

function formatKzt(value) {
  return new Intl.NumberFormat("ru-RU").format(value) + " ₸";
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
    sellerOffers.innerHTML = `<p class="muted">Ошибка: ${payload.error}</p>`;
    return;
  }

  sellerOffers.innerHTML = payload.offers.length
    ? payload.offers.map((offer) => `
      <div class="offer">
        <strong>${offer.product_title}</strong><br>
        Цена: ${formatKzt(offer.price)}, остаток: ${offer.stock}, доставка: ${offer.delivery_days} дн., гарантия: ${offer.warranty_months} мес.
      </div>
    `).join("")
    : `<p class="muted">Пока нет офферов.</p>`;
}

sellerSelect.addEventListener("change", () => loadSellerOffers(sellerSelect.value));

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
