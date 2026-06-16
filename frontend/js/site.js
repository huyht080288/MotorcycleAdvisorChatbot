const CATEGORY_LABELS = {
  electric: "Xe điện",
  petrol: "Xe xăng",
  promo: "Khuyến mãi",
  fifty_cc: "Xe 50cc",
  service: "Dịch vụ",
  contact: "Liên hệ",
  price: "Bảng giá",
  news: "Tin tức",
};

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text || "";
  return div.innerHTML;
}

function renderCategories(categories) {
  const grid = document.getElementById("categoryGrid");
  grid.innerHTML = categories
    .map(
      (cat) => `
      <button type="button" class="category-card" data-question="${escapeHtml(cat.question)}">
        <span class="category-icon">${cat.icon}</span>
        <span class="category-label">${escapeHtml(cat.label)}</span>
      </button>`
    )
    .join("");

  grid.querySelectorAll(".category-card").forEach((btn) => {
    btn.addEventListener("click", () => {
      const q = btn.dataset.question;
      if (window.askChatbot) window.askChatbot(q);
    });
  });
}

function renderProductCard(item, variant = "product") {
  const price = item.price
    ? `<span class="card-price">${escapeHtml(item.price)}</span>`
    : "";
  const cat = CATEGORY_LABELS[item.category] || "";
  return `
    <article class="card ${variant}-card" data-question="${escapeHtml(item.question)}">
      <span class="card-tag">${escapeHtml(cat)}</span>
      <h3>${escapeHtml(item.title)}</h3>
      <p>${escapeHtml(item.summary)}</p>
      ${price}
      <button type="button" class="card-ask-btn">Hỏi chatbot</button>
    </article>`;
}

function bindCardAskButtons(container) {
  container.querySelectorAll("[data-question]").forEach((card) => {
    const ask = () => {
      if (window.askChatbot) window.askChatbot(card.dataset.question);
    };
    card.querySelector(".card-ask-btn")?.addEventListener("click", (e) => {
      e.stopPropagation();
      ask();
    });
    card.addEventListener("click", ask);
  });
}

function renderFeatured(items) {
  const grid = document.getElementById("featuredGrid");
  if (!items.length) {
    grid.innerHTML = "<p class='empty-note'>Chưa có dữ liệu xe nổi bật.</p>";
    return;
  }
  grid.innerHTML = items.map((item) => renderProductCard(item)).join("");
  bindCardAskButtons(grid);
}

function renderPromos(items) {
  const grid = document.getElementById("promoGrid");
  if (!items.length) {
    grid.innerHTML = "<p class='empty-note'>Chưa có khuyến mãi.</p>";
    return;
  }
  grid.innerHTML = items.map((item) => renderProductCard(item, "promo")).join("");
  bindCardAskButtons(grid);
}

function renderServices(services) {
  const grid = document.getElementById("serviceGrid");
  grid.innerHTML = services
    .map(
      (s) => `
    <article class="card service-card" data-question="${escapeHtml(s.question)}">
      <h3>${escapeHtml(s.title)}</h3>
      <p>${escapeHtml(s.description)}</p>
      <button type="button" class="card-ask-btn">Tư vấn thêm</button>
    </article>`
    )
    .join("");
  bindCardAskButtons(grid);
}

function renderBranches(branches) {
  const grid = document.getElementById("branchGrid");
  grid.innerHTML = branches
    .map(
      (b) => `
    <article class="card branch-card">
      <h3>${escapeHtml(b.name)}</h3>
      <p>${escapeHtml(b.address)}</p>
      <button type="button" class="card-ask-btn branch-ask" data-question="Địa chỉ cửa hàng ${escapeHtml(b.name)}?">
        Hỏi đường đi
      </button>
    </article>`
    )
    .join("");

  grid.querySelectorAll(".branch-ask").forEach((btn) => {
    btn.addEventListener("click", (e) => {
      e.stopPropagation();
      if (window.askChatbot) window.askChatbot(btn.dataset.question);
    });
  });
}

function renderQuickQuestions(questions) {
  const wrap = document.getElementById("quickQuestions");
  wrap.innerHTML = questions
    .map(
      (q) =>
        `<button type="button" class="chip" data-question="${escapeHtml(q)}">${escapeHtml(q)}</button>`
    )
    .join("");

  wrap.querySelectorAll(".chip").forEach((chip) => {
    chip.addEventListener("click", () => {
      if (window.askChatbot) window.askChatbot(chip.dataset.question);
    });
  });
}

function renderHero(data) {
  document.getElementById("storeName").textContent = data.store_name;
  document.getElementById("heroTitle").textContent = data.hero.title;
  document.getElementById("heroSubtitle").textContent = data.hero.subtitle;
  document.getElementById("hotline").textContent = data.hotline;
  document.getElementById("statEntries").textContent = data.entry_count || "—";

  const list = document.getElementById("heroHighlights");
  list.innerHTML = (data.hero.highlights || [])
    .map((h) => `<li>${escapeHtml(h)}</li>`)
    .join("");
}

async function loadSiteContent() {
  try {
    const res = await fetch("/api/site-content");
    const data = await res.json();
    renderHero(data);
    renderCategories(data.categories);
    renderFeatured(data.featured);
    renderPromos(data.promotions);
    renderServices(data.services);
    renderBranches(data.branches);
    renderQuickQuestions(data.quick_questions);
  } catch {
    document.getElementById("featuredGrid").innerHTML =
      "<p class='empty-note'>Không tải được nội dung. Vui lòng chạy server backend.</p>";
  }
}

document.getElementById("navOpenChat")?.addEventListener("click", (e) => {
  e.preventDefault();
  if (window.openChatbot) window.openChatbot();
});

document.getElementById("heroOpenChat")?.addEventListener("click", (e) => {
  e.preventDefault();
  if (window.openChatbot) window.openChatbot();
});

loadSiteContent();
