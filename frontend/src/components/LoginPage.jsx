import { useState } from "react";
import { CONNECT_ERROR, login, register } from "../services/chatbotApi.js";

function LoginPage({ onLoggedIn }) {
  const [mode, setMode] = useState("login");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [shake, setShake] = useState(false);
  const [invalidFields, setInvalidFields] = useState({
    username: false,
    password: false,
  });

  const isRegister = mode === "register";

  function flashInvalid(nextInvalid) {
    setInvalidFields(nextInvalid);
    setShake(true);
  }

  async function handleSubmit(event) {
    event.preventDefault();
    const trimmedUser = username.trim();
    if (!trimmedUser || !password) {
      setError("Please enter a username and password.");
      flashInvalid({
        username: !trimmedUser,
        password: !password,
      });
      return;
    }

    setLoading(true);
    setError("");
    setInvalidFields({ username: false, password: false });

    try {
      const data = isRegister
        ? await register(trimmedUser, password)
        : await login(trimmedUser, password);
      onLoggedIn(data);
    } catch (requestError) {
      const isNetworkError =
        requestError instanceof TypeError ||
        (requestError.message &&
          requestError.message.toLowerCase().includes("failed to fetch"));
      setError(
        isNetworkError
          ? CONNECT_ERROR
          : requestError.message || "Something went wrong. Please try again."
      );
      flashInvalid({ username: false, password: false });
    } finally {
      setLoading(false);
    }
  }

  function toggleMode() {
    setMode(isRegister ? "login" : "register");
    setError("");
    setShake(false);
    setInvalidFields({ username: false, password: false });
  }

  return (
    <div className="login-shell">
      <div className="login-card">
        <div className="login-brand">
          <div className="logo login-logo" aria-hidden="true">
            <img
              src="/smartassist-logo.png"
              alt=""
              width="64"
              height="64"
              draggable="false"
            />
          </div>
          <h1>SmartAssist</h1>
          <p>
            {isRegister
              ? "Create an account to save your chat history."
              : "Log in to continue your conversations."}
          </p>
        </div>

        <form
          className={`login-form${shake ? " shake" : ""}${error ? " has-error" : ""}`}
          onSubmit={handleSubmit}
          onAnimationEnd={() => setShake(false)}
        >
          <label htmlFor="username">
            Username
            <input
              id="username"
              name="username"
              autoComplete="username"
              className={invalidFields.username ? "invalid" : undefined}
              value={username}
              onChange={(event) => {
                setUsername(event.target.value);
                if (invalidFields.username) {
                  setInvalidFields((current) => ({ ...current, username: false }));
                }
              }}
              placeholder="your_name"
              disabled={loading}
            />
          </label>
          <label htmlFor="password">
            Password
            <input
              id="password"
              name="password"
              type="password"
              autoComplete={isRegister ? "new-password" : "current-password"}
              className={invalidFields.password ? "invalid" : undefined}
              value={password}
              onChange={(event) => {
                setPassword(event.target.value);
                if (invalidFields.password) {
                  setInvalidFields((current) => ({ ...current, password: false }));
                }
              }}
              placeholder="At least 6 characters"
              disabled={loading}
            />
          </label>

          {error && (
            <p className="error-banner" role="alert">
              {error}
            </p>
          )}

          <button className="login-submit" type="submit" disabled={loading}>
            {loading ? "Please wait..." : isRegister ? "Create account" : "Log in"}
          </button>
        </form>

        <p className="login-toggle">
          {isRegister ? "Already have an account?" : "New here?"}{" "}
          <button type="button" onClick={toggleMode} disabled={loading}>
            {isRegister ? "Log in" : "Create an account"}
          </button>
        </p>
      </div>
    </div>
  );
}

export default LoginPage;
