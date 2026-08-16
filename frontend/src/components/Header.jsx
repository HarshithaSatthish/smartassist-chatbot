function Header({ username, onLogout, onToggleHistory, historyOpen }) {
  function handleBrandClick() {
    const pane = document.querySelector(".chat-window");
    pane?.scrollTo({ top: 0, behavior: "smooth" });
  }

  return (
    <header className="chat-header">
      <div className="header-left">
        <button
          type="button"
          className="menu-button"
          onClick={onToggleHistory}
          aria-expanded={historyOpen}
          aria-label={historyOpen ? "Hide chat history" : "Show chat history"}
        >
          Chats
        </button>
        <button
          type="button"
          className="logo logo-button"
          onClick={handleBrandClick}
          aria-label="Scroll conversation to top"
        >
          <img
            src="/smartassist-logo.png"
            alt=""
            width="40"
            height="40"
            draggable="false"
          />
        </button>
        <div>
          <h1>SmartAssist</h1>
          <p className="header-subtitle">
            AI Assistant
            <span className="online-badge">
              <span className="status-dot" aria-hidden="true" />
              Online
            </span>
          </p>
        </div>
      </div>
      <div className="header-actions">
        {username && (
          <span className="header-user" title={username}>
            {username}
          </span>
        )}
        <button type="button" className="clear-button" onClick={onLogout}>
          Logout
        </button>
      </div>
    </header>
  );
}

export default Header;
