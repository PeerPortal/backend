import React, { useState, useEffect, useRef } from 'react';
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  Grid,
  Button,
  TextField,
  Avatar,
  Paper,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
  Badge,
  IconButton,
  Chip,
  Divider,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import {
  Send as SendIcon,
  AttachFile as AttachFileIcon,
  EmojiEmotions as EmojiIcon,
  Search as SearchIcon,
  Add as AddIcon,
  MoreVert as MoreVertIcon,
  Phone as PhoneIcon,
  VideoCall as VideoCallIcon,
  Info as InfoIcon,
  SmartToy as AIIcon,
} from '@mui/icons-material';

// 导入AI聊天组件
import AIConsultationChat from '../components/AIConsultationChat';

const ChatPage = () => {
  const [selectedRoom, setSelectedRoom] = useState(null);
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState([]);
  const [chatRooms, setChatRooms] = useState([]);
  const [aiChatOpen, setAiChatOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const messagesEndRef = useRef(null);

  // 模拟聊天房间数据
  const mockChatRooms = [
    {
      id: 1,
      room_type: 'private',
      other_user: {
        id: 1,
        username: 'alice_cs',
        full_name: 'Alice Wang',
        avatar_url: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Alice',
        online_status: 'online',
        last_seen: null
      },
      last_message: {
        content: '好的，我来帮你看看文书',
        sender_id: 1,
        created_at: '2024-07-24T15:30:00Z'
      },
      unread_count: 2,
      updated_at: '2024-07-24T15:30:00Z'
    },
    {
      id: 2,
      room_type: 'private',
      other_user: {
        id: 2,
        username: 'bob_finance',
        full_name: 'Bob Chen',
        avatar_url: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Bob',
        online_status: 'offline',
        last_seen: '2024-07-24T12:00:00Z'
      },
      last_message: {
        content: '面试准备的资料我发给你了',
        sender_id: 2,
        created_at: '2024-07-24T10:15:00Z'
      },
      unread_count: 0,
      updated_at: '2024-07-24T10:15:00Z'
    },
    {
      id: 3,
      room_type: 'private',
      other_user: {
        id: 3,
        username: 'carol_ai',
        full_name: 'Carol Liu',
        avatar_url: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Carol',
        online_status: 'away',
        last_seen: '2024-07-24T14:00:00Z'
      },
      last_message: {
        content: '申请材料看起来不错，有几个地方可以优化',
        sender_id: 3,
        created_at: '2024-07-23T16:45:00Z'
      },
      unread_count: 1,
      updated_at: '2024-07-23T16:45:00Z'
    }
  ];

  // 模拟消息数据
  const mockMessages = {
    1: [
      {
        id: 1,
        sender_id: 1,
        content: '你好！看到你的申请需求了，我可以帮你看看文书',
        message_type: 'text',
        created_at: '2024-07-24T15:25:00Z'
      },
      {
        id: 2,
        sender_id: 999, // 当前用户ID
        content: '太好了！我现在还在准备PS，想请你帮忙看看思路对不对',
        message_type: 'text',
        created_at: '2024-07-24T15:28:00Z'
      },
      {
        id: 3,
        sender_id: 1,
        content: '好的，我来帮你看看文书。你可以把草稿发给我，我会详细批注',
        message_type: 'text',
        created_at: '2024-07-24T15:30:00Z'
      },
      {
        id: 4,
        sender_id: 999,
        content: '谢谢！我马上整理一下发给你',
        message_type: 'text',
        created_at: '2024-07-24T15:32:00Z'
      }
    ],
    2: [
      {
        id: 5,
        sender_id: 2,
        content: '关于MBA面试，我给你准备了一些常见问题',
        message_type: 'text',
        created_at: '2024-07-24T10:10:00Z'
      },
      {
        id: 6,
        sender_id: 2,
        content: '面试准备的资料我发给你了',
        message_type: 'text',
        created_at: '2024-07-24T10:15:00Z'
      }
    ],
    3: [
      {
        id: 7,
        sender_id: 3,
        content: '申请材料看起来不错，有几个地方可以优化',
        message_type: 'text',
        created_at: '2024-07-23T16:45:00Z'
      }
    ]
  };

  useEffect(() => {
    setChatRooms(mockChatRooms);
    // 默认选择第一个聊天室
    if (mockChatRooms.length > 0) {
      setSelectedRoom(mockChatRooms[0]);
      setMessages(mockMessages[mockChatRooms[0].id] || []);
    }
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleRoomSelect = (room) => {
    setSelectedRoom(room);
    setMessages(mockMessages[room.id] || []);
    
    // 标记消息为已读
    setChatRooms(prev => prev.map(r => 
      r.id === room.id ? { ...r, unread_count: 0 } : r
    ));
  };

  const handleSendMessage = () => {
    if (!message.trim() || !selectedRoom) return;

    const newMessage = {
      id: Date.now(),
      sender_id: 999, // 当前用户ID
      content: message,
      message_type: 'text',
      created_at: new Date().toISOString()
    };

    setMessages(prev => [...prev, newMessage]);
    setMessage('');

    // 更新聊天室的最后消息
    setChatRooms(prev => prev.map(room => 
      room.id === selectedRoom.id 
        ? { 
            ...room, 
            last_message: {
              content: message,
              sender_id: 999,
              created_at: new Date().toISOString()
            },
            updated_at: new Date().toISOString()
          }
        : room
    ));
  };

  const formatTime = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInMinutes = Math.floor((now - date) / (1000 * 60));
    
    if (diffInMinutes < 1) return '刚刚';
    if (diffInMinutes < 60) return `${diffInMinutes}分钟前`;
    if (diffInMinutes < 1440) return `${Math.floor(diffInMinutes / 60)}小时前`;
    return date.toLocaleDateString();
  };

  const getOnlineStatusColor = (status) => {
    switch (status) {
      case 'online': return 'success';
      case 'away': return 'warning';
      case 'offline': return 'error';
      default: return 'default';
    }
  };

  const filteredRooms = chatRooms.filter(room =>
    room.other_user.full_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    room.other_user.username.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <Container maxWidth="xl" sx={{ py: 2, height: '100vh' }}>
      <Grid container spacing={2} sx={{ height: 'calc(100vh - 32px)' }}>
        {/* 聊天列表侧边栏 */}
        <Grid item xs={12} md={4} lg={3}>
          <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
            {/* 头部 */}
            <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">消息</Typography>
                <Box>
                  <IconButton
                    onClick={() => setAiChatOpen(true)}
                    sx={{ 
                      background: 'linear-gradient(45deg, #ff6b6b, #ffa500)',
                      color: 'white',
                      mr: 1,
                      '&:hover': {
                        background: 'linear-gradient(45deg, #ff5252, #ff9800)',
                      }
                    }}
                    size="small"
                  >
                    <AIIcon />
                  </IconButton>
                  <IconButton>
                    <AddIcon />
                  </IconButton>
                </Box>
              </Box>
              
              {/* 搜索框 */}
              <TextField
                fullWidth
                size="small"
                placeholder="搜索联系人..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                InputProps={{
                  startAdornment: <SearchIcon sx={{ color: 'text.secondary', mr: 1 }} />
                }}
              />
            </Box>

            {/* 聊天室列表 */}
            <Box sx={{ flex: 1, overflow: 'auto' }}>
              <List sx={{ p: 0 }}>
                {filteredRooms.map((room) => (
                  <ListItem
                    key={room.id}
                    button
                    selected={selectedRoom?.id === room.id}
                    onClick={() => handleRoomSelect(room)}
                    sx={{
                      borderBottom: 1,
                      borderColor: 'divider',
                      '&.Mui-selected': {
                        backgroundColor: 'primary.light',
                        '&:hover': {
                          backgroundColor: 'primary.light',
                        }
                      }
                    }}
                  >
                    <ListItemAvatar>
                      <Badge
                        color={getOnlineStatusColor(room.other_user.online_status)}
                        variant="dot"
                        invisible={room.other_user.online_status === 'offline'}
                        anchorOrigin={{
                          vertical: 'bottom',
                          horizontal: 'right',
                        }}
                      >
                        <Avatar src={room.other_user.avatar_url} />
                      </Badge>
                    </ListItemAvatar>
                    <ListItemText
                      primary={
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <Typography variant="subtitle2" noWrap>
                            {room.other_user.full_name}
                          </Typography>
                          {room.unread_count > 0 && (
                            <Badge badgeContent={room.unread_count} color="error" />
                          )}
                        </Box>
                      }
                      secondary={
                        <Box>
                          <Typography
                            variant="body2"
                            color="text.secondary"
                            noWrap
                            sx={{ mb: 0.5 }}
                          >
                            {room.last_message?.content || '暂无消息'}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {formatTime(room.last_message?.created_at || room.updated_at)}
                          </Typography>
                        </Box>
                      }
                    />
                  </ListItem>
                ))}
              </List>
            </Box>
          </Card>
        </Grid>

        {/* 聊天区域 */}
        <Grid item xs={12} md={8} lg={9}>
          {selectedRoom ? (
            <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
              {/* 聊天头部 */}
              <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    <Badge
                      color={getOnlineStatusColor(selectedRoom.other_user.online_status)}
                      variant="dot"
                      invisible={selectedRoom.other_user.online_status === 'offline'}
                    >
                      <Avatar src={selectedRoom.other_user.avatar_url} />
                    </Badge>
                    <Box>
                      <Typography variant="h6">
                        {selectedRoom.other_user.full_name}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {selectedRoom.other_user.online_status === 'online'
                          ? '在线'
                          : selectedRoom.other_user.online_status === 'away'
                          ? '离开'
                          : `最后上线: ${formatTime(selectedRoom.other_user.last_seen)}`
                        }
                      </Typography>
                    </Box>
                  </Box>
                  <Box>
                    <IconButton>
                      <PhoneIcon />
                    </IconButton>
                    <IconButton>
                      <VideoCallIcon />
                    </IconButton>
                    <IconButton>
                      <InfoIcon />
                    </IconButton>
                    <IconButton>
                      <MoreVertIcon />
                    </IconButton>
                  </Box>
                </Box>
              </Box>

              {/* 消息区域 */}
              <Box sx={{ flex: 1, overflow: 'auto', p: 1 }}>
                {messages.map((msg) => (
                  <Box
                    key={msg.id}
                    sx={{
                      display: 'flex',
                      justifyContent: msg.sender_id === 999 ? 'flex-end' : 'flex-start',
                      mb: 1
                    }}
                  >
                    <Box
                      sx={{
                        maxWidth: '70%',
                        display: 'flex',
                        flexDirection: msg.sender_id === 999 ? 'row-reverse' : 'row',
                        alignItems: 'flex-end',
                        gap: 1
                      }}
                    >
                      {msg.sender_id !== 999 && (
                        <Avatar
                          src={selectedRoom.other_user.avatar_url}
                          sx={{ width: 32, height: 32 }}
                        />
                      )}
                      <Paper
                        sx={{
                          p: 1.5,
                          backgroundColor: msg.sender_id === 999 ? 'primary.main' : 'grey.100',
                          color: msg.sender_id === 999 ? 'white' : 'text.primary',
                          borderRadius: 2,
                          borderBottomRightRadius: msg.sender_id === 999 ? 4 : 16,
                          borderBottomLeftRadius: msg.sender_id === 999 ? 16 : 4,
                        }}
                      >
                        <Typography variant="body2">
                          {msg.content}
                        </Typography>
                        <Typography
                          variant="caption"
                          sx={{
                            display: 'block',
                            mt: 0.5,
                            opacity: 0.7,
                            fontSize: '0.75rem'
                          }}
                        >
                          {new Date(msg.created_at).toLocaleTimeString([], {
                            hour: '2-digit',
                            minute: '2-digit'
                          })}
                        </Typography>
                      </Paper>
                    </Box>
                  </Box>
                ))}
                <div ref={messagesEndRef} />
              </Box>

              {/* 输入区域 */}
              <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider' }}>
                <Box sx={{ display: 'flex', gap: 1, alignItems: 'flex-end' }}>
                  <IconButton>
                    <AttachFileIcon />
                  </IconButton>
                  <IconButton>
                    <EmojiIcon />
                  </IconButton>
                  <TextField
                    fullWidth
                    multiline
                    maxRows={4}
                    placeholder="输入消息..."
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    onKeyPress={(e) => {
                      if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        handleSendMessage();
                      }
                    }}
                    variant="outlined"
                    size="small"
                  />
                  <IconButton
                    color="primary"
                    onClick={handleSendMessage}
                    disabled={!message.trim()}
                  >
                    <SendIcon />
                  </IconButton>
                </Box>
              </Box>
            </Card>
          ) : (
            <Card sx={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="h6" color="text.secondary" gutterBottom>
                  选择一个对话开始聊天
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  或者
                </Typography>
                <Button
                  variant="contained"
                  startIcon={<AIIcon />}
                  onClick={() => setAiChatOpen(true)}
                  sx={{
                    mt: 2,
                    background: 'linear-gradient(45deg, #ff6b6b, #ffa500)',
                    '&:hover': {
                      background: 'linear-gradient(45deg, #ff5252, #ff9800)',
                    }
                  }}
                >
                  与AI助手聊天
                </Button>
              </Box>
            </Card>
          )}
        </Grid>
      </Grid>

      {/* AI聊天对话框 */}
      <Dialog
        open={aiChatOpen}
        onClose={() => setAiChatOpen(false)}
        maxWidth="md"
        fullWidth
        PaperProps={{
          sx: {
            height: '80vh',
            borderRadius: 3
          }
        }}
      >
        <DialogTitle sx={{ 
          background: 'linear-gradient(45deg, #ff6b6b, #ffa500)',
          color: 'white',
          display: 'flex',
          alignItems: 'center',
          gap: 1
        }}>
          <AIIcon />
          AI留学咨询助手
        </DialogTitle>
        <DialogContent sx={{ p: 0, height: '100%' }}>
          <AIConsultationChat />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAiChatOpen(false)}>关闭</Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default ChatPage;
