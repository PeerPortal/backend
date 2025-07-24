import React, { useState } from 'react';
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
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormControlLabel,
  Checkbox,
  Stepper,
  Step,
  StepLabel,
} from '@mui/material';
import {
  Visibility,
  VisibilityOff,
  Email as EmailIcon,
  Lock as LockIcon,
  Person as PersonIcon,
  School as SchoolIcon,
  Google as GoogleIcon,
  GitHub as GitHubIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

const RegisterPage = () => {
  const navigate = useNavigate();
  const [activeStep, setActiveStep] = useState(0);
  const [formData, setFormData] = useState({
    // 基本信息
    email: '',
    password: '',
    confirmPassword: '',
    fullName: '',
    userType: 'student', // student | mentor
    
    // 详细信息
    university: '',
    major: '',
    graduationYear: '',
    degree: '',
    introduction: '',
    
    // 协议同意
    agreeTerms: false,
    agreePrivacy: false,
  });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const steps = ['基本信息', '详细资料', '完成注册'];

  const handleChange = (e) => {
    const { name, value, checked, type } = e.target;
    setFormData({
      ...formData,
      [name]: type === 'checkbox' ? checked : value,
    });
  };

  const handleNext = () => {
    if (validateStep(activeStep)) {
      setActiveStep((prevStep) => prevStep + 1);
    }
  };

  const handleBack = () => {
    setActiveStep((prevStep) => prevStep - 1);
  };

  const validateStep = (step) => {
    setError('');
    
    if (step === 0) {
      if (!formData.email || !formData.password || !formData.fullName) {
        setError('请填写所有必填字段');
        return false;
      }
      if (formData.password !== formData.confirmPassword) {
        setError('两次输入的密码不一致');
        return false;
      }
      if (formData.password.length < 6) {
        setError('密码至少需要6位字符');
        return false;
      }
    }
    
    if (step === 1) {
      if (formData.userType === 'mentor' && (!formData.university || !formData.major)) {
        setError('导师账户需要填写院校和专业信息');
        return false;
      }
    }
    
    if (step === 2) {
      if (!formData.agreeTerms || !formData.agreePrivacy) {
        setError('请同意服务条款和隐私政策');
        return false;
      }
    }
    
    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validateStep(2)) return;
    
    setLoading(true);
    setError('');

    try {
      // 模拟注册API调用
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // 注册成功，跳转到登录页面
      navigate('/login', { 
        state: { 
          message: '注册成功！请登录您的账户',
          email: formData.email 
        }
      });
    } catch (err) {
      setError('注册失败，请重试');
    } finally {
      setLoading(false);
    }
  };

  const handleSocialRegister = (provider) => {
    console.log(`使用 ${provider} 注册`);
  };

  const BasicInfoStep = () => (
    <Box>
      <Typography variant="h6" gutterBottom>
        基本信息
      </Typography>
      
      <TextField
        margin="normal"
        required
        fullWidth
        id="fullName"
        label="姓名"
        name="fullName"
        autoComplete="name"
        autoFocus
        value={formData.fullName}
        onChange={handleChange}
        InputProps={{
          startAdornment: (
            <InputAdornment position="start">
              <PersonIcon color="action" />
            </InputAdornment>
          ),
        }}
      />
      
      <TextField
        margin="normal"
        required
        fullWidth
        id="email"
        label="邮箱地址"
        name="email"
        autoComplete="email"
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
        autoComplete="new-password"
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
                onClick={() => setShowPassword(!showPassword)}
                edge="end"
              >
                {showPassword ? <VisibilityOff /> : <Visibility />}
              </IconButton>
            </InputAdornment>
          ),
        }}
      />
      
      <TextField
        margin="normal"
        required
        fullWidth
        name="confirmPassword"
        label="确认密码"
        type={showConfirmPassword ? 'text' : 'password'}
        id="confirmPassword"
        value={formData.confirmPassword}
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
                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                edge="end"
              >
                {showConfirmPassword ? <VisibilityOff /> : <Visibility />}
              </IconButton>
            </InputAdornment>
          ),
        }}
      />
      
      <FormControl fullWidth margin="normal">
        <InputLabel>账户类型</InputLabel>
        <Select
          name="userType"
          value={formData.userType}
          label="账户类型"
          onChange={handleChange}
        >
          <MenuItem value="student">学生 - 寻求申请指导</MenuItem>
          <MenuItem value="mentor">导师 - 提供申请指导</MenuItem>
        </Select>
      </FormControl>
    </Box>
  );

  const DetailInfoStep = () => (
    <Box>
      <Typography variant="h6" gutterBottom>
        详细资料
      </Typography>
      
      {formData.userType === 'mentor' && (
        <Alert severity="info" sx={{ mb: 2 }}>
          导师账户需要填写教育背景信息，用于身份认证
        </Alert>
      )}
      
      <TextField
        margin="normal"
        fullWidth
        id="university"
        label="院校"
        name="university"
        value={formData.university}
        onChange={handleChange}
        required={formData.userType === 'mentor'}
        InputProps={{
          startAdornment: (
            <InputAdornment position="start">
              <SchoolIcon color="action" />
            </InputAdornment>
          ),
        }}
      />
      
      <TextField
        margin="normal"
        fullWidth
        id="major"
        label="专业"
        name="major"
        value={formData.major}
        onChange={handleChange}
        required={formData.userType === 'mentor'}
      />
      
      <Box sx={{ display: 'flex', gap: 2 }}>
        <FormControl margin="normal" sx={{ flex: 1 }}>
          <InputLabel>学历</InputLabel>
          <Select
            name="degree"
            value={formData.degree}
            label="学历"
            onChange={handleChange}
          >
            <MenuItem value="bachelor">本科</MenuItem>
            <MenuItem value="master">硕士</MenuItem>
            <MenuItem value="phd">博士</MenuItem>
          </Select>
        </FormControl>
        
        <TextField
          margin="normal"
          sx={{ flex: 1 }}
          id="graduationYear"
          label="毕业年份"
          name="graduationYear"
          type="number"
          value={formData.graduationYear}
          onChange={handleChange}
        />
      </Box>
      
      <TextField
        margin="normal"
        fullWidth
        id="introduction"
        label="个人简介"
        name="introduction"
        multiline
        rows={3}
        value={formData.introduction}
        onChange={handleChange}
        placeholder={formData.userType === 'mentor' 
          ? "请简要介绍您的教育背景和专业经验..." 
          : "请简要介绍您的背景和申请目标..."
        }
      />
    </Box>
  );

  const AgreementStep = () => (
    <Box>
      <Typography variant="h6" gutterBottom>
        完成注册
      </Typography>
      
      <Box sx={{ mb: 3 }}>
        <Typography variant="body1" gutterBottom>
          账户信息确认
        </Typography>
        <Box sx={{ bgcolor: 'grey.50', p: 2, borderRadius: 1 }}>
          <Typography variant="body2"><strong>姓名：</strong>{formData.fullName}</Typography>
          <Typography variant="body2"><strong>邮箱：</strong>{formData.email}</Typography>
          <Typography variant="body2"><strong>类型：</strong>{formData.userType === 'mentor' ? '导师' : '学生'}</Typography>
          {formData.university && (
            <Typography variant="body2"><strong>院校：</strong>{formData.university}</Typography>
          )}
          {formData.major && (
            <Typography variant="body2"><strong>专业：</strong>{formData.major}</Typography>
          )}
        </Box>
      </Box>
      
      <FormControlLabel
        control={
          <Checkbox
            name="agreeTerms"
            checked={formData.agreeTerms}
            onChange={handleChange}
          />
        }
        label={
          <Typography variant="body2">
            我已阅读并同意{' '}
            <Link href="#" color="primary">
              服务条款
            </Link>
          </Typography>
        }
      />
      
      <FormControlLabel
        control={
          <Checkbox
            name="agreePrivacy"
            checked={formData.agreePrivacy}
            onChange={handleChange}
          />
        }
        label={
          <Typography variant="body2">
            我已阅读并同意{' '}
            <Link href="#" color="primary">
              隐私政策
            </Link>
          </Typography>
        }
      />
    </Box>
  );

  return (
    <Container component="main" maxWidth="md">
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
            borderRadius: 3,
          }}
        >
          {/* Logo和标题 */}
          <Box sx={{ textAlign: 'center', mb: 4 }}>
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
              注册账户
            </Typography>
            <Typography variant="body2" color="text.secondary">
              加入我们的留学生社区
            </Typography>
          </Box>

          {/* 步骤指示器 */}
          <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
            {steps.map((label) => (
              <Step key={label}>
                <StepLabel>{label}</StepLabel>
              </Step>
            ))}
          </Stepper>

          {/* 错误提示 */}
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          {/* 表单内容 */}
          <Box component="form" onSubmit={handleSubmit}>
            {activeStep === 0 && <BasicInfoStep />}
            {activeStep === 1 && <DetailInfoStep />}
            {activeStep === 2 && <AgreementStep />}

            {/* 导航按钮 */}
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 3 }}>
              <Button
                disabled={activeStep === 0}
                onClick={handleBack}
              >
                上一步
              </Button>
              
              {activeStep === steps.length - 1 ? (
                <Button
                  type="submit"
                  variant="contained"
                  disabled={loading}
                >
                  {loading ? '注册中...' : '完成注册'}
                </Button>
              ) : (
                <Button
                  variant="contained"
                  onClick={handleNext}
                >
                  下一步
                </Button>
              )}
            </Box>
          </Box>

          {/* 第三方注册（仅在第一步显示） */}
          {activeStep === 0 && (
            <>
              <Divider sx={{ my: 3 }}>
                <Chip label="或者" size="small" />
              </Divider>

              <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
                <Button
                  fullWidth
                  variant="outlined"
                  startIcon={<GoogleIcon />}
                  onClick={() => handleSocialRegister('Google')}
                >
                  Google注册
                </Button>
                <Button
                  fullWidth
                  variant="outlined"
                  startIcon={<GitHubIcon />}
                  onClick={() => handleSocialRegister('GitHub')}
                >
                  GitHub注册
                </Button>
              </Box>
            </>
          )}

          {/* 登录链接 */}
          <Box sx={{ textAlign: 'center', mt: 2 }}>
            <Typography variant="body2">
              已有账户？{' '}
              <Link
                component="button"
                variant="body2"
                onClick={() => navigate('/login')}
              >
                立即登录
              </Link>
            </Typography>
          </Box>
        </Paper>
      </Box>
    </Container>
  );
};

export default RegisterPage;
