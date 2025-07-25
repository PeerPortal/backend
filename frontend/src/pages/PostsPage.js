import { useState, useEffect } from 'react';
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
  Tab,
  Tabs,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Paper,
  Divider,
  Fab,
} from '@mui/material';
import {
  Add as AddIcon,
  Visibility as VisibilityIcon,
  Favorite as FavoriteIcon,
  FavoriteBorder as FavoriteBorderIcon,
  Comment as CommentIcon,
  Share as ShareIcon,
  TrendingUp as TrendingIcon,
  School as SchoolIcon,
  Person as PersonIcon,
} from '@mui/icons-material';

const PostsPage = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [posts, setPosts] = useState([]);
  const [newPostDialog, setNewPostDialog] = useState(false);
  const [newPost, setNewPost] = useState({
    title: '',
    content: '',
    post_type: 'help_request',
    tags: '',
    target_degree: '',
    target_region: '',
    services_offered: '',
    pricing_info: ''
  });

  // 模拟帖子数据
  const mockPosts = [
    {
      id: 1,
      user_id: 1,
      post_type: "mentor_offer",
      title: "斯坦福CS硕士，提供专业申请指导",
      content: "大家好！我是2023年毕业的斯坦福计算机科学硕士，在申请过程中积累了丰富经验。现在提供以下服务：\n\n• 申请策略制定\n• 文书写作指导\n• 简历优化\n• 面试准备\n\n我的背景：本科985，GPA 3.8，托福110，GRE 330。成功申请到斯坦福、CMU、伯克利等顶尖学校。\n\n服务特色：\n✅ 一对一个性化指导\n✅ 提供实际案例参考\n✅ 24小时内回复\n✅ 满意度保证",
      tags: ["CS", "斯坦福", "硕士申请", "文书指导"],
      target_degree: "master",
      target_region: "美国",
      target_university: "斯坦福大学",
      target_major: "计算机科学",
      services_offered: ["申请咨询", "文书写作", "简历修改"],
      pricing_info: {
        "申请咨询": "200/小时",
        "文书写作": "1500/篇",
        "简历修改": "300/次"
      },
      author: {
        id: 1,
        username: "alice_cs",
        full_name: "Alice Wang",
        avatar_url: "https://api.dicebear.com/7.x/avataaars/svg?seed=Alice",
        verified: true,
        rating: 4.9
      },
      view_count: 156,
      like_count: 23,
      comment_count: 8,
      created_at: "2024-07-20T10:30:00Z",
      is_featured: true,
      liked_by_user: false
    },
    {
      id: 2,
      user_id: 2,
      post_type: "help_request",
      title: "求助！25Fall CS硕士申请，求学长学姐指导",
      content: "大家好，我是985本科CS专业的大三学生，准备申请25Fall的CS硕士项目。\n\n我的背景：\n• 本科：某985大学计算机科学\n• GPA：3.6/4.0\n• 托福：还没考（预计目标105+）\n• GRE：还没考（预计目标320+）\n• 研究经历：一篇二作论文在投\n• 实习：字节跳动算法实习3个月\n\n申请目标：\n• 冲刺：CMU、Stanford、MIT\n• 匹配：UCSD、UIUC、UW\n• 保底：还没定\n\n希望得到帮助：\n1. 选校建议（特别是保底学校）\n2. 文书写作指导\n3. 背景提升建议\n4. 时间规划\n\n预算：2000-5000元，希望找到合适的学长学姐！",
      tags: ["25Fall", "CS硕士", "求指导", "985背景"],
      target_degree: "master",
      target_region: "美国",
      target_major: "计算机科学",
      author: {
        id: 2,
        username: "student_cs",
        full_name: "Tom Li",
        avatar_url: "https://api.dicebear.com/7.x/avataaars/svg?seed=Tom",
        verified: false,
        rating: null
      },
      view_count: 89,
      like_count: 12,
      comment_count: 15,
      created_at: "2024-07-22T14:20:00Z",
      is_featured: false,
      liked_by_user: true
    },
    {
      id: 3,
      post_type: "mentor_offer",
      title: "哈佛商学院MBA，商科申请全套指导",
      content: "Hi大家好！我是2022年毕业的哈佛商学院MBA，目前在摩根大通工作。\n\n我的服务包括：\n📋 申请策略规划\n📝 Essay写作指导\n🎯 面试模拟训练\n🏫 选校建议\n💼 简历优化\n\n成功案例：\n• 帮助15+学生拿到M7 offer\n• 平均提升GMAT成绩30分\n• 面试通过率95%\n\n特别擅长：\n- 金融/咨询背景申请者\n- 转专业申请指导\n- 工作经验包装\n\n现在开放预约，先到先得！",
      tags: ["MBA", "哈佛商学院", "商科申请", "面试辅导"],
      author: {
        id: 3,
        username: "harvard_mba",
        full_name: "Sarah Chen",
        avatar_url: "https://api.dicebear.com/7.x/avataaars/svg?seed=Sarah",
        verified: true,
        rating: 4.9
      },
      view_count: 234,
      like_count: 45,
      comment_count: 12,
      created_at: "2024-07-21T09:15:00Z",
      is_featured: true,
      liked_by_user: false
    }
  ];

  useEffect(() => {
    setPosts(mockPosts);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
    // 根据tab筛选帖子
    if (newValue === 0) {
      setPosts(mockPosts);
    } else if (newValue === 1) {
      setPosts(mockPosts.filter(p => p.post_type === 'mentor_offer'));
    } else if (newValue === 2) {
      setPosts(mockPosts.filter(p => p.post_type === 'help_request'));
    }
  };

  const handleLike = (postId) => {
    setPosts(prev => prev.map(post => {
      if (post.id === postId) {
        return {
          ...post,
          liked_by_user: !post.liked_by_user,
          like_count: post.liked_by_user ? post.like_count - 1 : post.like_count + 1
        };
      }
      return post;
    }));
  };

  const handleCreatePost = () => {
    // 模拟创建帖子
    const post = {
      id: Date.now(),
      ...newPost,
      tags: newPost.tags.split(',').map(tag => tag.trim()).filter(Boolean),
      author: {
        id: 999,
        username: "current_user",
        full_name: "当前用户",
        avatar_url: "https://api.dicebear.com/7.x/avataaars/svg?seed=User",
        verified: false
      },
      view_count: 0,
      like_count: 0,
      comment_count: 0,
      created_at: new Date().toISOString(),
      is_featured: false,
      liked_by_user: false
    };

    setPosts(prev => [post, ...prev]);
    setNewPostDialog(false);
    setNewPost({
      title: '',
      content: '',
      post_type: 'help_request',
      tags: '',
      target_degree: '',
      target_region: '',
      services_offered: '',
      pricing_info: ''
    });
  };

  const formatTime = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInHours = Math.floor((now - date) / (1000 * 60 * 60));

    if (diffInHours < 1) return '刚刚';
    if (diffInHours < 24) return `${diffInHours}小时前`;
    return `${Math.floor(diffInHours / 24)}天前`;
  };

  const PostCard = ({ post }) => (
    <Card sx={{ mb: 3, '&:hover': { boxShadow: 3 } }}>
      <CardContent>
        {/* 作者信息 */}
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Avatar
            src={post.author.avatar_url}
            sx={{ width: 48, height: 48, mr: 2 }}
          />
          <Box sx={{ flex: 1 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Typography variant="subtitle1" fontWeight={600}>
                {post.author.full_name}
              </Typography>
              {post.author.verified && (
                <Chip
                  label="已认证"
                  size="small"
                  color="primary"
                  sx={{ height: 20 }}
                />
              )}
              <Chip
                label={post.post_type === 'mentor_offer' ? '导师' : '求助'}
                size="small"
                color={post.post_type === 'mentor_offer' ? 'success' : 'info'}
                sx={{ height: 20 }}
              />
              {post.is_featured && (
                <Chip
                  label="精选"
                  size="small"
                  color="warning"
                  sx={{ height: 20 }}
                />
              )}
            </Box>
            <Typography variant="body2" color="text.secondary">
              @{post.author.username} · {formatTime(post.created_at)}
            </Typography>
          </Box>
          {post.author.rating && (
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
              <TrendingIcon fontSize="small" color="primary" />
              <Typography variant="body2" color="primary" fontWeight={600}>
                {post.author.rating}
              </Typography>
            </Box>
          )}
        </Box>

        {/* 帖子标题 */}
        <Typography variant="h6" component="h3" gutterBottom>
          {post.title}
        </Typography>

        {/* 帖子内容 */}
        <Typography
          variant="body2"
          color="text.secondary"
          sx={{
            mb: 2,
            display: '-webkit-box',
            WebkitLineClamp: 4,
            WebkitBoxOrient: 'vertical',
            overflow: 'hidden'
          }}
        >
          {post.content}
        </Typography>

        {/* 标签 */}
        <Box sx={{ mb: 2 }}>
          {post.tags?.map((tag) => (
            <Chip
              key={tag}
              label={tag}
              size="small"
              sx={{ mr: 1, mb: 1 }}
              variant="outlined"
              color="primary"
            />
          ))}
        </Box>

        {/* 服务价格信息（仅导师帖子显示） */}
        {post.post_type === 'mentor_offer' && post.pricing_info && (
          <Paper sx={{ p: 2, mb: 2, bgcolor: 'grey.50' }}>
            <Typography variant="subtitle2" gutterBottom color="primary">
              服务价格
            </Typography>
            <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
              {Object.entries(post.pricing_info).map(([service, price]) => (
                <Typography key={service} variant="body2">
                  <strong>{service}:</strong> {price}
                </Typography>
              ))}
            </Box>
          </Paper>
        )}

        <Divider sx={{ my: 2 }} />

        {/* 互动按钮 */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Box sx={{ display: 'flex', gap: 2 }}>
            <Button
              size="small"
              startIcon={post.liked_by_user ? <FavoriteIcon /> : <FavoriteBorderIcon />}
              color={post.liked_by_user ? "error" : "inherit"}
              onClick={() => handleLike(post.id)}
            >
              {post.like_count}
            </Button>
            <Button
              size="small"
              startIcon={<CommentIcon />}
              color="inherit"
            >
              {post.comment_count}
            </Button>
            <Button
              size="small"
              startIcon={<VisibilityIcon />}
              color="inherit"
            >
              {post.view_count}
            </Button>
            <Button
              size="small"
              startIcon={<ShareIcon />}
              color="inherit"
            >
              分享
            </Button>
          </Box>

          {post.post_type === 'mentor_offer' ? (
            <Button variant="contained" size="small">
              联系导师
            </Button>
          ) : (
            <Button variant="outlined" size="small">
              提供帮助
            </Button>
          )}
        </Box>
      </CardContent>
    </Card>
  );

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* 页面标题 */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          社区广场
        </Typography>
        <Typography color="text.secondary">
          分享申请经验，寻找申请伙伴，获得专业指导
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {/* 主要内容区 */}
        <Grid item xs={12} md={8}>
          {/* 标签页 */}
          <Paper sx={{ mb: 3 }}>
            <Tabs
              value={activeTab}
              onChange={handleTabChange}
              variant="fullWidth"
              sx={{ borderBottom: 1, borderColor: 'divider' }}
            >
              <Tab
                label="全部"
                icon={<PersonIcon />}
                iconPosition="start"
              />
              <Tab
                label="导师服务"
                icon={<SchoolIcon />}
                iconPosition="start"
              />
              <Tab
                label="求助帖"
                icon={<PersonIcon />}
                iconPosition="start"
              />
            </Tabs>
          </Paper>

          {/* 帖子列表 */}
          <Box>
            {posts.map((post) => (
              <PostCard key={post.id} post={post} />
            ))}
          </Box>
        </Grid>

        {/* 侧边栏 */}
        <Grid item xs={12} md={4}>
          {/* 发布按钮 */}
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                分享你的故事
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                分享申请经验，提供专业指导，或寻求帮助
              </Typography>
              <Button
                variant="contained"
                fullWidth
                startIcon={<AddIcon />}
                onClick={() => setNewPostDialog(true)}
              >
                发布帖子
              </Button>
            </CardContent>
          </Card>

          {/* 热门话题 */}
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                热门话题
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                {[
                  { tag: '25Fall申请', count: 156 },
                  { tag: 'CS硕士', count: 89 },
                  { tag: 'MBA申请', count: 67 },
                  { tag: '文书写作', count: 45 },
                  { tag: '面试经验', count: 38 }
                ].map((topic) => (
                  <Button
                    key={topic.tag}
                    variant="text"
                    size="small"
                    sx={{ justifyContent: 'space-between' }}
                  >
                    <span>#{topic.tag}</span>
                    <span>{topic.count}</span>
                  </Button>
                ))}
              </Box>
            </CardContent>
          </Card>

          {/* 推荐导师 */}
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                推荐导师
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                {mockPosts
                  .filter(p => p.post_type === 'mentor_offer')
                  .slice(0, 3)
                  .map((post) => (
                    <Box key={post.id} sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Avatar
                        src={post.author.avatar_url}
                        sx={{ width: 32, height: 32 }}
                      />
                      <Box sx={{ flex: 1 }}>
                        <Typography variant="body2" fontWeight={600}>
                          {post.author.full_name}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {post.title.substring(0, 20)}...
                        </Typography>
                      </Box>
                      <Button size="small" variant="outlined">
                        关注
                      </Button>
                    </Box>
                  ))}
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* 发布帖子对话框 */}
      <Dialog
        open={newPostDialog}
        onClose={() => setNewPostDialog(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>发布新帖子</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 1 }}>
            {/* 帖子类型 */}
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>帖子类型</InputLabel>
              <Select
                value={newPost.post_type}
                label="帖子类型"
                onChange={(e) => setNewPost(prev => ({ ...prev, post_type: e.target.value }))}
              >
                <MenuItem value="help_request">求助帖</MenuItem>
                <MenuItem value="mentor_offer">导师服务</MenuItem>
              </Select>
            </FormControl>

            {/* 标题 */}
            <TextField
              fullWidth
              label="标题"
              value={newPost.title}
              onChange={(e) => setNewPost(prev => ({ ...prev, title: e.target.value }))}
              sx={{ mb: 2 }}
            />

            {/* 内容 */}
            <TextField
              fullWidth
              label="内容"
              multiline
              rows={6}
              value={newPost.content}
              onChange={(e) => setNewPost(prev => ({ ...prev, content: e.target.value }))}
              sx={{ mb: 2 }}
            />

            {/* 标签 */}
            <TextField
              fullWidth
              label="标签（用逗号分隔）"
              value={newPost.tags}
              onChange={(e) => setNewPost(prev => ({ ...prev, tags: e.target.value }))}
              sx={{ mb: 2 }}
              placeholder="例如：CS,硕士申请,文书指导"
            />

            {/* 目标学历 */}
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>目标学历</InputLabel>
              <Select
                value={newPost.target_degree}
                label="目标学历"
                onChange={(e) => setNewPost(prev => ({ ...prev, target_degree: e.target.value }))}
              >
                <MenuItem value="">不限</MenuItem>
                <MenuItem value="bachelor">本科</MenuItem>
                <MenuItem value="master">硕士</MenuItem>
                <MenuItem value="phd">博士</MenuItem>
              </Select>
            </FormControl>

            {/* 目标地区 */}
            <TextField
              fullWidth
              label="目标地区"
              value={newPost.target_region}
              onChange={(e) => setNewPost(prev => ({ ...prev, target_region: e.target.value }))}
              sx={{ mb: 2 }}
              placeholder="例如：美国，英国，加拿大"
            />

            {/* 导师服务专用字段 */}
            {newPost.post_type === 'mentor_offer' && (
              <>
                <TextField
                  fullWidth
                  label="提供服务（用逗号分隔）"
                  value={newPost.services_offered}
                  onChange={(e) => setNewPost(prev => ({ ...prev, services_offered: e.target.value }))}
                  sx={{ mb: 2 }}
                  placeholder="例如：申请咨询,文书写作,面试辅导"
                />
                <TextField
                  fullWidth
                  label="价格信息"
                  value={newPost.pricing_info}
                  onChange={(e) => setNewPost(prev => ({ ...prev, pricing_info: e.target.value }))}
                  sx={{ mb: 2 }}
                  placeholder="例如：申请咨询 200元/小时，文书写作 1500元/篇"
                />
              </>
            )}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setNewPostDialog(false)}>
            取消
          </Button>
          <Button
            onClick={handleCreatePost}
            variant="contained"
            disabled={!newPost.title || !newPost.content}
          >
            发布
          </Button>
        </DialogActions>
      </Dialog>

      {/* 悬浮发布按钮 */}
      <Fab
        color="primary"
        sx={{ position: 'fixed', bottom: 16, right: 16 }}
        onClick={() => setNewPostDialog(true)}
      >
        <AddIcon />
      </Fab>
    </Container>
  );
};

export default PostsPage;
