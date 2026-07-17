const CATEGORY_LABELS = {
  electric: "Xe điện",
  petrol: "Xe máy",
  promo: "Khuyến mãi",
  fifty_cc: "Xe 50cc",
  service: "Dịch vụ",
  price: "Bảng giá",
  news: "Tin tức",
};

function createElement(tag, className, text) {
  const element = document.createElement(tag);
  if (className) element.className = className;
  if (text !== undefined) element.textContent = text;
  return element;
}

function renderCategories(categories = []) {
  const grid = document.getElementById("categoryGrid");
  grid.replaceChildren(...categories.map((category) => {
    const link = createElement("a", "category-card");
    link.href = `#${category.target}`;
    const image = createElement("img", "category-image");
    image.src = category.image;
    image.alt = "";
    image.loading = "lazy";
    link.append(
      image,
      createElement("span", "category-shade"),
      createElement("span", "category-icon", category.icon),
      createElement("span", "category-label", category.label),
      createElement("small", "", `${category.count || 0} nội dung`)
    );
    return link;
  }));
}

function createProductCard(item, compact = false) {
  const card = createElement("article", `product-card${compact ? " compact" : ""}`);
  const media = createElement("div", `product-media brand-${(item.brand || "other").toLowerCase().replace(/\s+/g, "-")}`);

  if (item.image) {
    const image = createElement("img");
    image.src = item.image;
    image.alt = item.title;
    image.loading = "lazy";
    media.append(image);
  } else {
    media.append(
      createElement("span", "media-brand", item.brand || "Minh Long"),
      createElement("span", "media-bike", item.category === "electric" ? "⚡" : "🏍️")
    );
  }
  if (item.badge) media.append(createElement("span", "product-badge", item.badge));

  const body = createElement("div", "product-body");
  const meta = createElement("div", "product-meta");
  meta.append(
    createElement("span", "", item.brand || "Minh Long"),
    createElement("span", "", CATEGORY_LABELS[item.category] || "")
  );
  body.append(meta, createElement("h3", "", item.title));
  if (!compact) body.append(createElement("p", "", item.summary));
  body.append(createElement("strong", "card-price", item.price ? `Từ ${item.price}` : "Liên hệ"));

  const actions = createElement("div", "card-actions");
  const detail = createElement("a", "detail-link", "Xem chi tiết");
  detail.href = item.source_url || "#";
  detail.target = item.source_url ? "_blank" : "";
  detail.rel = item.source_url ? "noopener" : "";
  const ask = createElement("button", "card-ask-btn", "Tư vấn");
  ask.type = "button";
  ask.addEventListener("click", () => window.askChatbot?.(item.question));
  actions.append(detail, ask);
  body.append(actions);
  card.append(media, body);
  return card;
}

function renderProducts(containerId, items = [], compact = false) {
  const grid = document.getElementById(containerId);
  if (!items.length) {
    grid.replaceChildren(createElement("p", "empty-note", "Nội dung đang được cập nhật."));
    return;
  }
  grid.replaceChildren(...items.map((item) => createProductCard(item, compact)));
}

function renderBrands(brands = []) {
  const list = document.getElementById("brandList");
  list.replaceChildren(...brands.map((brand) => createElement("span", "brand-pill", brand)));
}

function renderServices(services = []) {
  const grid = document.getElementById("serviceGrid");
  grid.replaceChildren(...services.map((service) => {
    const card = createElement("article", "service-card");
    card.append(
      createElement("span", "service-icon", service.icon),
      createElement("h3", "", service.title),
      createElement("p", "", service.description)
    );
    const button = createElement("button", "service-link", "Tìm hiểu thêm →");
    button.type = "button";
    button.addEventListener("click", () => window.askChatbot?.(service.question));
    card.append(button);
    return card;
  }));
}

