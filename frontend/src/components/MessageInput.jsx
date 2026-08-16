import { useState } from "react";

function MessageInput({ onSend, disabled }) {
  const [text, setText] = useState("");

  function submitMessage() {
    const trimmed = text.trim();
    if (!trimmed || disabled) {
      return;
    }
    onSend(trimmed);
    setText("");
  }

  function handleSubmit(event) {
    event.preventDefault();
    submitMessage();
  }

  function handleKeyDown(event) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      submitMessage();
    }
  }

  return (
    <form className="message-input" onSubmit={handleSubmit}>
      <label htmlFor="chat-input" className="sr-only">
        Type your message
      </label>
      <textarea
        id="chat-input"
        rows="1"
        value={text}
        onChange={(event) => setText(event.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={disabled ? "Please wait..." : "Start your search..."}
        disabled={disabled}
      />
      <button type="submit" disabled={disabled || !text.trim()} aria-label="Send">
        <svg className="send-icon" viewBox="0 0 24 24" aria-hidden="true">
          <path d="M2.01 21 23 12 2.01 3 2 10l15 2-15 2z" />
        </svg>
      </button>
    </form>
  );
}

export default MessageInput;
