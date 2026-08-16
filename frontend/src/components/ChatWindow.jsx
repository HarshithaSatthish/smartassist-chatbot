import { useEffect, useRef } from "react";
import Message from "./Message.jsx";

function ChatWindow({ messages, loading, error }) {
  const endRef = useRef(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  return (
    <section className="chat-window" aria-live="polite">
      {messages.map((message, index) => (
        <Message key={`${message.timestamp}-${index}`} message={message} />
      ))}

      {loading && (
        <div className="message-row bot">
          <div className="avatar avatar-bot" aria-hidden="true">
            <img
              src="/smartassist-logo.png"
              alt=""
              width="36"
              height="36"
              draggable="false"
            />
          </div>
          <div className="message-body">
            <p className="message-text typing">
              <span />
              <span />
              <span />
            </p>
            <span className="message-time">SmartAssist is typing</span>
          </div>
        </div>
      )}

      {error && !loading && (
        <p className="error-banner" role="alert">
          {error}
        </p>
      )}

      <div ref={endRef} />
    </section>
  );
}

export default ChatWindow;