function renderNews(items = []) {
  const grid = document.getElementById("newsGrid");
  if (!items.length) {
    grid.replaceChildren(createElement("p", "empty-note", "Tin tức đang được cập nhật."));
    return;
  }
  grid.replaceChildren(...items.map((item, index) => {
    const article = createElement("article", `news-card${index === 0 ? " news-featured" : ""}`);
    const visual = createElement("div", "news-visual");
    if (item.image) visual.style.backgroundImage = `url("${item.image}")`;
    visual.append(createElement("span", "", item.brand), createElement("b", "", "TIN XE"));
    const content = createElement("div", "news-content");
    content.append(createElement("span", "news-tag", "Tin mới"), createElement("h3", "", item.title));
    if (index === 0) content.append(createElement("p", "", item.summary));
    const link = createElement("a", "text-link", "Đọc bài viết →");
    link.href = item.source_url;
    link.target = "_blank";
    link.rel = "noopener";
    content.append(link);
    article.append(visual, content);
    return article;
  }));
}

function renderBranches(branches = []) {
  const grid = document.getElementById("branchGrid");
  grid.replaceChildren(...branches.map((branch, index) => {
    const card = createElement("article", "branch-card");
    const number = createElement("span", "branch-number", String(index + 1).padStart(2, "0"));
    card.append(number, createElement("h3", "", branch.name), createElement("p", "", branch.address));
    const phone = createElement("a", "branch-phone", `☎ ${branch.phone}`);
    phone.href = `tel:${branch.phone.replace(/\D/g, "")}`;
    const map = createElement("a", "branch-map", "Chỉ đường ↗");
    map.href = `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(branch.address)}`;
    map.target = "_blank";
    map.rel = "noopener";
    const actions = createElement("div", "branch-actions");
    actions.append(phone, map);
    card.append(actions);
    return card;
  }));
}

function renderQuickQuestions(questions = []) {
  const wrap = document.getElementById("quickQuestions");
  wrap.replaceChildren(...questions.map((question) => {
    const chip = createElement("button", "chip", question);
    chip.type = "button";
    chip.addEventListener("click", () => window.askChatbot?.(question));
    return chip;
  }));
}

function renderHero(data) {
  document.getElementById("storeName").textContent = data.store_name;
  document.getElementById("heroTitle").textContent = data.hero.title;
  document.getElementById("heroSubtitle").textContent = data.hero.subtitle;
  const list = document.getElementById("heroHighlights");
  list.replaceChildren(...(data.hero.highlights || []).map((item) => createElement("li", "", item)));
}

function showLoadError() {
  ["featuredGrid", "electricGrid", "petrolGrid", "fiftyGrid", "promoGrid", "newsGrid"].forEach((id) => {
    document.getElementById(id)?.replaceChildren(
      createElement("p", "empty-note", "Không tải được nội dung. Vui lòng kiểm tra kết nối backend.")
    );
  });
}

async function loadSiteContent() {
  try {
    const response = await fetch("/api/site-content");
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const data = await response.json();
    renderHero(data);
    renderCategories(data.categories);
    renderBrands(data.brands);
    renderProducts("featuredGrid", data.featured);
    renderProducts("electricGrid", data.collections?.electric, true);
    renderProducts("petrolGrid", data.collections?.petrol, true);
    renderProducts("fiftyGrid", data.collections?.fifty_cc, true);
    renderProducts("promoGrid", data.promotions);
    renderServices(data.services);
    renderNews(data.news);
    renderBranches(data.branches);
    renderQuickQuestions(data.quick_questions);
  } catch {
    showLoadError();
  }
}

["navOpenChat", "heroOpenChat", "footerOpenChat"].forEach((id) => {
  document.getElementById(id)?.addEventListener("click", (event) => {
    event.preventDefault();
    window.openChatbot?.();
  });
});

const menuToggle = document.getElementById("menuToggle");
const mainNav = document.querySelector(".main-nav");
menuToggle?.addEventListener("click", () => {
  const isOpen = mainNav.classList.toggle("is-open");
  menuToggle.setAttribute("aria-expanded", String(isOpen));
});
mainNav?.querySelectorAll("a").forEach((link) => link.addEventListener("click", () => {
  mainNav.classList.remove("is-open");
  menuToggle?.setAttribute("aria-expanded", "false");
}));

loadSiteContent();
