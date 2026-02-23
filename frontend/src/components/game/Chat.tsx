import { useState, useEffect, useRef } from 'react';
import { useSocket } from '@/hooks/useSocket';
import { useGame } from '@/hooks/useGame';
import { motion, AnimatePresence } from 'framer-motion';

interface ChatMessage {
  player_id: string;
  display_name: string;
  message: string;
  timestamp: number;
}

export default function Chat() {
  const { socket } = useSocket();
  const { sendChat } = useGame();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [expanded, setExpanded] = useState(false);
  const [unread, setUnread] = useState(0);
  const messagesRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!socket) return;

    const handleMessage = (data: Omit<ChatMessage, 'timestamp'>) => {
      const msg = { ...data, timestamp: Date.now() };
      setMessages(prev => [...prev.slice(-49), msg]);
      if (!expanded) setUnread(prev => prev + 1);
    };

    socket.on('chat_message', handleMessage);
    return () => { socket.off('chat_message', handleMessage); };
  }, [socket, expanded]);

  useEffect(() => {
    if (expanded && messagesRef.current) {
      messagesRef.current.scrollTop = messagesRef.current.scrollHeight;
    }
  }, [messages, expanded]);

  const handleSend = () => {
    const trimmed = input.trim();
    if (trimmed) {
      sendChat(trimmed);
      setInput('');
    }
  };

  return (
    <div className="fixed bottom-4 left-4 z-40">
      <button
        onClick={() => { setExpanded(!expanded); setUnread(0); }}
        className="rounded-lg bg-card border border-border px-4 py-2.5 text-base font-semibold shadow-lg hover:bg-secondary transition relative"
      >
        💬 Chat
        {unread > 0 && (
          <span className="absolute -top-2 -right-2 rounded-full bg-primary px-2 py-0.5 text-sm text-primary-foreground">
            {unread}
          </span>
        )}
      </button>

      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ opacity: 0, y: 10, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 10, scale: 0.95 }}
            className="absolute bottom-12 left-0 w-72 rounded-xl bg-card border border-border shadow-2xl overflow-hidden"
          >
            <div
              ref={messagesRef}
              className="h-48 overflow-y-auto p-3 space-y-2"
            >
              {messages.length === 0 ? (
                <p className="text-sm text-muted-foreground text-center py-4">No messages yet</p>
              ) : (
                messages.map((msg, i) => (
                  <div key={i} className="text-sm">
                    <span className="font-semibold text-accent">{msg.display_name}: </span>
                    <span className="text-foreground/80">{msg.message}</span>
                  </div>
                ))
              )}
            </div>
            <div className="border-t border-border p-2 flex gap-1">
              <input
                type="text"
                value={input}
                onChange={e => setInput(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && handleSend()}
                placeholder="Type a message..."
                maxLength={200}
                className="flex-1 rounded bg-muted px-3 py-1.5 text-sm focus:outline-none"
              />
              <button
                onClick={handleSend}
                className="rounded bg-primary px-3 py-1.5 text-sm text-primary-foreground"
              >
                Send
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
