/*
OAuth认证配置
支持Google和GitHub第三方登录
*/

// OAuth配置
export const OAUTH_CONFIG = {
  google: {
    clientId: process.env.REACT_APP_GOOGLE_CLIENT_ID || 'your-google-client-id',
    redirectUri: `${window.location.origin}/auth/google/callback`,
    scope: 'openid email profile',
    authUrl: 'https://accounts.google.com/o/oauth2/v2/auth'
  },
  github: {
    clientId: process.env.REACT_APP_GITHUB_CLIENT_ID || 'your-github-client-id',
    redirectUri: `${window.location.origin}/auth/github/callback`,
    scope: 'user:email',
    authUrl: 'https://github.com/login/oauth/authorize'
  }
};

// 生成OAuth授权URL
export const generateOAuthUrl = (provider) => {
  const config = OAUTH_CONFIG[provider];
  if (!config) {
    throw new Error(`不支持的OAuth提供商: ${provider}`);
  }

  const params = new URLSearchParams({
    client_id: config.clientId,
    redirect_uri: config.redirectUri,
    scope: config.scope,
    response_type: 'code',
    state: generateRandomState()
  });

  return `${config.authUrl}?${params.toString()}`;
};

// 生成随机状态字符串（防CSRF）
const generateRandomState = () => {
  return Math.random().toString(36).substring(2, 15) +
    Math.random().toString(36).substring(2, 15);
};

// 启动OAuth认证流程
export const initiateOAuth = (provider) => {
  try {
    const authUrl = generateOAuthUrl(provider);
    // 保存state到sessionStorage（用于回调验证）
    const state = new URL(authUrl).searchParams.get('state');
    sessionStorage.setItem('oauth_state', state);
    sessionStorage.setItem('oauth_provider', provider);

    // 跳转到OAuth提供商的授权页面
    window.location.href = authUrl;
  } catch (error) {
    console.error(`启动${provider}登录失败:`, error);
    throw error;
  }
};

// 处理OAuth回调
export const handleOAuthCallback = async (provider, code, state) => {
  try {
    // 验证state参数
    const storedState = sessionStorage.getItem('oauth_state');
    if (state !== storedState) {
      throw new Error('无效的OAuth状态参数');
    }

    // 发送授权码到后端
    const response = await fetch('/api/v1/auth/oauth/callback', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        provider,
        code,
        state
      })
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'OAuth认证失败');
    }

    const data = await response.json();

    // 清理sessionStorage
    sessionStorage.removeItem('oauth_state');
    sessionStorage.removeItem('oauth_provider');

    return data;
  } catch (error) {
    console.error('OAuth回调处理失败:', error);
    throw error;
  }
};

// 检查OAuth支持状态
export const isOAuthEnabled = (provider) => {
  const config = OAUTH_CONFIG[provider];
  return config && config.clientId && config.clientId !== 'your-google-client-id' && config.clientId !== 'your-github-client-id';
};
