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
  Rating,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Slider,
  Paper,
  Pagination,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
} from '@mui/material';
import {
  FilterList as FilterIcon,
  Verified as VerifiedIcon,
  Star as StarIcon,
  Chat as ChatIcon,
  Bookmark as BookmarkIcon,
  LocationOn as LocationIcon,
  School as SchoolIcon,
  Clear as ClearIcon,
} from '@mui/icons-material';

const MentorSearchPage = () => {
  const [filters, setFilters] = useState({
    degree: '',
    region: '',
    university: '',
    major: '',
    serviceTypes: [],
    minRating: 0,
    maxPrice: 1000,
  });

  const [mentors, setMentors] = useState([]);
  const [loading, setLoading] = useState(false);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [filterDialogOpen, setFilterDialogOpen] = useState(false);
  const [selectedMentor, setSelectedMentor] = useState(null);

  // 筛选选项数据
  const filterOptions = {
    degrees: [
      { value: 'bachelor', label: '本科' },
      { value: 'master', label: '硕士' },
      { value: 'phd', label: '博士' },
    ],
    regions: [
      { value: 'us', label: '美国' },
      { value: 'uk', label: '英国' },
      { value: 'canada', label: '加拿大' },
      { value: 'australia', label: '澳大利亚' },
      { value: 'singapore', label: '新加坡' },
    ],
    serviceTypes: [
      '申请咨询', '文书写作', '文书润色', '简历修改',
      '面试辅导', '选校定位', '背景提升', '网申指导'
    ],
  };

  // 模拟导师数据
  const mockMentors = [
    {
      id: 1,
      username: 'alice_cs',
      full_name: 'Alice Wang',
      avatar_url: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Alice',
      university: '斯坦福大学',
      major: '计算机科学',
      degree: 'master',
      graduation_year: 2023,
      region: '美国',
      rating: 4.9,
      review_count: 28,
      services: ['申请咨询', '文书写作', '简历修改'],
      hourly_rate: 200,
      currency: 'CNY',
      tagline: '斯坦福CS硕士，专业申请指导',
      verified: true,
      response_rate: '95%',
      response_time: '2小时内',
      introduction: '大家好！我是2023年毕业的斯坦福计算机科学硕士，在申请过程中积累了丰富经验。我可以帮助你制定申请策略、优化文书、准备面试等。',
      achievements: ['斯坦福大学CS硕士', 'Google软件工程师', '发表2篇顶级会议论文'],
      languages: ['中文', 'English'],
    },
    {
      id: 2,
      username: 'bob_finance',
      full_name: 'Bob Chen',
      avatar_url: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Bob',
      university: '哈佛大学',
      major: '金融学',
      degree: 'master',
      graduation_year: 2022,
      region: '美国',
      rating: 4.8,
      review_count: 35,
      services: ['申请咨询', '面试辅导', '选校定位'],
      hourly_rate: 250,
      currency: 'CNY',
      tagline: '哈佛商学院MBA，金融背景',
      verified: true,
      response_rate: '90%',
      response_time: '1小时内',
      introduction: '哈佛商学院MBA毕业，目前在投行工作。专门帮助商科申请者，特别擅长面试辅导和申请策略制定。',
      achievements: ['哈佛商学院MBA', '摩根大通投资银行', 'CFA持证人'],
      languages: ['中文', 'English'],
    },
    {
      id: 3,
      username: 'carol_ai',
      full_name: 'Carol Liu',
      avatar_url: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Carol',
      university: 'MIT',
      major: '人工智能',
      degree: 'phd',
      graduation_year: 2024,
      region: '美国',
      rating: 5.0,
      review_count: 15,
      services: ['申请咨询', '文书写作', '背景提升'],
      hourly_rate: 300,
      currency: 'CNY',
      tagline: 'MIT AI博士，顶尖学术背景',
      verified: true,
      response_rate: '98%',
      response_time: '30分钟内',
      introduction: 'MIT人工智能博士在读，研究方向为机器学习和深度学习。可以帮助理工科背景的同学申请顶尖项目。',
      achievements: ['MIT AI博士', '发表15篇顶级论文', 'Google Research实习'],
      languages: ['中文', 'English'],
    },
  ];

  useEffect(() => {
    searchMentors();
  }, [filters, page]);

  const searchMentors = async () => {
    setLoading(true);
    // 模拟API调用
    setTimeout(() => {
      let filteredMentors = [...mockMentors];

      // 应用筛选条件
      if (filters.degree) {
        filteredMentors = filteredMentors.filter(m => m.degree === filters.degree);
      }
      if (filters.minRating) {
        filteredMentors = filteredMentors.filter(m => m.rating >= filters.minRating);
      }
      if (filters.maxPrice) {
        filteredMentors = filteredMentors.filter(m => m.hourly_rate <= filters.maxPrice);
      }
      if (filters.serviceTypes.length > 0) {
        filteredMentors = filteredMentors.filter(m =>
          filters.serviceTypes.some(service => m.services.includes(service))
        );
      }

      setMentors(filteredMentors);
      setTotalPages(Math.ceil(filteredMentors.length / 10));
      setLoading(false);
    }, 500);
  };

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({
      ...prev,
      [key]: value
    }));
    setPage(1);
  };

  const clearFilters = () => {
    setFilters({
      degree: '',
      region: '',
      university: '',
      major: '',
      serviceTypes: [],
      minRating: 0,
      maxPrice: 1000,
    });
  };

  const handleServiceTypeToggle = (service) => {
    setFilters(prev => ({
      ...prev,
      serviceTypes: prev.serviceTypes.includes(service)
        ? prev.serviceTypes.filter(s => s !== service)
        : [...prev.serviceTypes, service]
    }));
  };

  const MentorCard = ({ mentor }) => (
    <Card
      sx={{
        height: '100%',
        '&:hover': {
          transform: 'translateY(-4px)',
          transition: '0.3s',
          boxShadow: 4
        },
        cursor: 'pointer'
      }}
      onClick={() => setSelectedMentor(mentor)}
    >
      <CardContent>
        {/* 头部信息 */}
        <Box sx={{ display: 'flex', alignItems: 'flex-start', mb: 2 }}>
          <Avatar
            src={mentor.avatar_url}
            sx={{ width: 64, height: 64, mr: 2 }}
          />
          <Box sx={{ flex: 1 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
              <Typography variant="h6">
                {mentor.full_name}
              </Typography>
              {mentor.verified && (
                <VerifiedIcon sx={{ color: 'primary.main', fontSize: 20 }} />
              )}
            </Box>
            <Typography color="text.secondary" variant="body2" sx={{ mb: 1 }}>
              <SchoolIcon fontSize="small" sx={{ mr: 0.5, verticalAlign: 'middle' }} />
              {mentor.university} · {mentor.major}
            </Typography>
            <Typography color="text.secondary" variant="body2">
              <LocationIcon fontSize="small" sx={{ mr: 0.5, verticalAlign: 'middle' }} />
              {mentor.region} · {mentor.degree === 'master' ? '硕士' : mentor.degree === 'phd' ? '博士' : '本科'}
            </Typography>
          </Box>
          <IconButton size="small">
            <BookmarkIcon />
          </IconButton>
        </Box>

        {/* 标语 */}
        <Typography variant="body2" sx={{ mb: 2, height: '2.4em', overflow: 'hidden' }}>
          {mentor.tagline}
        </Typography>

        {/* 评分 */}
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Rating value={mentor.rating} precision={0.1} size="small" readOnly />
          <Typography variant="body2" sx={{ ml: 1 }}>
            {mentor.rating} ({mentor.review_count}条评价)
          </Typography>
        </Box>

        {/* 服务标签 */}
        <Box sx={{ mb: 2 }}>
          {mentor.services.slice(0, 3).map((service) => (
            <Chip
              key={service}
              label={service}
              size="small"
              sx={{ mr: 1, mb: 1 }}
              color="primary"
              variant="outlined"
            />
          ))}
          {mentor.services.length > 3 && (
            <Chip
              label={`+${mentor.services.length - 3}`}
              size="small"
              variant="outlined"
            />
          )}
        </Box>

        {/* 响应信息 */}
        <Box sx={{ display: 'flex', gap: 1, mb: 2, fontSize: '0.875rem', color: 'text.secondary' }}>
          <span>响应率: {mentor.response_rate}</span>
          <span>·</span>
          <span>响应时间: {mentor.response_time}</span>
        </Box>

        {/* 底部操作 */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h6" color="primary" fontWeight="bold">
            ¥{mentor.hourly_rate}/时
          </Typography>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Button
              variant="outlined"
              size="small"
              startIcon={<ChatIcon />}
              onClick={(e) => {
                e.stopPropagation();
                // 处理聊天
              }}
            >
              咨询
            </Button>
            <Button
              variant="contained"
              size="small"
              onClick={(e) => {
                e.stopPropagation();
                // 处理预订
              }}
            >
              预订
            </Button>
          </Box>
        </Box>
      </CardContent>
    </Card>
  );

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* 页面标题 */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          找导师
        </Typography>
        <Typography color="text.secondary">
          找到最适合你的留学申请导师
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {/* 筛选侧边栏 */}
        <Grid item xs={12} md={3}>
          <Paper sx={{ p: 3, position: 'sticky', top: 100 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
              <Typography variant="h6">筛选条件</Typography>
              <Button size="small" onClick={clearFilters} startIcon={<ClearIcon />}>
                清空
              </Button>
            </Box>

            {/* 学历筛选 */}
            <FormControl fullWidth sx={{ mb: 3 }}>
              <InputLabel>学历层次</InputLabel>
              <Select
                value={filters.degree}
                label="学历层次"
                onChange={(e) => handleFilterChange('degree', e.target.value)}
              >
                <MenuItem value="">全部</MenuItem>
                {filterOptions.degrees.map((degree) => (
                  <MenuItem key={degree.value} value={degree.value}>
                    {degree.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            {/* 地区筛选 */}
            <FormControl fullWidth sx={{ mb: 3 }}>
              <InputLabel>目标地区</InputLabel>
              <Select
                value={filters.region}
                label="目标地区"
                onChange={(e) => handleFilterChange('region', e.target.value)}
              >
                <MenuItem value="">全部</MenuItem>
                {filterOptions.regions.map((region) => (
                  <MenuItem key={region.value} value={region.value}>
                    {region.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            {/* 服务类型 */}
            <Box sx={{ mb: 3 }}>
              <Typography variant="subtitle1" gutterBottom>
                服务类型
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                {filterOptions.serviceTypes.map((service) => (
                  <Chip
                    key={service}
                    label={service}
                    size="small"
                    color={filters.serviceTypes.includes(service) ? 'primary' : 'default'}
                    onClick={() => handleServiceTypeToggle(service)}
                    variant={filters.serviceTypes.includes(service) ? 'filled' : 'outlined'}
                  />
                ))}
              </Box>
            </Box>

            {/* 评分筛选 */}
            <Box sx={{ mb: 3 }}>
              <Typography variant="subtitle1" gutterBottom>
                最低评分: {filters.minRating}
              </Typography>
              <Slider
                value={filters.minRating}
                onChange={(e, value) => handleFilterChange('minRating', value)}
                min={0}
                max={5}
                step={0.5}
                marks
                valueLabelDisplay="auto"
              />
            </Box>

            {/* 价格筛选 */}
            <Box sx={{ mb: 3 }}>
              <Typography variant="subtitle1" gutterBottom>
                最高价格: ¥{filters.maxPrice}/时
              </Typography>
              <Slider
                value={filters.maxPrice}
                onChange={(e, value) => handleFilterChange('maxPrice', value)}
                min={50}
                max={1000}
                step={50}
                valueLabelDisplay="auto"
              />
            </Box>
          </Paper>
        </Grid>

        {/* 导师列表 */}
        <Grid item xs={12} md={9}>
          {/* 结果统计和排序 */}
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
            <Typography>
              找到 {mentors.length} 位导师
            </Typography>
            <FormControl sx={{ minWidth: 120 }}>
              <InputLabel size="small">排序方式</InputLabel>
              <Select size="small" defaultValue="rating" label="排序方式">
                <MenuItem value="rating">评分最高</MenuItem>
                <MenuItem value="price_low">价格最低</MenuItem>
                <MenuItem value="price_high">价格最高</MenuItem>
                <MenuItem value="reviews">评价最多</MenuItem>
              </Select>
            </FormControl>
          </Box>

          {/* 导师卡片网格 */}
          {loading ? (
            <Box sx={{ textAlign: 'center', py: 8 }}>
              <Typography>加载中...</Typography>
            </Box>
          ) : (
            <>
              <Grid container spacing={3}>
                {mentors.map((mentor) => (
                  <Grid item xs={12} sm={6} lg={4} key={mentor.id}>
                    <MentorCard mentor={mentor} />
                  </Grid>
                ))}
              </Grid>

              {/* 分页 */}
              {totalPages > 1 && (
                <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
                  <Pagination
                    count={totalPages}
                    page={page}
                    onChange={(e, value) => setPage(value)}
                    color="primary"
                  />
                </Box>
              )}
            </>
          )}
        </Grid>
      </Grid>

      {/* 导师详情对话框 */}
      <Dialog
        open={Boolean(selectedMentor)}
        onClose={() => setSelectedMentor(null)}
        maxWidth="md"
        fullWidth
      >
        {selectedMentor && (
          <>
            <DialogTitle>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Avatar
                  src={selectedMentor.avatar_url}
                  sx={{ width: 64, height: 64 }}
                />
                <Box>
                  <Typography variant="h5">
                    {selectedMentor.full_name}
                  </Typography>
                  <Typography color="text.secondary">
                    {selectedMentor.university} · {selectedMentor.major}
                  </Typography>
                </Box>
              </Box>
            </DialogTitle>
            <DialogContent>
              <Box sx={{ mb: 3 }}>
                <Typography variant="h6" gutterBottom>
                  个人介绍
                </Typography>
                <Typography paragraph>
                  {selectedMentor.introduction}
                </Typography>
              </Box>

              <Box sx={{ mb: 3 }}>
                <Typography variant="h6" gutterBottom>
                  主要成就
                </Typography>
                {selectedMentor.achievements.map((achievement, index) => (
                  <Chip
                    key={index}
                    label={achievement}
                    sx={{ mr: 1, mb: 1 }}
                    color="primary"
                    variant="outlined"
                  />
                ))}
              </Box>

              <Box sx={{ mb: 3 }}>
                <Typography variant="h6" gutterBottom>
                  提供服务
                </Typography>
                {selectedMentor.services.map((service) => (
                  <Chip
                    key={service}
                    label={service}
                    sx={{ mr: 1, mb: 1 }}
                    color="secondary"
                  />
                ))}
              </Box>

              <Box sx={{ mb: 3 }}>
                <Typography variant="h6" gutterBottom>
                  语言能力
                </Typography>
                {selectedMentor.languages.map((language) => (
                  <Chip
                    key={language}
                    label={language}
                    sx={{ mr: 1, mb: 1 }}
                    variant="outlined"
                  />
                ))}
              </Box>
            </DialogContent>
            <DialogActions>
              <Button onClick={() => setSelectedMentor(null)}>
                关闭
              </Button>
              <Button variant="outlined" startIcon={<ChatIcon />}>
                发消息
              </Button>
              <Button variant="contained">
                立即预订
              </Button>
            </DialogActions>
          </>
        )}
      </Dialog>
    </Container>
  );
};

export default MentorSearchPage;
