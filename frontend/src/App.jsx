import { useEffect, useState } from "react";
import Header from "./components/Header.jsx";
import ChatWindow from "./components/ChatWindow.jsx";
import MessageInput from "./components/MessageInput.jsx";
import LoginPage from "./components/LoginPage.jsx";
import ConversationList from "./components/ConversationList.jsx";
import {
  AuthError,
  CONNECT_ERROR,
  clearSession,
  createConversation,
  deleteConversation,
  getConversation,
  getMe,
  getStoredUsername,
  getToken,
  listConversations,
  sendMessage,
  setSession,
} from "./services/chatbotApi.js";

function createMessage(role, content, timestamp) {
  return {
    role,
    content,
    timestamp: timestamp || new Date().toISOString(),
  };
}

function getWelcomeMessages() {
  return [
    createMessage("bot", "Hello! I'm SmartAssist. How can I help you today?"),
  ];
}

function App() {
  const [authReady, setAuthReady] = useState(false);
  const [username, setUsername] = useState(getStoredUsername);
  const [messages, setMessages] = useState(getWelcomeMessages);
  const [conversations, setConversations] = useState([]);
  const [conversationId, setConversationId] = useState(null);
  const [historyOpen, setHistoryOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const isLoggedIn = Boolean(username && getToken());

  async function refreshConversations() {
    const items = await listConversations();
    setConversations(items);
    return items;
  }

  function handleAuthError(requestError) {
    if (requestError instanceof AuthError) {
      setUsername("");
      setConversations([]);
      setConversationId(null);
      setMessages(getWelcomeMessages());
      setError("");
      return true;
    }
    return false;
  }

  useEffect(() => {
    async function restoreSession() {
      if (!getToken()) {
        setAuthReady(true);
        return;
      }

      try {
        const me = await getMe();
        setUsername(me.username);
        setSession(getToken(), me.username);
        await refreshConversations();
      } catch (requestError) {
        if (requestError instanceof AuthError) {
          clearSession();
          setUsername("");
        } else if (getStoredUsername()) {
          setUsername(getStoredUsername());
        } else {
          clearSession();
          setUsername("");
        }
      } finally {
        setAuthReady(true);
      }
    }

    restoreSession();
  }, []);

  function handleLoggedIn(data) {
    setSession(data.access_token, data.username);
    setUsername(data.username);
    setMessages(getWelcomeMessages());
    setConversationId(null);
    setError("");
    refreshConversations().catch(() => {
      setConversations([]);
    });
  }

  function handleLogout() {
    clearSession();
    setUsername("");
    setConversations([]);
    setConversationId(null);
    setMessages(getWelcomeMessages());
    setHistoryOpen(false);
    setError("");
  }

  async function handleNewChat() {
    try {
      const created = await createConversation();
      setConversationId(created.id);
      setMessages(getWelcomeMessages());
      setError("");
      setHistoryOpen(false);
      await refreshConversations();
    } catch (requestError) {
      if (handleAuthError(requestError)) {
        return;
      }
      setError(requestError.message || "Unable to start a new chat.");
    }
  }

  async function handleSelectConversation(id) {
    try {
      const data = await getConversation(id);
      setConversationId(data.id);
      setMessages(
        data.messages && data.messages.length > 0
          ? data.messages
          : getWelcomeMessages()
      );
      setError("");
      setHistoryOpen(false);
    } catch (requestError) {
      if (handleAuthError(requestError)) {
        return;
      }
      setError(requestError.message || "Unable to load that conversation.");
    }
  }

  async function handleDeleteConversation(id) {
    const confirmed = window.confirm(
      "Delete this conversation? This cannot be undone."
    );
    if (!confirmed) {
      return;
    }

    try {
      await deleteConversation(id);
      await refreshConversations();
      if (conversationId === id) {
        setConversationId(null);
        setMessages(getWelcomeMessages());
      }
    } catch (requestError) {
      if (handleAuthError(requestError)) {
        return;
      }
      setError(requestError.message || "Unable to delete that conversation.");
    }
  }

  async function handleSend(text) {
    const userMessage = createMessage("user", text);
    setMessages((current) => [...current, userMessage]);
    setLoading(true);
    setError("");

    try {
      const data = await sendMessage(text, conversationId);
      const botMessage = createMessage("bot", data.reply);
      setMessages((current) => [...current, botMessage]);
      setConversationId(data.conversation_id);
      await refreshConversations();
    } catch (requestError) {
      if (handleAuthError(requestError)) {
        return;
      }

      const isNetworkError =
        requestError instanceof TypeError ||
        (requestError.message &&
          requestError.message.toLowerCase().includes("failed to fetch"));

      const displayError = isNetworkError
        ? CONNECT_ERROR
        : requestError.message || CONNECT_ERROR;

      setError(displayError);
      setMessages((current) => [
        ...current,
        createMessage("bot", displayError),
      ]);
    } finally {
      setLoading(false);
    }
  }

  if (!authReady) {
    return (
      <div className="boot-screen" role="status">
        Loading SmartAssist...
      </div>
    );
  }

  if (!isLoggedIn) {
    return <LoginPage onLoggedIn={handleLoggedIn} />;
  }

  return (
    <div className="app-shell app-shell-chat">
      {historyOpen && (
        <button
          type="button"
          className="history-backdrop"
          aria-label="Close chat history"
          onClick={() => setHistoryOpen(false)}
        />
      )}
      <div className="app-layout">
        <ConversationList
          conversations={conversations}
          selectedId={conversationId}
          onSelect={handleSelectConversation}
          onNewChat={handleNewChat}
          onDelete={handleDeleteConversation}
          open={historyOpen}
        />
        <div className="chat-card">
          <Header
            username={username}
            onLogout={handleLogout}
            onToggleHistory={() => setHistoryOpen((open) => !open)}
            historyOpen={historyOpen}
          />
          <ChatWindow messages={messages} loading={loading} error={error} />
          <MessageInput onSend={handleSend} disabled={loading} />
        </div>
      </div>
    </div>
  );
}

export default App;
