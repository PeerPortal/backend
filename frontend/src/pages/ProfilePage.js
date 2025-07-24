import { useState } from 'react';
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  Grid,
  Button,
  Avatar,
  Chip,
  Rating,
  TextField,
  Tab,
  Tabs,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from '@mui/material';
import {
  Edit as EditIcon,
  School as SchoolIcon,
  Language as LanguageIcon,
  Star as StarIcon,
  Verified as VerifiedIcon,
  LocationOn as LocationIcon,
  Email as EmailIcon,
  Phone as PhoneIcon,
  Link as LinkIcon,
  Upload as UploadIcon,
} from '@mui/icons-material';

const ProfilePage = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [editMode, setEditMode] = useState(false);
  const [verificationDialog, setVerificationDialog] = useState(false);
  const [profile, setProfile] = useState({
    id: 1,
    username: 'alice_cs',
    email: 'alice@example.com',
    phone: '+1-234-567-8900',
    full_name: 'Alice Wang',
    avatar_url: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Alice',
    cover_image_url: null,
    tagline: '斯坦福CS硕士，专业申请指导',
    introduction: '大家好！我是2023年毕业的斯坦福计算机科学硕士，在申请过程中积累了丰富经验。我可以帮助你制定申请策略、优化文书、准备面试等。专业、细致、负责是我的服务特色。',
    user_type: 'mentor',
    verification_status: 'university_verified',
    languages_spoken: ['中文', 'English'],
    timezone: 'America/Los_Angeles',

    // 教育背景
    education: [
      {
        id: 1,
        degree_type: 'master',
        school_name: '斯坦福大学',
        major: '计算机科学',
        graduation_year: 2023,
        gpa: 3.9,
        is_verified: true
      },
      {
        id: 2,
        degree_type: 'bachelor',
        school_name: '清华大学',
        major: '计算机科学与技术',
        graduation_year: 2021,
        gpa: 3.8,
        is_verified: true
      }
    ],

    // 服务能力
    services: [
      {
        id: 1,
        service_type: '申请咨询',
        proficiency_level: 5,
        experience_years: 2,
        hourly_rate: 200,
        description: '提供专业的申请策略制定和指导'
      },
      {
        id: 2,
        service_type: '文书写作',
        proficiency_level: 5,
        experience_years: 2,
        hourly_rate: 300,
        description: '帮助完善个人陈述和推荐信'
      }
    ],

    // 统计信息
    stats: {
      total_students_helped: 28,
      average_rating: 4.9,
      response_rate: '95%',
      response_time: '2小时内',
      completion_rate: '100%',
      total_reviews: 28,
      total_earnings: 8500.00
    },

    // 认证状态
    verifications: {
      identity_verified: true,
      university_verified: true,
      phone_verified: true,
      email_verified: true
    }
  });

  const [editForm, setEditForm] = useState({ ...profile });

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const handleEditSave = () => {
    setProfile({ ...editForm });
    setEditMode(false);
  };

  const handleEditCancel = () => {
    setEditForm({ ...profile });
    setEditMode(false);
  };

  const getVerificationBadges = () => {
    const badges = [];
    if (profile.verifications.identity_verified) badges.push('实名认证');
    if (profile.verifications.university_verified) badges.push('院校认证');
    if (profile.verifications.phone_verified) badges.push('手机认证');
    if (profile.verifications.email_verified) badges.push('邮箱认证');
    return badges;
  };

  // 评价数据
  const reviews = [
    {
      id: 1,
      user: {
        name: 'Tom Li',
        avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Tom'
      },
      rating: 5,
      content: 'Alice老师非常专业，帮我修改的文书最终成功拿到了Stanford的offer！推荐大家选择她的服务。',
      service: '文书写作',
      created_at: '2024-07-20T10:30:00Z'
    },
    {
      id: 2,
      user: {
        name: 'Lucy Zhang',
        avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Lucy'
      },
      rating: 5,
      content: '申请策略制定很详细，时间安排也很合理。Alice学姐人很好，会耐心解答所有问题。',
      service: '申请咨询',
      created_at: '2024-07-18T15:20:00Z'
    },
    {
      id: 3,
      user: {
        name: 'David Chen',
        avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=David'
      },
      rating: 4,
      content: '面试准备很充分，模拟面试帮助很大。最终成功通过了所有面试。',
      service: '面试辅导',
      created_at: '2024-07-15T09:45:00Z'
    }
  ];

  const ProfileInfo = () => (
    <Card>
      <CardContent>
        {/* 头像和基本信息 */}
        <Box sx={{ display: 'flex', alignItems: 'flex-start', mb: 3 }}>
          <Avatar
            src={profile.avatar_url}
            sx={{ width: 120, height: 120, mr: 3 }}
          />
          <Box sx={{ flex: 1 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
              <Typography variant="h4">{profile.full_name}</Typography>
              {profile.verifications.university_verified && (
                <VerifiedIcon color="primary" />
              )}
            </Box>
            <Typography variant="h6" color="text.secondary" gutterBottom>
              @{profile.username}
            </Typography>
            <Typography variant="body1" sx={{ mb: 2 }}>
              {profile.tagline}
            </Typography>

            {/* 认证徽章 */}
            <Box sx={{ mb: 2 }}>
              {getVerificationBadges().map((badge) => (
                <Chip
                  key={badge}
                  label={badge}
                  size="small"
                  color="primary"
                  sx={{ mr: 1, mb: 1 }}
                />
              ))}
            </Box>

            {/* 统计信息 */}
            <Box sx={{ display: 'flex', gap: 3, mb: 2 }}>
              <Box>
                <Typography variant="h6" color="primary">
                  {profile.stats.total_students_helped}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  帮助学生
                </Typography>
              </Box>
              <Box>
                <Typography variant="h6" color="primary">
                  {profile.stats.average_rating}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  平均评分
                </Typography>
              </Box>
              <Box>
                <Typography variant="h6" color="primary">
                  {profile.stats.completion_rate}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  完成率
                </Typography>
              </Box>
            </Box>

            <Button
              variant="outlined"
              startIcon={<EditIcon />}
              onClick={() => setEditMode(true)}
            >
              编辑资料
            </Button>
          </Box>
        </Box>

        {/* 详细介绍 */}
        <Typography variant="body1" paragraph>
          {profile.introduction}
        </Typography>

        {/* 联系信息 */}
        <Box sx={{ mt: 3 }}>
          <Typography variant="h6" gutterBottom>
            联系信息
          </Typography>
          <List dense>
            <ListItem>
              <ListItemIcon>
                <EmailIcon />
              </ListItemIcon>
              <ListItemText primary={profile.email} />
            </ListItem>
            <ListItem>
              <ListItemIcon>
                <PhoneIcon />
              </ListItemIcon>
              <ListItemText primary={profile.phone} />
            </ListItem>
            <ListItem>
              <ListItemIcon>
                <LocationIcon />
              </ListItemIcon>
              <ListItemText primary={profile.timezone} />
            </ListItem>
            <ListItem>
              <ListItemIcon>
                <LanguageIcon />
              </ListItemIcon>
              <ListItemText primary={profile.languages_spoken.join(', ')} />
            </ListItem>
          </List>
        </Box>
      </CardContent>
    </Card>
  );

  const EducationTab = () => (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          教育背景
        </Typography>
        {profile.education.map((edu) => (
          <Paper key={edu.id} sx={{ p: 2, mb: 2 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
              <Box>
                <Typography variant="h6">
                  {edu.school_name}
                </Typography>
                <Typography color="text.secondary">
                  {edu.major} · {edu.degree_type === 'master' ? '硕士' : edu.degree_type === 'phd' ? '博士' : '本科'}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  毕业年份: {edu.graduation_year} · GPA: {edu.gpa}
                </Typography>
              </Box>
              {edu.is_verified && (
                <Chip label="已认证" color="primary" size="small" />
              )}
            </Box>
          </Paper>
        ))}
        <Button
          variant="outlined"
          onClick={() => setVerificationDialog(true)}
          sx={{ mt: 2 }}
        >
          添加院校认证
        </Button>
      </CardContent>
    </Card>
  );

  const ServicesTab = () => (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          提供服务
        </Typography>
        {profile.services.map((service) => (
          <Paper key={service.id} sx={{ p: 2, mb: 2 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
              <Box sx={{ flex: 1 }}>
                <Typography variant="h6">
                  {service.service_type}
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                  {service.description}
                </Typography>
                <Rating
                  value={service.proficiency_level}
                  readOnly
                  size="small"
                />
                <Typography variant="body2" color="text.secondary">
                  经验: {service.experience_years}年
                </Typography>
              </Box>
              <Typography variant="h6" color="primary">
                ¥{service.hourly_rate}/时
              </Typography>
            </Box>
          </Paper>
        ))}
      </CardContent>
    </Card>
  );

  const ReviewsTab = () => (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          学生评价 ({profile.stats.total_reviews}条)
        </Typography>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
          <Rating value={profile.stats.average_rating} precision={0.1} readOnly />
          <Typography variant="h6" sx={{ ml: 1 }}>
            {profile.stats.average_rating}
          </Typography>
        </Box>

        {reviews.map((review) => (
          <Paper key={review.id} sx={{ p: 2, mb: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'flex-start', mb: 1 }}>
              <Avatar
                src={review.user.avatar}
                sx={{ width: 32, height: 32, mr: 2 }}
              />
              <Box sx={{ flex: 1 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Typography variant="subtitle2">
                    {review.user.name}
                  </Typography>
                  <Chip label={review.service} size="small" variant="outlined" />
                </Box>
                <Rating value={review.rating} size="small" readOnly />
                <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                  {review.content}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {new Date(review.created_at).toLocaleDateString()}
                </Typography>
              </Box>
            </Box>
          </Paper>
        ))}
      </CardContent>
    </Card>
  );

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Grid container spacing={3}>
        {/* 主要内容 */}
        <Grid item xs={12} md={8}>
          <Box sx={{ mb: 3 }}>
            <Tabs value={activeTab} onChange={handleTabChange}>
              <Tab label="个人信息" />
              <Tab label="教育背景" />
              <Tab label="服务项目" />
              <Tab label="学生评价" />
            </Tabs>
          </Box>

          {activeTab === 0 && <ProfileInfo />}
          {activeTab === 1 && <EducationTab />}
          {activeTab === 2 && <ServicesTab />}
          {activeTab === 3 && <ReviewsTab />}
        </Grid>

        {/* 侧边栏 */}
        <Grid item xs={12} md={4}>
          {/* 快速统计 */}
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                数据统计
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography>响应率</Typography>
                  <Typography color="primary" fontWeight={600}>
                    {profile.stats.response_rate}
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography>响应时间</Typography>
                  <Typography color="primary" fontWeight={600}>
                    {profile.stats.response_time}
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography>总收入</Typography>
                  <Typography color="primary" fontWeight={600}>
                    ¥{profile.stats.total_earnings.toLocaleString()}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>

          {/* 认证状态 */}
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                认证状态
              </Typography>
              <List dense>
                <ListItem>
                  <ListItemIcon>
                    <VerifiedIcon color={profile.verifications.identity_verified ? 'primary' : 'disabled'} />
                  </ListItemIcon>
                  <ListItemText
                    primary="实名认证"
                    secondary={profile.verifications.identity_verified ? '已认证' : '未认证'}
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <SchoolIcon color={profile.verifications.university_verified ? 'primary' : 'disabled'} />
                  </ListItemIcon>
                  <ListItemText
                    primary="院校认证"
                    secondary={profile.verifications.university_verified ? '已认证' : '未认证'}
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <PhoneIcon color={profile.verifications.phone_verified ? 'primary' : 'disabled'} />
                  </ListItemIcon>
                  <ListItemText
                    primary="手机认证"
                    secondary={profile.verifications.phone_verified ? '已认证' : '未认证'}
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <EmailIcon color={profile.verifications.email_verified ? 'primary' : 'disabled'} />
                  </ListItemIcon>
                  <ListItemText
                    primary="邮箱认证"
                    secondary={profile.verifications.email_verified ? '已认证' : '未认证'}
                  />
                </ListItem>
              </List>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* 编辑资料对话框 */}
      <Dialog open={editMode} onClose={handleEditCancel} maxWidth="md" fullWidth>
        <DialogTitle>编辑个人资料</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 1 }}>
            <TextField
              fullWidth
              label="姓名"
              value={editForm.full_name}
              onChange={(e) => setEditForm(prev => ({ ...prev, full_name: e.target.value }))}
              sx={{ mb: 2 }}
            />
            <TextField
              fullWidth
              label="一句话介绍"
              value={editForm.tagline}
              onChange={(e) => setEditForm(prev => ({ ...prev, tagline: e.target.value }))}
              sx={{ mb: 2 }}
            />
            <TextField
              fullWidth
              label="详细介绍"
              multiline
              rows={4}
              value={editForm.introduction}
              onChange={(e) => setEditForm(prev => ({ ...prev, introduction: e.target.value }))}
              sx={{ mb: 2 }}
            />
            <TextField
              fullWidth
              label="语言能力（用逗号分隔）"
              value={editForm.languages_spoken.join(', ')}
              onChange={(e) => setEditForm(prev => ({
                ...prev,
                languages_spoken: e.target.value.split(',').map(lang => lang.trim())
              }))}
              sx={{ mb: 2 }}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleEditCancel}>取消</Button>
          <Button onClick={handleEditSave} variant="contained">保存</Button>
        </DialogActions>
      </Dialog>

      {/* 院校认证对话框 */}
      <Dialog open={verificationDialog} onClose={() => setVerificationDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>院校认证</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 1 }}>
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>院校</InputLabel>
              <Select defaultValue="">
                <MenuItem value="stanford">斯坦福大学</MenuItem>
                <MenuItem value="harvard">哈佛大学</MenuItem>
                <MenuItem value="mit">麻省理工学院</MenuItem>
              </Select>
            </FormControl>
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>学历类型</InputLabel>
              <Select defaultValue="">
                <MenuItem value="bachelor">本科</MenuItem>
                <MenuItem value="master">硕士</MenuItem>
                <MenuItem value="phd">博士</MenuItem>
              </Select>
            </FormControl>
            <TextField
              fullWidth
              label="毕业年份"
              type="number"
              sx={{ mb: 2 }}
            />
            <TextField
              fullWidth
              label="学号"
              sx={{ mb: 2 }}
            />
            <Button
              variant="outlined"
              startIcon={<UploadIcon />}
              fullWidth
              sx={{ mb: 1 }}
            >
              上传录取通知书
            </Button>
            <Button
              variant="outlined"
              startIcon={<UploadIcon />}
              fullWidth
            >
              上传学生卡
            </Button>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setVerificationDialog(false)}>取消</Button>
          <Button variant="contained">提交认证</Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default ProfilePage;
