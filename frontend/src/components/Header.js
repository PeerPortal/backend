import React, { useState } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  IconButton,
  Menu,
  MenuItem,
  Avatar,
  Badge,
  Box,
  TextField,
  InputAdornment,
  Chip,
} from '@mui/material';
import {
  Search as SearchIcon,
  Notifications as NotificationsIcon,
  Chat as ChatIcon,
  AccountCircle,
  Dashboard as DashboardIcon,
  Settings as SettingsIcon,
  Logout as LogoutIcon,
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';

const Header = () => {
  const [anchorEl, setAnchorEl] = useState(null);
  const [notificationAnchor, setNotificationAnchor] = useState(null);
  const navigate = useNavigate();
  const location = useLocation();

  // 模拟用户登录状态
  const [isLoggedIn, setIsLoggedIn] = useState(true);
  const [user, setUser] = useState({
    username: 'alice_cs',
    full_name: 'Alice Wang',
    avatar_url: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Alice',
    is_mentor: true
  });

  const handleProfileMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleProfileMenuClose = () => {
    setAnchorEl(null);
  };

  const handleNotificationOpen = (event) => {
    setNotificationAnchor(event.currentTarget);
  };

  const handleNotificationClose = () => {
    setNotificationAnchor(null);
  };

  const handleLogout = () => {
    setIsLoggedIn(false);
    setUser(null);
    handleProfileMenuClose();
    navigate('/');
  };

  const menuItems = [
    { text: '首页', path: '/', active: location.pathname === '/' },
    { text: '找导师', path: '/mentors', active: location.pathname === '/mentors' },
    { text: '社区', path: '/posts', active: location.pathname === '/posts' },
  ];

  return (
    <AppBar position="sticky" sx={{ backgroundColor: 'white', color: 'text.primary', boxShadow: 1 }}>
      <Toolbar sx={{ justifyContent: 'space-between', px: { xs: 2, md: 4 } }}>
        {/* Logo和导航 */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 4 }}>
          <Typography
            variant="h6"
            sx={{
              fontWeight: 700,
              background: 'linear-gradient(45deg, #1976d2, #42a5f5)',
              backgroundClip: 'text',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              cursor: 'pointer'
            }}
            onClick={() => navigate('/')}
          >
            留学助手
          </Typography>
          
          <Box sx={{ display: { xs: 'none', md: 'flex' }, gap: 2 }}>
            {menuItems.map((item) => (
              <Button
                key={item.path}
                onClick={() => navigate(item.path)}
                sx={{
                  color: item.active ? 'primary.main' : 'text.primary',
                  fontWeight: item.active ? 600 : 400,
                  borderBottom: item.active ? '2px solid' : 'none',
                  borderRadius: 0,
                  '&:hover': {
                    backgroundColor: 'rgba(25, 118, 210, 0.04)',
                  }
                }}
              >
                {item.text}
              </Button>
            ))}
          </Box>
        </Box>

        {/* 搜索框 */}
        <Box sx={{ flex: 1, maxWidth: 400, mx: 2, display: { xs: 'none', sm: 'block' } }}>
          <TextField
            fullWidth
            size="small"
            placeholder="搜索导师、院校、专业..."
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon color="action" />
                </InputAdornment>
              ),
              sx: {
                borderRadius: 3,
                backgroundColor: '#f5f5f5',
                '& .MuiOutlinedInput-notchedOutline': {
                  border: 'none',
                },
                '&:hover .MuiOutlinedInput-notchedOutline': {
                  border: '1px solid #e0e0e0',
                },
                '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
                  border: '2px solid #1976d2',
                },
              }
            }}
          />
        </Box>

        {/* 右侧功能区 */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          {isLoggedIn ? (
            <>
              {/* AI助手标识 */}
              <Chip
                label="AI助手"
                size="small"
                sx={{
                  background: 'linear-gradient(45deg, #ff6b6b, #ffa500)',
                  color: 'white',
                  fontWeight: 600,
                  '&:hover': {
                    background: 'linear-gradient(45deg, #ff5252, #ff9800)',
                  }
                }}
                onClick={() => navigate('/ai-chat')}
              />

              {/* 消息 */}
              <IconButton onClick={() => navigate('/chat')}>
                <Badge badgeContent={3} color="error">
                  <ChatIcon />
                </Badge>
              </IconButton>

              {/* 通知 */}
              <IconButton onClick={handleNotificationOpen}>
                <Badge badgeContent={5} color="error">
                  <NotificationsIcon />
                </Badge>
              </IconButton>

              {/* 用户头像菜单 */}
              <IconButton onClick={handleProfileMenuOpen} sx={{ ml: 1 }}>
                <Avatar
                  src={user.avatar_url}
                  alt={user.full_name}
                  sx={{ width: 32, height: 32 }}
                />
              </IconButton>

              {/* 用户菜单 */}
              <Menu
                anchorEl={anchorEl}
                open={Boolean(anchorEl)}
                onClose={handleProfileMenuClose}
                sx={{ mt: 1 }}
              >
                <MenuItem onClick={() => { navigate('/profile'); handleProfileMenuClose(); }}>
                  <AccountCircle sx={{ mr: 2 }} />
                  个人资料
                </MenuItem>
                {user.is_mentor && (
                  <MenuItem onClick={() => { navigate('/dashboard'); handleProfileMenuClose(); }}>
                    <DashboardIcon sx={{ mr: 2 }} />
                    工作台
                  </MenuItem>
                )}
                <MenuItem onClick={handleProfileMenuClose}>
                  <SettingsIcon sx={{ mr: 2 }} />
                  设置
                </MenuItem>
                <MenuItem onClick={handleLogout}>
                  <LogoutIcon sx={{ mr: 2 }} />
                  退出登录
                </MenuItem>
              </Menu>

              {/* 通知菜单 */}
              <Menu
                anchorEl={notificationAnchor}
                open={Boolean(notificationAnchor)}
                onClose={handleNotificationClose}
                sx={{ mt: 1 }}
              >
                <MenuItem onClick={handleNotificationClose}>
                  <Box>
                    <Typography variant="subtitle2">新订单</Typography>
                    <Typography variant="body2" color="text.secondary">
                      Tom Li 预订了文书写作服务
                    </Typography>
                  </Box>
                </MenuItem>
                <MenuItem onClick={handleNotificationClose}>
                  <Box>
                    <Typography variant="subtitle2">新消息</Typography>
                    <Typography variant="body2" color="text.secondary">
                      Lucy Zhang 发来了消息
                    </Typography>
                  </Box>
                </MenuItem>
                <MenuItem onClick={handleNotificationClose}>
                  <Box>
                    <Typography variant="subtitle2">系统通知</Typography>
                    <Typography variant="body2" color="text.secondary">
                      您的院校认证已通过审核
                    </Typography>
                  </Box>
                </MenuItem>
              </Menu>
            </>
          ) : (
            <Box sx={{ display: 'flex', gap: 1 }}>
              <Button onClick={() => navigate('/login')}>
                登录
              </Button>
              <Button variant="contained" onClick={() => navigate('/register')}>
                注册
              </Button>
            </Box>
          )}
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Header;
