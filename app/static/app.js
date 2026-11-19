const state = { category: "", query: "", routes: [], map: null, routeLayer: null };
const grid = document.querySelector("#places-grid");
const resultCount = document.querySelector("#result-count");
const emptyState = document.querySelector("#empty-state");
const dialog = document.querySelector("#place-dialog");

async function api(path) {
  const response = await fetch(path);
  if (!response.ok) throw new Error(`API error: ${response.status}`);
  return response.json();
}

function imageFallback(event) {
  event.currentTarget.src = "data:image/svg+xml;charset=UTF-8," + encodeURIComponent(`<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 800 500'><rect fill='#dce8dc' width='800' height='500'/><path fill='#176b4d' d='M0 400L180 220l120 120 100-90 230 150z'/><circle fill='#d7f26b' cx='620' cy='130' r='65'/></svg>`);
}

function card(item) {
  const article = document.createElement("article");
  article.className = "place-card";
  article.innerHTML = `
    <div class="place-image"><img src="${item.image}" alt="${item.name}" loading="lazy"><span>${item.category}</span></div>
    <div class="place-body">
      <div class="place-meta"><span>★ ${item.rating}</span><span>${item.price ? `€${item.price}` : "Безкоштовно"}</span></div>
      <h3>${item.name}</h3><p>${item.description}</p>
      <button type="button">Детальніше</button>
    </div>`;
  article.querySelector("img").addEventListener("error", imageFallback, { once: true });
  article.querySelector("button").addEventListener("click", () => openPlace(item.id));
  return article;
}

async function loadPlaces() {
  const params = new URLSearchParams();
  if (state.query) params.set("q", state.query);
  if (state.category) params.set("category", state.category);
  grid.setAttribute("aria-busy", "true");
  try {
    const data = await api(`/api/attractions?${params}`);
    grid.replaceChildren(...data.items.map(card));
    resultCount.textContent = `${data.count} ${data.count === 1 ? "місце" : "місць"}`;
    emptyState.hidden = data.count !== 0;
  } catch (error) {
    resultCount.textContent = "Помилка завантаження";
    console.error(error);
  } finally {
    grid.removeAttribute("aria-busy");
  }
}

async function openPlace(id) {
  const item = await api(`/api/attractions/${id}`);
  document.querySelector("#dialog-content").innerHTML = `
    <div class="dialog-hero" style="background-image:linear-gradient(0deg,rgba(5,20,14,.75),transparent),url('${item.image}')">
      <h2 id="dialog-title">${item.name}</h2>
    </div>
    <div class="dialog-body">
      <p>${item.description}</p>
      <div class="dialog-stats"><span>${item.category}</span><span>★ ${item.rating}</span><span>${item.price ? `€${item.price}` : "Вхід вільний"}</span><span>${item.latitude}, ${item.longitude}</span></div>
      <h3>Пов’язані факти</h3>
      <ul class="facts">${item.semantic_facts.length ? item.semantic_facts.map(fact => `<li><strong>${fact.subject}</strong> — ${fact.object}<br>${fact.evidence}</li>`).join("") : "<li>Семантичні факти ще не додані.</li>"}</ul>
    </div>`;
  dialog.showModal();
}

async function loadCategories() {
  const categories = await api("/api/categories");
  const filters = document.querySelector("#filters");
  categories.forEach(category => {
    const button = document.createElement("button");
    button.textContent = category.name;
    button.dataset.category = category.id;
    filters.append(button);
  });
  filters.addEventListener("click", event => {
    const button = event.target.closest("button");
    if (!button) return;
    filters.querySelectorAll("button").forEach(item => item.classList.toggle("active", item === button));
    state.category = button.dataset.category;
    loadPlaces();
  });
}

function showRoute(route, button) {
  document.querySelectorAll(".route-button").forEach(item => item.classList.toggle("active", item === button));
  if (state.routeLayer) state.routeLayer.remove();
  const points = route.stops.map(stop => [stop.latitude, stop.longitude]);
  const markers = route.stops.map(stop => L.marker([stop.latitude, stop.longitude]).bindPopup(`<strong>${stop.position}. ${stop.name}</strong>`));
  const line = L.polyline(points, { color: "#176b4d", weight: 5, opacity: .85 });
  state.routeLayer = L.featureGroup([...markers, line]).addTo(state.map);
  state.map.fitBounds(state.routeLayer.getBounds().pad(.18));
}

async function loadRoutes() {
  const data = await api("/api/routes");
  state.routes = data.items;
  state.map = L.map("map", { scrollWheelZoom: false }).setView([50.4501, 30.5234], 13);
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", { maxZoom: 19, attribution: "© OpenStreetMap" }).addTo(state.map);
  const list = document.querySelector("#route-list");
  const seasons = { spring: "весна", summer: "літо", autumn: "осінь", winter: "зима" };
  data.items.forEach((route, index) => {
    const button = document.createElement("button");
    button.className = "route-button";
    button.innerHTML = `<strong>${route.name}</strong><span>${route.stops.length} зупинок · ${seasons[route.season] || route.season}</span>`;
    button.addEventListener("click", () => showRoute(route, button));
    list.append(button);
    if (index === 0) showRoute(route, button);
  });
}

document.querySelector("#search-form").addEventListener("submit", event => {
  event.preventDefault();
  state.query = document.querySelector("#search-input").value.trim();
  loadPlaces();
  document.querySelector("#places").scrollIntoView();
});
document.querySelectorAll("[data-query]").forEach(button => button.addEventListener("click", () => {
  document.querySelector("#search-input").value = button.dataset.query;
  state.query = button.dataset.query;
  loadPlaces();
  document.querySelector("#places").scrollIntoView();
}));
document.querySelector("#reset-search").addEventListener("click", () => {
  state.query = ""; state.category = "";
  document.querySelector("#search-input").value = "";
  document.querySelectorAll("#filters button").forEach((button, index) => button.classList.toggle("active", index === 0));
  loadPlaces();
});
document.querySelector(".dialog-close").addEventListener("click", () => dialog.close());
dialog.addEventListener("click", event => { if (event.target === dialog) dialog.close(); });

Promise.all([loadCategories(), loadPlaces(), loadRoutes()]).catch(console.error);
