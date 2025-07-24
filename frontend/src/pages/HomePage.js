import React, { useState } from 'react';
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  Grid,
  Button,
  Chip,
  Avatar,
  Rating,
  TextField,
  InputAdornment,
  Paper,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import {
  Search as SearchIcon,
  Star as StarIcon,
  Verified as VerifiedIcon,
  Group as GroupIcon,
  Chat as ChatIcon,
  SmartToy as AIIcon,
} from '@mui/icons-material';

// 导入AI聊天组件
import AIConsultationChat from '../components/AIConsultationChat';

const HomePage = () => {
  const [aiChatOpen, setAiChatOpen] = useState(false);

  // 热门导师数据
  const featuredMentors = [
    {
      id: 1,
      username: 'alice_cs',
      full_name: 'Alice Wang',
      avatar_url: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Alice',
      university: '斯坦福大学',
      major: '计算机科学',
      degree: 'Master',
      rating: 4.9,
      review_count: 28,
      tagline: '斯坦福CS硕士，专业申请指导',
      verified: true,
      services: ['申请咨询', '文书写作'],
      hourly_rate: 200
    },
    {
      id: 2,
      username: 'bob_finance',
      full_name: 'Bob Chen',
      avatar_url: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Bob',
      university: '哈佛大学',
      major: '金融学',
      degree: 'MBA',
      rating: 4.8,
      review_count: 35,
      tagline: '哈佛商学院MBA，金融背景',
      verified: true,
      services: ['申请咨询', '面试辅导'],
      hourly_rate: 250
    },
    {
      id: 3,
      username: 'carol_ai',
      full_name: 'Carol Liu',
      avatar_url: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Carol',
      university: 'MIT',
      major: '人工智能',
      degree: 'PhD',
      rating: 5.0,
      review_count: 15,
      tagline: 'MIT AI博士，顶尖学术背景',
      verified: true,
      services: ['申请咨询', '文书写作', '背景提升'],
      hourly_rate: 300
    }
  ];

  // 热门帖子数据
  const featuredPosts = [
    {
      id: 1,
      title: '25Fall CS申请总结 - 从双非到Top 10',
      author: 'Tom Student',
      avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Tom',
      tags: ['CS', '申请经验', '双非逆袭'],
      likes: 156,
      comments: 23,
      time: '2小时前'
    },
    {
      id: 2,
      title: '商科申请文书写作技巧分享',
      author: 'Lucy Business',
      avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Lucy',
      tags: ['商科', '文书写作', '经验分享'],
      likes: 89,
      comments: 15,
      time: '5小时前'
    },
    {
      id: 3,
      title: 'CMU MSCS项目详细介绍',
      author: 'David CMU',
      avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=David',
      tags: ['CMU', 'CS', '项目介绍'],
      likes: 134,
      comments: 31,
      time: '1天前'
    }
  ];

  return (
    <Box>
      {/* Hero Section */}
      <Box
        sx={{
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: 'white',
          py: 8,
          position: 'relative',
          overflow: 'hidden'
        }}
      >
        <Container maxWidth="lg">
          <Grid container spacing={4} alignItems="center">
            <Grid item xs={12} md={6}>
              <Typography variant="h3" component="h1" gutterBottom fontWeight="bold">
                找到最适合的留学导师
              </Typography>
              <Typography variant="h6" sx={{ mb: 4, opacity: 0.9 }}>
                连接优秀学长学姐，获得个性化申请指导
              </Typography>

              {/* 搜索框 */}
              <Paper
                sx={{
                  p: 1,
                  display: 'flex',
                  alignItems: 'center',
                  borderRadius: 3,
                  mb: 3
                }}
              >
                <TextField
                  fullWidth
                  placeholder="搜索导师、院校或专业..."
                  variant="outlined"
                  size="medium"
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <SearchIcon />
                      </InputAdornment>
                    ),
                    sx: {
                      '& .MuiOutlinedInput-notchedOutline': { border: 'none' }
                    }
                  }}
                />
                <Button
                  variant="contained"
                  size="large"
                  sx={{ ml: 1, borderRadius: 2, px: 3 }}
                >
                  搜索
                </Button>
              </Paper>

              {/* 快速筛选标签 */}
              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                {['计算机科学', '商科', '工程', '社会科学', '艺术'].map((tag) => (
                  <Chip
                    key={tag}
                    label={tag}
                    variant="outlined"
                    sx={{
                      color: 'white',
                      borderColor: 'rgba(255,255,255,0.5)',
                      '&:hover': {
                        backgroundColor: 'rgba(255,255,255,0.1)'
                      }
                    }}
                  />
                ))}
              </Box>
            </Grid>

            <Grid item xs={12} md={6}>
              <Box sx={{ textAlign: 'center' }}>
                <img
                  src="https://images.unsplash.com/photo-1522202176988-66273c2fd55f?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80"
                  alt="Students studying"
                  style={{
                    maxWidth: '100%',
                    height: 'auto',
                    borderRadius: 16,
                    boxShadow: '0 20px 40px rgba(0,0,0,0.2)'
                  }}
                />
              </Box>
            </Grid>
          </Grid>
        </Container>
      </Box>

      {/* AI助手悬浮按钮 */}
      <IconButton
        onClick={() => setAiChatOpen(true)}
        sx={{
          position: 'fixed',
          bottom: 24,
          right: 24,
          background: 'linear-gradient(45deg, #ff6b6b, #ffa500)',
          color: 'white',
          width: 60,
          height: 60,
          zIndex: 1000,
          boxShadow: 3,
          '&:hover': {
            background: 'linear-gradient(45deg, #ff5252, #ff9800)',
            transform: 'scale(1.05)',
          },
          transition: 'all 0.3s ease'
        }}
      >
        <AIIcon fontSize="large" />
      </IconButton>

      <Container maxWidth="lg" sx={{ py: 6 }}>
        {/* 平台特色 */}
        <Box sx={{ mb: 8 }}>
          <Typography variant="h4" component="h2" textAlign="center" gutterBottom>
            为什么选择我们？
          </Typography>
          <Grid container spacing={4} sx={{ mt: 2 }}>
            <Grid item xs={12} md={4}>
              <Card sx={{ textAlign: 'center', p: 3, height: '100%' }}>
                <VerifiedIcon sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
                <Typography variant="h6" gutterBottom>
                  认证导师
                </Typography>
                <Typography color="text.secondary">
                  所有导师均经过院校认证，确保专业度和可信度
                </Typography>
              </Card>
            </Grid>
            <Grid item xs={12} md={4}>
              <Card sx={{ textAlign: 'center', p: 3, height: '100%' }}>
                <AIIcon sx={{ fontSize: 48, color: 'secondary.main', mb: 2 }} />
                <Typography variant="h6" gutterBottom>
                  AI智能助手
                </Typography>
                <Typography color="text.secondary">
                  24/7 AI咨询服务，即时解答申请疑问和背景评估
                </Typography>
              </Card>
            </Grid>
            <Grid item xs={12} md={4}>
              <Card sx={{ textAlign: 'center', p: 3, height: '100%' }}>
                <GroupIcon sx={{ fontSize: 48, color: 'success.main', mb: 2 }} />
                <Typography variant="h6" gutterBottom>
                  活跃社区
                </Typography>
                <Typography color="text.secondary">
                  分享经验，互相帮助，建立留学生社交网络
                </Typography>
              </Card>
            </Grid>
          </Grid>
        </Box>

        {/* 热门导师 */}
        <Box sx={{ mb: 8 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
            <Typography variant="h4" component="h2">
              热门导师
            </Typography>
            <Button variant="outlined" href="/mentors">
              查看更多
            </Button>
          </Box>

          <Grid container spacing={3}>
            {featuredMentors.map((mentor) => (
              <Grid item xs={12} md={4} key={mentor.id}>
                <Card sx={{ height: '100%', '&:hover': { transform: 'translateY(-4px)', transition: '0.3s' } }}>
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <Avatar
                        src={mentor.avatar_url}
                        sx={{ width: 56, height: 56, mr: 2 }}
                      />
                      <Box sx={{ flex: 1 }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Typography variant="h6">
                            {mentor.full_name}
                          </Typography>
                          {mentor.verified && (
                            <VerifiedIcon sx={{ color: 'primary.main', fontSize: 20 }} />
                          )}
                        </Box>
                        <Typography color="text.secondary" variant="body2">
                          {mentor.university} · {mentor.major}
                        </Typography>
                      </Box>
                    </Box>

                    <Typography variant="body2" sx={{ mb: 2 }}>
                      {mentor.tagline}
                    </Typography>

                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <Rating value={mentor.rating} precision={0.1} size="small" readOnly />
                      <Typography variant="body2" sx={{ ml: 1 }}>
                        {mentor.rating} ({mentor.review_count}条评价)
                      </Typography>
                    </Box>

                    <Box sx={{ mb: 2 }}>
                      {mentor.services.slice(0, 2).map((service) => (
                        <Chip
                          key={service}
                          label={service}
                          size="small"
                          sx={{ mr: 1, mb: 1 }}
                        />
                      ))}
                    </Box>

                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <Typography variant="h6" color="primary">
                        ¥{mentor.hourly_rate}/时
                      </Typography>
                      <Button variant="contained" size="small">
                        联系导师
                      </Button>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Box>

        {/* 热门帖子 */}
        <Box sx={{ mb: 8 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
            <Typography variant="h4" component="h2">
              社区热门
            </Typography>
            <Button variant="outlined" href="/posts">
              查看更多
            </Button>
          </Box>

          <Grid container spacing={3}>
            {featuredPosts.map((post) => (
              <Grid item xs={12} md={4} key={post.id}>
                <Card sx={{ height: '100%', '&:hover': { transform: 'translateY(-4px)', transition: '0.3s' } }}>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      {post.title}
                    </Typography>

                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <Avatar
                        src={post.avatar}
                        sx={{ width: 32, height: 32, mr: 1 }}
                      />
                      <Typography variant="body2" color="text.secondary">
                        {post.author} · {post.time}
                      </Typography>
                    </Box>

                    <Box sx={{ mb: 2 }}>
                      {post.tags.map((tag) => (
                        <Chip
                          key={tag}
                          label={tag}
                          size="small"
                          variant="outlined"
                          sx={{ mr: 1, mb: 1 }}
                        />
                      ))}
                    </Box>

                    <Box sx={{ display: 'flex', gap: 2, color: 'text.secondary' }}>
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <StarIcon fontSize="small" sx={{ mr: 0.5 }} />
                        {post.likes}
                      </Box>
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <ChatIcon fontSize="small" sx={{ mr: 0.5 }} />
                        {post.comments}
                      </Box>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Box>

        {/* 统计数据 */}
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <Grid container spacing={4}>
            <Grid item xs={6} md={3}>
              <Typography variant="h4" color="primary" fontWeight="bold">
                1000+
              </Typography>
              <Typography color="text.secondary">
                认证导师
              </Typography>
            </Grid>
            <Grid item xs={6} md={3}>
              <Typography variant="h4" color="primary" fontWeight="bold">
                5000+
              </Typography>
              <Typography color="text.secondary">
                成功案例
              </Typography>
            </Grid>
            <Grid item xs={6} md={3}>
              <Typography variant="h4" color="primary" fontWeight="bold">
                50+
              </Typography>
              <Typography color="text.secondary">
                合作院校
              </Typography>
            </Grid>
            <Grid item xs={6} md={3}>
              <Typography variant="h4" color="primary" fontWeight="bold">
                98%
              </Typography>
              <Typography color="text.secondary">
                满意度
              </Typography>
            </Grid>
          </Grid>
        </Paper>
      </Container>

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
    </Box>
  );
};

export default HomePage;
