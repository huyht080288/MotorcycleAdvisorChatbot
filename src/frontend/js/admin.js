const loginSection = document.getElementById("loginSection");
const trainSection = document.getElementById("trainSection");
const loginForm = document.getElementById("loginForm");
const loginError = document.getElementById("loginError");
const fileList = document.getElementById("fileList");
const trainBtn = document.getElementById("trainBtn");
const logoutBtn = document.getElementById("logoutBtn");
const trainStatus = document.getElementById("trainStatus");

let token = localStorage.getItem("admin_token") || "";

function authHeaders() {
  return {
    "Content-Type": "application/json",
    Authorization: `Bearer ${token}`,
  };
}

function showTrainUI() {
  loginSection.classList.add("hidden");
  trainSection.classList.remove("hidden");
  loadFiles();
}

function showLoginUI() {
  token = "";
  localStorage.removeItem("admin_token");
  loginSection.classList.remove("hidden");
  trainSection.classList.add("hidden");
}

async function loadFiles() {
  fileList.innerHTML = "Đang tải danh sách file...";
  try {
    const res = await fetch("/api/admin/files", { headers: authHeaders() });
    if (res.status === 401) {
      showLoginUI();
      return;
    }
    if (!res.ok) {
      fileList.innerHTML =
        "<p class='error'>Không tải được danh sách file (lỗi " +
        res.status +
        "). Thử đăng xuất và đăng nhập lại.</p>";
      return;
    }
    const data = await res.json();
    if (!data.files.length) {
      fileList.innerHTML = "<p>Chưa có file JSON trong DataRef/.</p>";
      return;
    }
    fileList.innerHTML = data.files
      .map(
        (name) =>
          `<label><input type="checkbox" name="dataref" value="${name}"> ${name}</label>`
      )
      .join("");
  } catch {
    fileList.innerHTML = "<p class='error'>Không tải được danh sách file.</p>";
  }
}

loginForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  loginError.classList.add("hidden");
  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;

  try {
    const res = await fetch("/api/admin/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Đăng nhập thất bại");
    token = data.token;
    localStorage.setItem("admin_token", token);
    showTrainUI();
  } catch (err) {
    loginError.textContent = err.message;
    loginError.classList.remove("hidden");
  }
});

trainBtn.addEventListener("click", async () => {
  const selected = [...document.querySelectorAll('input[name="dataref"]:checked')].map(
    (el) => el.value
  );
  if (!selected.length) {
    trainStatus.textContent = "Vui lòng chọn ít nhất một file JSON.";
    trainStatus.classList.remove("hidden", "success");
    trainStatus.classList.add("error");
    return;
  }

  trainStatus.textContent = "Đang train...";
  trainStatus.classList.remove("hidden", "error", "success");

  try {
    const res = await fetch("/api/admin/train", {
      method: "POST",
      headers: authHeaders(),
      body: JSON.stringify({ files: selected }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Train thất bại");
    trainStatus.textContent = data.message;
    trainStatus.classList.add("success");
    trainStatus.classList.remove("error");
  } catch (err) {
    trainStatus.textContent = err.message;
    trainStatus.classList.add("error");
    trainStatus.classList.remove("success");
  }
});

logoutBtn.addEventListener("click", showLoginUI);

if (token) {
  showTrainUI();
}
