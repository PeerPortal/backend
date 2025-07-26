# AI留学规划师Agent手动测试指南

## 🎯 测试目标

验证AI留学规划师Agent的核心功能，包括：
- 基础对话能力
- 工具调用集成
- LangSmith追踪
- 错误处理
- 对话连续性

---

## 🚀 快速开始

### 1. 自动化测试（推荐）

```bash
# 运行综合测试脚本
python test_agent_comprehensive.py

# 或运行LangSmith集成测试
python test_langsmith_integration.py

# 运行快速验证脚本
./verify_langsmith.sh
```

### 2. 启动API服务进行手动测试

```bash
# 启动API服务
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload

# 或使用启动脚本
./start_api.sh
```

服务启动后访问：
- **API文档**: http://localhost:8001/docs
- **健康检查**: http://localhost:8001/api/v1/advanced-planner/health

---

## 🧪 手动测试场景

### 场景1: 基础留学咨询

**测试目标**: 验证Agent对基础留学问题的回答能力

**API调用**:
```bash
curl -X POST "http://localhost:8001/api/v1/advanced-planner/invoke" \
  -H "Content-Type: application/json" \
  -d '{
    "input": "我想申请美国的计算机科学硕士，需要什么条件？",
    "user_id": "test_user_001",
    "session_id": "session_001",
    "chat_history": [],
    "stream": false
  }'
```

**预期结果**:
- ✅ 响应时间 < 10秒
- ✅ 回答包含关键信息：GPA要求、语言成绩、GRE、推荐信等
- ✅ 回答长度 > 200字符
- ✅ LangSmith追踪正常（如果已配置）

**验证要点**:
- 回答的准确性和完整性
- 是否包含具体的申请要求
- 语言表达是否自然流畅

### 场景2: 工具调用测试

**测试目标**: 验证Agent能正确调用各种工具

#### 2.1 网络搜索工具
```bash
curl -X POST "http://localhost:8001/api/v1/advanced-planner/invoke" \
  -H "Content-Type: application/json" \
  -d '{
    "input": "2024年最新的美国大学计算机专业排名是什么？",
    "user_id": "test_user_002",
    "session_id": "session_002",
    "stream": false
  }'
```

**预期结果**:
- ✅ 调用了网络搜索工具
- ✅ 返回最新的排名信息
- ✅ metadata中tool_calls > 0

#### 2.2 知识库搜索
```bash
curl -X POST "http://localhost:8001/api/v1/advanced-planner/invoke" \
  -H "Content-Type: application/json" \
  -d '{
    "input": "Spring Boot框架有哪些核心特性？",
    "user_id": "test_user_003",
    "session_id": "session_003",
    "stream": false
  }'
```

**预期结果**:
- ✅ 调用了知识库搜索工具
- ✅ 返回相关的技术信息
- ✅ 基于上传的知识库文档回答

#### 2.3 数据库查询
```bash
curl -X POST "http://localhost:8001/api/v1/advanced-planner/invoke" \
  -H "Content-Type: application/json" \
  -d '{
    "input": "有哪些计算机科学方面的导师或服务？",
    "user_id": "test_user_004",
    "session_id": "session_004",
    "stream": false
  }'
```

**预期结果**:
- ✅ 调用了数据库查询工具
- ✅ 返回相关的导师或服务信息
- ✅ 数据来自Supabase数据库

### 场景3: 对话连续性测试

**测试目标**: 验证Agent能维持多轮对话的上下文

#### 第一轮对话
```bash
curl -X POST "http://localhost:8001/api/v1/advanced-planner/invoke" \
  -H "Content-Type: application/json" \
  -d '{
    "input": "我想申请美国的研究生",
    "user_id": "continuity_user",
    "session_id": "continuity_session",
    "chat_history": [],
    "stream": false
  }'
```

#### 第二轮对话（基于第一轮的响应）
```bash
curl -X POST "http://localhost:8001/api/v1/advanced-planner/invoke" \
  -H "Content-Type: application/json" \
  -d '{
    "input": "我的专业是计算机科学，GPA 3.7",
    "user_id": "continuity_user",
    "session_id": "continuity_session",
    "chat_history": [
      {"role": "user", "content": "我想申请美国的研究生"},
      {"role": "assistant", "content": "第一轮的回答内容"}
    ],
    "stream": false
  }'
```

#### 第三轮对话
```bash
curl -X POST "http://localhost:8001/api/v1/advanced-planner/invoke" \
  -H "Content-Type: application/json" \
  -d '{
    "input": "你觉得我应该申请哪些学校？",
    "user_id": "continuity_user", 
    "session_id": "continuity_session",
    "chat_history": [
      {"role": "user", "content": "我想申请美国的研究生"},
      {"role": "assistant", "content": "第一轮的回答内容"},
      {"role": "user", "content": "我的专业是计算机科学，GPA 3.7"},
      {"role": "assistant", "content": "第二轮的回答内容"}
    ],
    "stream": false
  }'
```

