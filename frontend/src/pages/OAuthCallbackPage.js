/*
OAuth回调处理页面
处理Google和GitHub登录回调
*/

import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import {
  Container,
  Paper,
  Typography,
  Box,
  CircularProgress,
  Alert,
} from '@mui/material';
import { handleOAuthCallback } from '../utils/oauth';

const OAuthCallbackPage = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [status, setStatus] = useState('processing'); // processing, success, error
  const [message, setMessage] = useState('正在处理登录...');

  useEffect(() => {
    const processCallback = async () => {
      try {
        const code = searchParams.get('code');
        const state = searchParams.get('state');
        const error = searchParams.get('error');
        const provider = sessionStorage.getItem('oauth_provider');

        // 检查是否有错误
        if (error) {
          throw new Error(`OAuth认证失败: ${error}`);
        }

        // 检查必要参数
        if (!code || !state || !provider) {
          throw new Error('缺少必要的OAuth参数');
        }

        setMessage(`正在处理${provider === 'google' ? 'Google' : 'GitHub'}登录...`);

        // 处理OAuth回调
        const result = await handleOAuthCallback(provider, code, state);

        if (result.access_token) {
          // 保存token
          localStorage.setItem('access_token', result.access_token);

          setStatus('success');
          setMessage('登录成功！正在跳转...');

          // 延迟跳转，让用户看到成功消息
          setTimeout(() => {
            navigate('/', { replace: true });
          }, 1500);
        } else {
          throw new Error('未收到访问令牌');
        }
      } catch (err) {
        console.error('OAuth回调处理失败:', err);
        setStatus('error');
        setMessage(err.message || 'OAuth认证失败');

        // 3秒后跳转到登录页
        setTimeout(() => {
          navigate('/login', {
            state: { error: err.message || 'OAuth认证失败' },
            replace: true
          });
        }, 3000);
      }
    };

    processCallback();
  }, [searchParams, navigate]);

  const getStatusColor = () => {
    switch (status) {
      case 'success': return 'success';
      case 'error': return 'error';
      default: return 'info';
    }
  };

  const getStatusIcon = () => {
    switch (status) {
      case 'processing': return <CircularProgress size={24} />;
      case 'success': return '✅';
      case 'error': return '❌';
      default: return null;
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
              mb: 3,
              fontWeight: 700,
              background: 'linear-gradient(45deg, #1976d2, #42a5f5)',
              backgroundClip: 'text',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
            }}
          >
            留学助手
          </Typography>

          {/* 状态消息 */}
          <Box sx={{ textAlign: 'center', mb: 3 }}>
            {getStatusIcon()}
            <Typography variant="h6" sx={{ mt: 2 }}>
              第三方登录
            </Typography>
          </Box>

          {/* 详细消息 */}
          <Alert
            severity={getStatusColor()}
            sx={{ width: '100%', textAlign: 'center' }}
          >
            {message}
          </Alert>

          {/* 提示信息 */}
          {status === 'error' && (
            <Typography
              variant="body2"
              color="text.secondary"
              sx={{ mt: 2, textAlign: 'center' }}
            >
              3秒后将自动跳转到登录页面...
            </Typography>
          )}
        </Paper>
      </Box>
    </Container>
  );
};

export default OAuthCallbackPage;
