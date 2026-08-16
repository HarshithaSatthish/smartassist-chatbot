function ConversationList({
  conversations,
  selectedId,
  onSelect,
  onNewChat,
  onDelete,
  open,
}) {
  return (
    <aside className={`history-sidebar ${open ? "open" : ""}`}>
      <div className="history-header">
        <h2>Chats</h2>
        <button type="button" className="new-chat-button" onClick={onNewChat}>
          New chat
        </button>
      </div>

      <ul className="history-list">
        {conversations.length === 0 && (
          <li className="history-empty">No chats yet. Send a message to start one.</li>
        )}
        {conversations.map((conversation) => {
          const selected = conversation.id === selectedId;
          return (
            <li key={conversation.id} className={`history-item ${selected ? "selected" : ""}`}>
              <button
                type="button"
                className="history-item-main"
                aria-current={selected ? "true" : undefined}
                onClick={() => onSelect(conversation.id)}
              >
                <span className="history-title">{conversation.title || "New chat"}</span>
              </button>
              <button
                type="button"
                className="history-delete"
                aria-label="Delete conversation"
                onClick={() => onDelete(conversation.id)}
              >
                Delete
              </button>
            </li>
          );
        })}
      </ul>
    </aside>
  );
}

export default ConversationList;
