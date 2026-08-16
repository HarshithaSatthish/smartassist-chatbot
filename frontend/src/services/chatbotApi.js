const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
const TOKEN_KEY = "smartassist_token";
const USERNAME_KEY = "smartassist_username";

export class AuthError extends Error {
  constructor(message) {
    super(message);
    this.name = "AuthError";
  }
}

export function getToken() {
  return localStorage.getItem(TOKEN_KEY) || "";
}

export function getStoredUsername() {
  return localStorage.getItem(USERNAME_KEY) || "";
}

export function setSession(token, username) {
  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem(USERNAME_KEY, username);
}

export function clearSession() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USERNAME_KEY);
}

function authHeaders() {
  const headers = {
    "Content-Type": "application/json",
  };
  const token = getToken();
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }
  return headers;
}

async function readError(response, options = {}) {
  let detail = "Something went wrong. Please try again.";
  try {
    const errorBody = await response.json();
    if (errorBody.detail) {
      detail = errorBody.detail;
    }
  } catch {
    // Keep the default message if the body is not JSON.
  }

  if (response.status === 401 && !options.skipAuthClear) {
    clearSession();
    throw new AuthError(detail);
  }

  throw new Error(detail);
}

async function request(path, options = {}) {
  const { skipAuthClear = false, ...fetchOptions } = options;
  const response = await fetch(`${API_URL}${path}`, {
    ...fetchOptions,
    headers: {
      ...authHeaders(),
      ...(fetchOptions.headers || {}),
    },
  });

  if (!response.ok) {
    await readError(response, { skipAuthClear });
  }

  if (response.status === 204) {
    return null;
  }

  return response.json();
}

export async function register(username, password) {
  return request("/auth/register", {
    method: "POST",
    body: JSON.stringify({ username, password }),
    skipAuthClear: true,
  });
}

export async function login(username, password) {
  return request("/auth/login", {
    method: "POST",
    body: JSON.stringify({ username, password }),
    skipAuthClear: true,
  });
}

export async function getMe() {
  return request("/auth/me");
}

export async function listConversations() {
  return request("/conversations");
}

export async function createConversation() {
  return request("/conversations", { method: "POST" });
}

export async function getConversation(conversationId) {
  return request(`/conversations/${conversationId}`);
}

export async function deleteConversation(conversationId) {
  return request(`/conversations/${conversationId}`, { method: "DELETE" });
}

export async function sendMessage(message, conversationId) {
  const body = { message };
  if (conversationId) {
    body.conversation_id = conversationId;
  }
  return request("/chat", {
    method: "POST",
    body: JSON.stringify(body),
  });
}
