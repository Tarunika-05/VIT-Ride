import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  Typography,
  TextField,
  IconButton,
  Button,
  Paper,
  CircularProgress,
  Chip,
  Tooltip
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
import RestartAltIcon from '@mui/icons-material/RestartAlt';
import ReactMarkdown from 'react-markdown';
import api from '../api';

const SUGGESTED_QUERIES = [
  "Any bus from CMBT in the morning?",
  "Who drives Route 2?",
  "I am near Vadapalani, need to reach campus by 9 AM",
  "Which route goes through Velachery?",
  "13.090476, 80.215826"
];

export default function ChatPanel() {
  const [sessionId, setSessionId] = useState(() => 'sess_' + Math.random().toString(36).substring(2, 9));
  const [inputMessage, setInputMessage] = useState('');
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: `👋 **Hello! I am the VIT Chennai AI Campus Transit Assistant.**
I can help you with:
- Finding buses from any neighborhood in Chennai
- Goal-directed trip planning (walk + bus travel time)
- Comparing routes & boarding times
- Checking driver & faculty in-charge contacts

Ask me any question in plain English or select a suggested prompt below!`,
      latencyMs: null
    }
  ]);
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleSend = async (textToSend = null) => {
    const query = (textToSend || inputMessage).trim();
    if (!query || loading) return;

    // Append user message
    const newMessages = [...messages, { role: 'user', content: query }];
    setMessages(newMessages);
    setInputMessage('');
    setLoading(true);

    try {
      const data = await api.sendChatMessage(query, sessionId);
      setMessages([
        ...newMessages,
        {
          role: 'assistant',
          content: data.response || "No response received.",
          latencyMs: data.response_time_ms
        }
      ]);
    } catch (err) {
      setMessages([
        ...newMessages,
        {
          role: 'assistant',
          content: "⚠️ I encountered an error connecting to the transit server. Please check the backend connection.",
          latencyMs: null
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleResetChat = async () => {
    try {
      await api.clearChat(sessionId);
    } catch (e) {
      // Ignore
    }
    const newId = 'sess_' + Math.random().toString(36).substring(2, 9);
    setSessionId(newId);
    setMessages([
      {
        role: 'assistant',
        content: "New conversation started. How can I assist you with VIT campus routes today?",
        latencyMs: null
      }
    ]);
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%', p: 2, bgcolor: '#ffffff' }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1, pb: 1, borderBottom: 1, borderColor: 'divider' }}>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <AutoAwesomeIcon sx={{ color: '#0284c7', mr: 1 }} />
          <Typography variant="h6" sx={{ fontWeight: 700, color: '#0f172a' }}>
            AI Transit Assistant
          </Typography>
          <Chip label="LangGraph + Gemini + RAG" size="small" color="primary" variant="outlined" sx={{ ml: 1, height: 22, fontSize: '0.65rem' }} />
        </Box>
        <Tooltip title="Reset Conversation Session">
          <Button
            size="small"
            variant="outlined"
            startIcon={<RestartAltIcon />}
            onClick={handleResetChat}
            sx={{ textTransform: 'none', fontSize: '0.75rem' }}
          >
            New Chat
          </Button>
        </Tooltip>
      </Box>

      {/* Messages Stream */}
      <Box sx={{ flex: 1, overflowY: 'auto', pr: 1, mb: 1 }}>
        {messages.map((msg, index) => {
          const isUser = msg.role === 'user';
          return (
            <Box
              key={index}
              sx={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: isUser ? 'flex-end' : 'flex-start',
                mb: 1.5
              }}
            >
              <Paper
                elevation={0}
                sx={{
                  p: 1.5,
                  maxWidth: '85%',
                  borderRadius: 2,
                  bgcolor: isUser ? '#003366' : '#f1f5f9',
                  color: isUser ? '#ffffff' : '#0f172a',
                  border: isUser ? 'none' : '1px solid #e2e8f0',
                  fontSize: '0.9rem',
                  lineHeight: 1.5,
                  '& p': { m: 0, mb: 0.8 },
                  '& p:last-child': { mb: 0 },
                  '& ul, & ol': { pl: 2, my: 0.5 },
                  '& table': { width: '100%', borderCollapse: 'collapse', my: 1, fontSize: '0.8rem' },
                  '& th, & td': { border: '1px solid #cbd5e1', p: 0.5, textAlign: 'left' }
                }}
              >
                <ReactMarkdown>{msg.content}</ReactMarkdown>
              </Paper>
              {msg.latencyMs && (
                <Typography variant="caption" sx={{ color: 'text.secondary', fontSize: '0.65rem', mt: 0.3, px: 0.5 }}>
                  ⚡ Response time: {msg.latencyMs} ms
                </Typography>
              )}
            </Box>
          );
        })}

        {loading && (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, my: 1, p: 1 }}>
            <CircularProgress size={16} sx={{ color: '#0284c7' }} />
            <Typography variant="caption" sx={{ color: 'text.secondary', fontStyle: 'italic' }}>
              Assistant is analyzing routes and calculating journey durations...
            </Typography>
          </Box>
        )}
        <div ref={messagesEndRef} />
      </Box>

      {/* Suggested Quick Prompts */}
      <Box sx={{ display: 'flex', gap: 0.8, overflowX: 'auto', py: 0.8, mb: 1, '&::-webkit-scrollbar': { height: 4 } }}>
        {SUGGESTED_QUERIES.map((q, idx) => (
          <Chip
            key={idx}
            label={q}
            size="small"
            onClick={() => handleSend(q)}
            sx={{ cursor: 'pointer', fontSize: '0.72rem', flexShrink: 0, bgcolor: '#f8fafc', border: '1px solid #cbd5e1' }}
          />
        ))}
      </Box>

      {/* Input Field */}
      <Box sx={{ display: 'flex', gap: 1 }}>
        <TextField
          fullWidth
          size="small"
          placeholder="Ask a question about VIT routes, stops, or travel times..."
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault();
              handleSend();
            }
          }}
          disabled={loading}
        />
        <IconButton
          color="primary"
          onClick={() => handleSend()}
          disabled={loading || !inputMessage.trim()}
          sx={{ backgroundColor: '#003366', color: '#ffffff', '&:hover': { bgcolor: '#002244' } }}
        >
          <SendIcon />
        </IconButton>
      </Box>
    </Box>
  );
}