**预期结果**:
- ✅ Agent能记住之前的对话内容
- ✅ 回答基于前面提供的信息（专业、GPA等）
- ✅ 给出个性化的学校推荐

### 场景4: 流式响应测试

**测试目标**: 验证流式响应功能

```bash
curl -X POST "http://localhost:8001/api/v1/advanced-planner/invoke" \
  -H "Content-Type: application/json" \
  -d '{
    "input": "请详细介绍一下申请美国研究生的完整流程",
    "user_id": "stream_user",
    "session_id": "stream_session",
    "stream": true
  }' \
  --no-buffer
```

**预期结果**:
- ✅ 返回流式数据（Server-Sent Events格式）
- ✅ 逐步输出回答内容
- ✅ 最后发送完成信号

### 场景5: 错误处理测试

#### 5.1 空输入测试
```bash
curl -X POST "http://localhost:8001/api/v1/advanced-planner/invoke" \
  -H "Content-Type: application/json" \
  -d '{
    "input": "",
    "user_id": "error_user",
    "session_id": "error_session",
    "stream": false
  }'
```

**预期结果**:
- ✅ 返回400错误或优雅的错误提示
- ✅ 不会导致服务崩溃

#### 5.2 超长输入测试
```bash
curl -X POST "http://localhost:8001/api/v1/advanced-planner/invoke" \
  -H "Content-Type: application/json" \
  -d '{
    "input": "'$(python -c "print('很长的测试输入' * 200)")'"",
    "user_id": "error_user",
    "session_id": "error_session",
    "stream": false
  }'
```

**预期结果**:
- ✅ 输入长度验证生效
- ✅ 返回适当的错误信息

---

## 📊 LangSmith监控验证

### 1. 检查LangSmith Dashboard

访问 https://smith.langchain.com 并检查：

- **项目**: AI留学规划师
- **追踪记录**: 每次API调用都应有对应的trace
- **执行时间**: 监控响应时间趋势
- **工具调用**: 查看工具使用统计
- **错误监控**: 检查是否有异常记录

### 2. 本地追踪验证

检查终端输出中的LangSmith日志：
```
🔍 [LangSmith] 开始追踪Agent运行 - 用户: test_user_001
✅ [LangSmith] Agent运行完成 - 用户: test_user_001, 执行时间: 2.34秒
```

---

## 🔧 故障排查

### 常见问题及解决方案

#### 1. Agent初始化失败
**现象**: 
```
❌ Agent初始化失败: 'NoneType' object has no attribute...
```

**解决方案**:
- 检查 `.env` 文件中的 `OPENAI_API_KEY` 是否正确
- 验证网络连接和API配额
- 检查依赖包是否完整安装

#### 2. 工具调用失败
**现象**: 
```
⚠️ 工具调用异常: API key not found
```

**解决方案**:
- 检查 `TAVILY_API_KEY` 配置
- 验证 Supabase 数据库连接
- 检查知识库文件是否存在

#### 3. LangSmith追踪不显示
**现象**: 
```
🔍 LangSmith状态: 未启用
```

**解决方案**:
- 检查 `LANGCHAIN_TRACING_V2=true`
- 验证 `LANGCHAIN_API_KEY` 是否有效
- 确认 `LANGCHAIN_PROJECT` 名称正确

#### 4. 数据库连接错误
**现象**:
```
❌ 数据库连接失败: could not connect to server
```

**解决方案**:
- 检查 Supabase URL 和密钥
- 验证网络连接
- 检查数据库是否正常运行

---

## 📝 测试记录模板

### 测试执行记录

| 测试场景 | 执行时间 | 结果 | 响应时间 | 工具调用 | 备注 |
|---------|---------|------|---------|---------|------|
| 基础咨询 | 2024-01-25 | ✅/❌ | 2.3s | 1次 | |
| 网络搜索 | 2024-01-25 | ✅/❌ | 4.1s | 2次 | |
| 知识库查询 | 2024-01-25 | ✅/❌ | 1.8s | 1次 | |
| 对话连续性 | 2024-01-25 | ✅/❌ | 2.1s | 0次 | |
| 流式响应 | 2024-01-25 | ✅/❌ | 3.2s | 1次 | |

### 性能基准

- **目标响应时间**: < 5秒
- **成功率**: > 95%
- **用户满意度**: 基于回答质量评估
- **工具调用成功率**: > 90%

---

## 🎯 测试完成清单

- [ ] 自动化测试脚本运行成功
- [ ] API服务正常启动
- [ ] 基础对话功能正常
- [ ] 各种工具调用成功
- [ ] 对话连续性维持良好
- [ ] 流式响应功能正常
- [ ] 错误处理机制有效
- [ ] LangSmith追踪正常记录
- [ ] 性能指标符合预期
- [ ] 用户体验满意

---

**💡 提示**: 
- 首次运行建议使用自动化测试脚本 `python test_agent_comprehensive.py`
- 如需深入测试特定功能，可使用对应的手动测试场景
- 建议在不同网络环境下进行测试以验证稳定性
- 定期运行测试以确保功能持续正常
