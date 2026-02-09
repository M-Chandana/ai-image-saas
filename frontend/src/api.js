const API = "http://localhost:8000";

// ---------- AUTH ----------

export async function signup(email, password) {
  const res = await fetch(`${API}/signup`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });

  if (!res.ok) {
    throw new Error("Signup failed");
  }
}

export async function login(email, password) {
  const res = await fetch(`${API}/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });

  if (!res.ok) {
    throw new Error("Login failed");
  }

  const data = await res.json();
  localStorage.setItem("token", data.access_token);
}

// ---------- UPLOAD ----------

export async function uploadImage(file) {
  const token = localStorage.getItem("token");

  const fd = new FormData();
  fd.append("file", file);

  const res = await fetch(`${API}/upload`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
    },
    body: fd,
  });

  if (!res.ok) {
    throw new Error("Upload failed");
  }

  return await res.json();
}

// ---------- JOBS ----------

export async function getJobs() {
  const token = localStorage.getItem("token");

  const res = await fetch(`${API}/jobs`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!res.ok) {
    throw new Error("Unauthorized");
  }

  return await res.json();
}
