function formatTime(timestamp) {
  return new Date(timestamp).toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  });
}

function Message({ message }) {
  const isUser = message.role === "user";

  return (
    <article className={`message-row ${isUser ? "user" : "bot"}`}>
      <div className={`avatar ${isUser ? "avatar-user" : "avatar-bot"}`} aria-hidden="true">
        {isUser ? (
          "You"
        ) : (
          <img
            src="/smartassist-logo.png"
            alt=""
            width="36"
            height="36"
            draggable="false"
          />
        )}
      </div>
      <div className="message-body">
        <p className="message-text">{message.content}</p>
        <time className="message-time" dateTime={message.timestamp}>
          {formatTime(message.timestamp)}
        </time>
      </div>
    </article>
  );
}

export default Message;
