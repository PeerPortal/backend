# Supabase CLI 推送方法

## 安装 Supabase CLI
```bash
npm install -g supabase
# 或者
brew install supabase/tap/supabase
```

## 初始化项目
```bash
supabase init
```

## 登录
```bash
supabase login
```

## 链接到远程项目
```bash
supabase link --project-ref mbpqctxpzxehrevxlhfl
```

## 创建迁移文件
```bash
supabase migration new mentorship_system
```

## 将我们的 SQL 复制到迁移文件中
然后执行：
```bash
supabase db push
```

## 或者直接重置数据库（谨慎使用）
```bash
supabase db reset
```
