import React, { useState } from 'react';
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  Grid,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Avatar,
  IconButton,
  Menu,
  MenuItem,
  Tab,
  Tabs,
  LinearProgress,
} from '@mui/material';
import {
  MonetizationOn as MoneyIcon,
  Group as GroupIcon,
  Star as StarIcon,
  MoreVert as MoreVertIcon,
  Visibility as ViewIcon,
  Chat as ChatIcon,
  CheckCircle as CheckIcon,
  Schedule as ScheduleIcon,
} from '@mui/icons-material';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line } from 'recharts';

const DashboardPage = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [menuAnchor, setMenuAnchor] = useState(null);
  const [selectedOrder, setSelectedOrder] = useState(null);

  // 模拟数据
  const stats = {
    overview: {
      total_orders: 15,
      active_orders: 3,
      completed_orders: 12,
      total_earnings: 8500.00,
      this_month_earnings: 2100.00,
      average_rating: 4.9,
      total_reviews: 28,
      response_rate: '95%'
    },
    monthly_earnings: [
      { month: '1月', earnings: 1200 },
      { month: '2月', earnings: 1800 },
      { month: '3月', earnings: 2200 },
      { month: '4月', earnings: 1900 },
      { month: '5月', earnings: 2400 },
      { month: '6月', earnings: 2100 },
      { month: '7月', earnings: 2600 }
    ],
    service_stats: [
      { service: '申请咨询', count: 8, earnings: 3200 },
      { service: '文书写作', count: 5, earnings: 4500 },
      { service: '面试辅导', count: 3, earnings: 800 }
    ]
  };

  const orders = [
    {
      id: 1,
      student: {
        name: 'Tom Li',
        avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Tom',
        university: '北京大学',
        major: '计算机科学'
      },
      service: '文书写作',
      status: 'active',
      amount: 1500,
      created_at: '2024-07-20T10:30:00Z',
      deadline: '2024-07-30T23:59:59Z',
      progress: 60
    },
    {
      id: 2,
      student: {
        name: 'Lucy Zhang',
        avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Lucy',
        university: '清华大学',
        major: '金融学'
      },
      service: '申请咨询',
      status: 'completed',
      amount: 800,
      created_at: '2024-07-18T15:20:00Z',
      completed_at: '2024-07-24T10:30:00Z',
      rating: 5
    },
    {
      id: 3,
      student: {
        name: 'David Chen',
        avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=David',
        university: '复旦大学',
        major: '经济学'
      },
      service: '面试辅导',
      status: 'pending',
      amount: 400,
      created_at: '2024-07-22T09:15:00Z',
      scheduled_at: '2024-07-25T14:00:00Z'
    }
  ];

  const recent_activities = [
    {
      type: 'order_completed',
      title: '文书写作服务已完成',
      description: '为Tom Li完成了PS写作',
      amount: 1500.00,
      created_at: '2024-07-24T10:30:00Z'
    },
    {
      type: 'new_order',
      title: '收到新订单',
      description: 'Lucy Zhang预订了申请咨询服务',
      amount: 800.00,
      created_at: '2024-07-23T15:20:00Z'
    },
    {
      type: 'review_received',
      title: '收到新评价',
      description: 'David Chen给了你5星评价',
      created_at: '2024-07-22T16:45:00Z'
    }
  ];

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'warning';
      case 'completed': return 'success';
      case 'pending': return 'info';
      case 'cancelled': return 'error';
      default: return 'default';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'active': return '进行中';
      case 'completed': return '已完成';
      case 'pending': return '待开始';
      case 'cancelled': return '已取消';
      default: return '未知';
    }
  };

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const OverviewTab = () => (
    <Grid container spacing={3}>
      {/* 统计卡片 */}
      <Grid item xs={12} sm={6} md={3}>
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <Box>
                <Typography color="text.secondary" gutterBottom>
                  总订单数
                </Typography>
                <Typography variant="h4">
                  {stats.overview.total_orders}
                </Typography>
              </Box>
              <GroupIcon sx={{ fontSize: 40, color: 'primary.main' }} />
            </Box>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} sm={6} md={3}>
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <Box>
                <Typography color="text.secondary" gutterBottom>
                  进行中订单
                </Typography>
                <Typography variant="h4">
                  {stats.overview.active_orders}
                </Typography>
              </Box>
              <ScheduleIcon sx={{ fontSize: 40, color: 'warning.main' }} />
            </Box>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} sm={6} md={3}>
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <Box>
                <Typography color="text.secondary" gutterBottom>
                  本月收入
                </Typography>
                <Typography variant="h4">
                  ¥{stats.overview.this_month_earnings.toLocaleString()}
                </Typography>
              </Box>
              <MoneyIcon sx={{ fontSize: 40, color: 'success.main' }} />
            </Box>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} sm={6} md={3}>
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <Box>
                <Typography color="text.secondary" gutterBottom>
                  平均评分
                </Typography>
                <Typography variant="h4">
                  {stats.overview.average_rating}
                </Typography>
              </Box>
              <StarIcon sx={{ fontSize: 40, color: 'warning.main' }} />
            </Box>
          </CardContent>
        </Card>
      </Grid>

      {/* 收入趋势图 */}
      <Grid item xs={12} md={8}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              月度收入趋势
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={stats.monthly_earnings}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="earnings" stroke="#1976d2" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </Grid>

      {/* 服务统计 */}
      <Grid item xs={12} md={4}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              服务类型统计
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={stats.service_stats}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="service" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="count" fill="#1976d2" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </Grid>

      {/* 最近活动 */}
      <Grid item xs={12}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              最近活动
            </Typography>
            {recent_activities.map((activity, index) => (
              <Box key={index} sx={{ display: 'flex', alignItems: 'center', mb: 2, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
                <Box sx={{ flex: 1 }}>
                  <Typography variant="subtitle2">
                    {activity.title}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {activity.description}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {new Date(activity.created_at).toLocaleString()}
                  </Typography>
                </Box>
                {activity.amount && (
                  <Typography variant="h6" color="success.main">
                    +¥{activity.amount.toLocaleString()}
                  </Typography>
                )}
              </Box>
            ))}
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );

  const OrdersTab = () => (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          订单管理
        </Typography>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>学生</TableCell>
                <TableCell>服务</TableCell>
                <TableCell>状态</TableCell>
                <TableCell>金额</TableCell>
                <TableCell>进度</TableCell>
                <TableCell>操作</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {orders.map((order) => (
                <TableRow key={order.id}>
                  <TableCell>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Avatar src={order.student.avatar} sx={{ width: 32, height: 32 }} />
                      <Box>
                        <Typography variant="subtitle2">
                          {order.student.name}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {order.student.university} · {order.student.major}
                        </Typography>
                      </Box>
                    </Box>
                  </TableCell>
                  <TableCell>{order.service}</TableCell>
                  <TableCell>
                    <Chip
                      label={getStatusText(order.status)}
                      color={getStatusColor(order.status)}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>¥{order.amount}</TableCell>
                  <TableCell>
                    {order.status === 'active' && (
                      <Box sx={{ width: '100%' }}>
                        <LinearProgress variant="determinate" value={order.progress} />
                        <Typography variant="caption">{order.progress}%</Typography>
                      </Box>
                    )}
                    {order.status === 'completed' && order.rating && (
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <StarIcon fontSize="small" color="warning" />
                        <Typography variant="body2">{order.rating}</Typography>
                      </Box>
                    )}
                    {order.status === 'pending' && (
                      <Typography variant="body2" color="text.secondary">
                        {order.scheduled_at ? new Date(order.scheduled_at).toLocaleString() : '待安排'}
                      </Typography>
                    )}
                  </TableCell>
                  <TableCell>
                    <IconButton
                      onClick={(e) => {
                        setMenuAnchor(e.currentTarget);
                        setSelectedOrder(order);
                      }}
                    >
                      <MoreVertIcon />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </CardContent>
    </Card>
  );

  const EarningsTab = () => (
    <Grid container spacing={3}>
      <Grid item xs={12} md={6}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              收入概览
            </Typography>
            <Box sx={{ mb: 2 }}>
              <Typography variant="h4" color="primary">
                ¥{stats.overview.total_earnings.toLocaleString()}
              </Typography>
              <Typography color="text.secondary">
                总收入
              </Typography>
            </Box>
            <Box sx={{ mb: 2 }}>
              <Typography variant="h5" color="success.main">
                ¥{stats.overview.this_month_earnings.toLocaleString()}
              </Typography>
              <Typography color="text.secondary">
                本月收入
              </Typography>
            </Box>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} md={6}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              服务收入分布
            </Typography>
            {stats.service_stats.map((service) => (
              <Box key={service.service} sx={{ mb: 2 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2">{service.service}</Typography>
                  <Typography variant="body2">¥{service.earnings}</Typography>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={(service.earnings / stats.overview.total_earnings) * 100}
                />
              </Box>
            ))}
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              收入详细记录
            </Typography>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>日期</TableCell>
                    <TableCell>学生</TableCell>
                    <TableCell>服务</TableCell>
                    <TableCell>金额</TableCell>
                    <TableCell>状态</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {orders.filter(o => o.status === 'completed').map((order) => (
                    <TableRow key={order.id}>
                      <TableCell>
                        {new Date(order.completed_at).toLocaleDateString()}
                      </TableCell>
                      <TableCell>{order.student.name}</TableCell>
                      <TableCell>{order.service}</TableCell>
                      <TableCell>¥{order.amount}</TableCell>
                      <TableCell>
                        <Chip label="已完成" color="success" size="small" />
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* 页面标题 */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          工作台
        </Typography>
        <Typography color="text.secondary">
          管理你的订单、收入和学生服务
        </Typography>
      </Box>

      {/* 标签页 */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={activeTab} onChange={handleTabChange}>
          <Tab label="概览" />
          <Tab label="订单管理" />
          <Tab label="收入统计" />
        </Tabs>
      </Box>

      {/* 内容区域 */}
      {activeTab === 0 && <OverviewTab />}
      {activeTab === 1 && <OrdersTab />}
      {activeTab === 2 && <EarningsTab />}

      {/* 订单操作菜单 */}
      <Menu
        anchorEl={menuAnchor}
        open={Boolean(menuAnchor)}
        onClose={() => setMenuAnchor(null)}
      >
        <MenuItem onClick={() => setMenuAnchor(null)}>
          <ViewIcon sx={{ mr: 1 }} />
          查看详情
        </MenuItem>
        <MenuItem onClick={() => setMenuAnchor(null)}>
          <ChatIcon sx={{ mr: 1 }} />
          联系学生
        </MenuItem>
        {selectedOrder?.status === 'pending' && (
          <MenuItem onClick={() => setMenuAnchor(null)}>
            <CheckIcon sx={{ mr: 1 }} />
            开始服务
          </MenuItem>
        )}
        {selectedOrder?.status === 'active' && (
          <MenuItem onClick={() => setMenuAnchor(null)}>
            <CheckIcon sx={{ mr: 1 }} />
            标记完成
          </MenuItem>
        )}
      </Menu>
    </Container>
  );
};

export default DashboardPage;
