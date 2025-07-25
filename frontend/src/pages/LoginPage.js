import React, { useState, useEffect } from 'react';
import {
  Container,
  Paper,
  TextField,
  Button,
  Typography,
  Box,
  Link,
  Alert,
  InputAdornment,
  IconButton,
  Divider,
  Chip,
} from '@mui/material';
import {
  Visibility,
  VisibilityOff,
  Email as EmailIcon,
  Lock as LockIcon,
  Google as GoogleIcon,
  GitHub as GitHubIcon,
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';
import { initiateOAuth, isOAuthEnabled } from '../utils/oauth';

const LoginPage = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');

  // 检查是否有注册成功的消息
  useEffect(() => {
    if (location.state?.message) {
      setSuccessMessage(location.state.message);
      if (location.state?.email) {
        setFormData(prev => ({ ...prev, email: location.state.email }));
      }
    }
  }, [location.state]);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      // 使用真实的后端API
      const response = await fetch('/api/v1/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
          username: formData.email,
          password: formData.password
        })
      });

      if (response.ok) {
        const data = await response.json();
        // 存储token
        localStorage.setItem('access_token', data.access_token);
        // 登录成功，跳转到主页
        navigate('/');
      } else {
        const errorData = await response.json();
        setError(errorData.detail || '登录失败，请检查用户名和密码');
      }
    } catch (err) {
      setError('网络错误，请重试');
    } finally {
      setLoading(false);
    }
  };

  const handleSocialLogin = async (provider) => {
    try {
      if (!isOAuthEnabled(provider)) {
        setError(`${provider === 'google' ? 'Google' : 'GitHub'}登录暂未配置，请使用邮箱密码登录`);
        return;
      }

      setError('');
      await initiateOAuth(provider);
    } catch (err) {
      setError(`${provider === 'google' ? 'Google' : 'GitHub'}登录失败: ${err.message}`);
    }
  };

  return (
    <Container component="main" maxWidth="sm">
      <Box
        sx={{
          minHeight: '100vh',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          py: 4,
        }}
      >
        <Paper
          elevation={3}
          sx={{
            p: 4,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            borderRadius: 3,
          }}
        >
          {/* Logo和标题 */}
          <Typography
            variant="h4"
            sx={{
              mb: 1,
              fontWeight: 700,
              background: 'linear-gradient(45deg, #1976d2, #42a5f5)',
              backgroundClip: 'text',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
            }}
          >
            留学助手
          </Typography>
          <Typography variant="h5" component="h1" gutterBottom>
            登录
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            欢迎回来！请登录您的账户
          </Typography>

          {/* 成功提示 */}
          {successMessage && (
            <Alert severity="success" sx={{ width: '100%', mb: 2 }}>
              {successMessage}
            </Alert>
          )}

          {/* 错误提示 */}
          {error && (
            <Alert severity="error" sx={{ width: '100%', mb: 2 }}>
              {error}
            </Alert>
          )}

          {/* 登录表单 */}
          <Box component="form" onSubmit={handleSubmit} sx={{ width: '100%' }}>
            <TextField
              margin="normal"
              required
              fullWidth
              id="email"
              label="邮箱地址"
              name="email"
              autoComplete="email"
              autoFocus
              value={formData.email}
              onChange={handleChange}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <EmailIcon color="action" />
                  </InputAdornment>
                ),
              }}
            />
            <TextField
              margin="normal"
              required
              fullWidth
              name="password"
              label="密码"
              type={showPassword ? 'text' : 'password'}
              id="password"
              autoComplete="current-password"
              value={formData.password}
              onChange={handleChange}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <LockIcon color="action" />
                  </InputAdornment>
                ),
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton
                      aria-label="toggle password visibility"
                      onClick={() => setShowPassword(!showPassword)}
                      edge="end"
                    >
                      {showPassword ? <VisibilityOff /> : <Visibility />}
                    </IconButton>
                  </InputAdornment>
                ),
              }}
            />

            <Button
              type="submit"
              fullWidth
              variant="contained"
              disabled={loading}
              sx={{ mt: 3, mb: 2, py: 1.5 }}
            >
              {loading ? '登录中...' : '登录'}
            </Button>

            {/* 找回密码 */}
            <Box sx={{ textAlign: 'center', mb: 2 }}>
              <Link href="#" variant="body2">
                忘记密码？
              </Link>
            </Box>

            {/* 分割线 */}
            <Divider sx={{ my: 2 }}>
              <Chip label="或者" size="small" />
            </Divider>

            {/* 第三方登录 */}
            <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
              <Button
                fullWidth
                variant="outlined"
                startIcon={<GoogleIcon />}
                onClick={() => handleSocialLogin('Google')}
              >
                Google
              </Button>
              <Button
                fullWidth
                variant="outlined"
                startIcon={<GitHubIcon />}
                onClick={() => handleSocialLogin('GitHub')}
              >
                GitHub
              </Button>
            </Box>

            {/* 注册链接 */}
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="body2">
                还没有账户？{' '}
                <Link
                  component="button"
                  variant="body2"
                  onClick={() => navigate('/register')}
                >
                  立即注册
                </Link>
              </Typography>
            </Box>
          </Box>

          {/* 测试账户提示 */}
          <Box sx={{ mt: 3, p: 2, bgcolor: 'info.light', borderRadius: 1, width: '100%' }}>
            <Typography variant="caption" color="info.dark">
              测试账户：alice@example.com / password123
            </Typography>
          </Box>
        </Paper>
      </Box>
    </Container>
  );
};

export default LoginPage;
