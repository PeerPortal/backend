/*
留学申请AI咨询聊天界面
基于React的实时聊天组件
*/

import React, { useState, useEffect, useRef } from 'react';
import { Send, User, Bot, FileText, School, Calendar, Award } from 'lucide-react';

const AIConsultationChat = () => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      role: 'assistant',
      content: '你好！我是小申，你的留学申请AI助手。我可以帮你分析背景、推荐学校、制定申请策略。请告诉我你的基本情况，我们开始咨询吧！',
      timestamp: new Date(),
      type: 'text'
    }
  ]);

  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [userProfile, setUserProfile] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [chatPhase, setChatPhase] = useState('greeting'); // greeting, profile, analysis, recommendations, strategy, chat

  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    // 初始化会话
    initializeSession();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const initializeSession = async () => {
    try {
      const response = await fetch('/api/v1/consultation/sessions/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        setSessionId(data.session_id);
      }
    } catch (error) {
      console.error('初始化会话失败:', error);
    }
  };

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = {
      id: Date.now(),
      role: 'user',
      content: inputMessage,
      timestamp: new Date(),
      type: 'text'
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      // 根据聊天阶段决定处理方式
      if (chatPhase === 'greeting') {
        // 引导用户填写基本信息
        await handleGreetingPhase(inputMessage);
      } else if (chatPhase === 'profile') {
        // 收集档案信息
        await handleProfilePhase(inputMessage);
      } else {
        // 正常聊天
        await handleChatMessage(inputMessage);
      }
    } catch (error) {
      console.error('发送消息失败:', error);
      addSystemMessage('抱歉，消息发送失败，请稍后重试。');
    } finally {
      setIsLoading(false);
    }
  };

  const handleGreetingPhase = async (message) => {
    // 智能识别用户意图
    const intent = analyzeUserIntent(message);

    if (intent === 'profile_info') {
      setChatPhase('profile');
      addSystemMessage('太好了！为了给你更精准的建议，我需要了解你的背景信息。让我们开始填写你的档案吧！');
      setTimeout(() => {
        showProfileForm();
      }, 1000);
    } else if (intent === 'school_question') {
      addSystemMessage('我很乐意帮你了解学校信息！不过为了给你最合适的推荐，建议先完善你的背景档案。这样我就能为你量身定制推荐方案了。');
    } else {
      await handleChatMessage(message);
    }
  };

  const handleProfilePhase = async (message) => {
    // 在这个阶段，主要通过表单收集信息
    addSystemMessage('请使用上方的表单填写你的详细信息，这样我就能为你进行专业的背景分析了！');
  };

  const handleChatMessage = async (message) => {
    if (!sessionId) {
      addSystemMessage('会话未初始化，请刷新页面重试。');
      return;
    }

    try {
      const response = await fetch(`/api/v1/consultation/chat/${sessionId}/message`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ message })
      });

      if (response.ok) {
        const data = await response.json();
        addAssistantMessage(data.ai_response);
      } else {
        addSystemMessage('抱歉，我暂时无法回应。请稍后再试。');
      }
    } catch (error) {
      addSystemMessage('网络连接出现问题，请检查网络后重试。');
    }
  };

  const analyzeUserIntent = (message) => {
    const lowerMessage = message.toLowerCase();

    if (lowerMessage.includes('档案') || lowerMessage.includes('背景') || lowerMessage.includes('信息')) {
      return 'profile_info';
    } else if (lowerMessage.includes('学校') || lowerMessage.includes('推荐') || lowerMessage.includes('大学')) {
      return 'school_question';
    } else if (lowerMessage.includes('申请') || lowerMessage.includes('策略') || lowerMessage.includes('规划')) {
      return 'strategy_question';
    } else {
      return 'general';
    }
  };

  const addAssistantMessage = (content, type = 'text', metadata = {}) => {
    const message = {
      id: Date.now(),
      role: 'assistant',
      content,
      timestamp: new Date(),
      type,
      metadata
    };
    setMessages(prev => [...prev, message]);
  };

  const addSystemMessage = (content) => {
    addAssistantMessage(content, 'system');
  };

  const showProfileForm = () => {
    const formMessage = {
      id: Date.now(),
      role: 'assistant',
      content: '',
      timestamp: new Date(),
      type: 'profile_form'
    };
    setMessages(prev => [...prev, formMessage]);
  };

  const submitProfile = async (profileData) => {
    if (!sessionId) return;

    setIsLoading(true);

    try {
      const response = await fetch('/api/v1/consultation/analysis/profile', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          session_id: sessionId,
          ...profileData
        })
      });

      if (response.ok) {
        const data = await response.json();
        setUserProfile(profileData);
        setAnalysis(data.analysis);
        setChatPhase('analysis');

        // 显示分析结果
        showAnalysisResult(data.analysis);

        setTimeout(() => {
          addAssistantMessage('分析完成！我发现你有很多亮点。现在我来为你推荐一些合适的学校吧！');
          generateSchoolRecommendations();
        }, 2000);
      }
    } catch (error) {
      console.error('档案提交失败:', error);
      addSystemMessage('档案分析失败，请稍后重试。');
    } finally {
      setIsLoading(false);
    }
  };

  const showAnalysisResult = (analysisData) => {
    const analysisMessage = {
      id: Date.now(),
      role: 'assistant',
      content: '',
      timestamp: new Date(),
      type: 'analysis_result',
      metadata: { analysis: analysisData }
    };
    setMessages(prev => [...prev, analysisMessage]);
  };

  const generateSchoolRecommendations = async () => {
    if (!sessionId) return;

    try {
      const response = await fetch(`/api/v1/consultation/recommendations/${sessionId}/schools`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setRecommendations(data.recommendations_by_tier);
        setChatPhase('recommendations');

        // 显示推荐结果
        showRecommendationResult(data.recommendations_by_tier);

        setTimeout(() => {
          addAssistantMessage('学校推荐已生成！现在有什么具体问题想要咨询的吗？比如申请策略、文书写作、面试准备等。');
          setChatPhase('chat');
        }, 3000);
      }
    } catch (error) {
      console.error('生成推荐失败:', error);
      addSystemMessage('学校推荐生成失败，请稍后重试。');
    }
  };

  const showRecommendationResult = (recommendationsData) => {
    const recMessage = {
      id: Date.now(),
      role: 'assistant',
      content: '',
      timestamp: new Date(),
      type: 'recommendations',
      metadata: { recommendations: recommendationsData }
    };
    setMessages(prev => [...prev, recMessage]);
  };

  const MessageComponent = ({ message }) => {
    const isUser = message.role === 'user';

    return (
      <div className={`flex items-start space-x-3 ${isUser ? 'flex-row-reverse space-x-reverse' : ''} mb-4`}>
        <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${isUser ? 'bg-blue-500' : 'bg-green-500'
          }`}>
          {isUser ? <User size={16} className="text-white" /> : <Bot size={16} className="text-white" />}
        </div>

        <div className={`flex-1 max-w-md ${isUser ? 'text-right' : ''}`}>
          <div className={`rounded-lg px-4 py-2 ${isUser
              ? 'bg-blue-500 text-white'
              : message.type === 'system'
                ? 'bg-gray-100 text-gray-700 border border-gray-200'
                : 'bg-white border border-gray-200'
            }`}>
            {message.type === 'text' || message.type === 'system' ? (
              <p className="text-sm">{message.content}</p>
            ) : message.type === 'profile_form' ? (
              <ProfileForm onSubmit={submitProfile} />
            ) : message.type === 'analysis_result' ? (
              <AnalysisResultCard analysis={message.metadata.analysis} />
            ) : message.type === 'recommendations' ? (
              <RecommendationsCard recommendations={message.metadata.recommendations} />
            ) : null}
          </div>

          <div className="text-xs text-gray-500 mt-1">
            {message.timestamp.toLocaleTimeString()}
          </div>
        </div>
      </div>
    );
  };

  const ProfileForm = ({ onSubmit }) => {
    const [formData, setFormData] = useState({
      name: '',
      target_degree: 'master',
      target_major: '',
      target_year: '2025Fall',
      academic_background: {
        undergraduate_school: '',
        undergraduate_major: '',
        gpa: '',
        school_ranking: '',
        core_courses: []
      },
      test_scores: {
        gre_total: '',
        gre_verbal: '',
        gre_quantitative: '',
        toefl_total: ''
      }
    });

    const handleSubmit = (e) => {
      e.preventDefault();
      onSubmit(formData);
    };

    return (
      <div className="bg-gray-50 p-4 rounded-lg">
        <h3 className="text-lg font-semibold mb-4 flex items-center">
          <FileText className="mr-2" size={20} />
          背景档案信息
        </h3>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">姓名</label>
              <input
                type="text"
                className="w-full p-2 border rounded-md"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">目标学位</label>
              <select
                className="w-full p-2 border rounded-md"
                value={formData.target_degree}
                onChange={(e) => setFormData({ ...formData, target_degree: e.target.value })}
              >
                <option value="master">硕士</option>
                <option value="phd">博士</option>
                <option value="bachelor">本科</option>
              </select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">目标专业</label>
              <input
                type="text"
                className="w-full p-2 border rounded-md"
                placeholder="如: Computer Science"
                value={formData.target_major}
                onChange={(e) => setFormData({ ...formData, target_major: e.target.value })}
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">申请年份</label>
              <select
                className="w-full p-2 border rounded-md"
                value={formData.target_year}
                onChange={(e) => setFormData({ ...formData, target_year: e.target.value })}
              >
                <option value="2025Fall">2025 Fall</option>
                <option value="2025Spring">2025 Spring</option>
                <option value="2026Fall">2026 Fall</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">本科院校</label>
            <input
              type="text"
              className="w-full p-2 border rounded-md"
              value={formData.academic_background.undergraduate_school}
              onChange={(e) => setFormData({
                ...formData,
                academic_background: {
                  ...formData.academic_background,
                  undergraduate_school: e.target.value
                }
              })}
              required
            />
          </div>

          <div className="grid grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">本科专业</label>
              <input
                type="text"
                className="w-full p-2 border rounded-md"
                value={formData.academic_background.undergraduate_major}
                onChange={(e) => setFormData({
                  ...formData,
                  academic_background: {
                    ...formData.academic_background,
                    undergraduate_major: e.target.value
                  }
                })}
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">GPA</label>
              <input
                type="number"
                step="0.01"
                min="0"
                max="4"
                className="w-full p-2 border rounded-md"
                value={formData.academic_background.gpa}
                onChange={(e) => setFormData({
                  ...formData,
                  academic_background: {
                    ...formData.academic_background,
                    gpa: parseFloat(e.target.value)
                  }
                })}
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">GRE总分</label>
              <input
                type="number"
                className="w-full p-2 border rounded-md"
                value={formData.test_scores.gre_total}
                onChange={(e) => setFormData({
                  ...formData,
                  test_scores: {
                    ...formData.test_scores,
                    gre_total: parseInt(e.target.value)
                  }
                })}
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">TOEFL</label>
              <input
                type="number"
                className="w-full p-2 border rounded-md"
                value={formData.test_scores.toefl_total}
                onChange={(e) => setFormData({
                  ...formData,
                  test_scores: {
                    ...formData.test_scores,
                    toefl_total: parseInt(e.target.value)
                  }
                })}
              />
            </div>
          </div>

          <button
            type="submit"
            className="w-full bg-blue-500 text-white py-2 px-4 rounded-md hover:bg-blue-600 transition-colors"
          >
            提交档案并开始分析
          </button>
        </form>
      </div>
    );
  };

  const AnalysisResultCard = ({ analysis }) => {
    return (
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 p-4 rounded-lg border">
        <h3 className="text-lg font-semibold mb-4 flex items-center text-blue-700">
          <Award className="mr-2" size={20} />
          背景分析结果
        </h3>

        <div className="space-y-4">
          <div className="bg-white p-3 rounded-md">
            <div className="flex items-center justify-between mb-2">
              <span className="font-medium">竞争力评分</span>
              <span className="text-2xl font-bold text-blue-600">
                {analysis.competitiveness_score}/10
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-blue-500 h-2 rounded-full"
                style={{ width: `${(analysis.competitiveness_score / 10) * 100}%` }}
              ></div>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="bg-green-50 p-3 rounded-md">
              <h4 className="font-medium text-green-700 mb-2">主要优势</h4>
              <ul className="text-sm space-y-1">
                {analysis.strengths.slice(0, 3).map((strength, index) => (
                  <li key={index} className="flex items-start">
                    <span className="text-green-500 mr-1">•</span>
                    {strength}
                  </li>
                ))}
              </ul>
            </div>

            <div className="bg-orange-50 p-3 rounded-md">
              <h4 className="font-medium text-orange-700 mb-2">改进建议</h4>
              <ul className="text-sm space-y-1">
                {analysis.improvement_suggestions.slice(0, 3).map((suggestion, index) => (
                  <li key={index} className="flex items-start">
                    <span className="text-orange-500 mr-1">•</span>
                    {suggestion}
                  </li>
                ))}
              </ul>
            </div>
          </div>

          <div className="bg-white p-3 rounded-md">
            <h4 className="font-medium mb-2">录取概率评估</h4>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>冲刺档学校</span>
                <span className="font-medium">{Math.round(analysis.success_probability.reach * 100)}%</span>
              </div>
              <div className="flex justify-between text-sm">
                <span>匹配档学校</span>
                <span className="font-medium">{Math.round(analysis.success_probability.match * 100)}%</span>
              </div>
              <div className="flex justify-between text-sm">
                <span>保底档学校</span>
                <span className="font-medium">{Math.round(analysis.success_probability.safety * 100)}%</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  };

  const RecommendationsCard = ({ recommendations }) => {
    return (
      <div className="bg-gradient-to-r from-green-50 to-emerald-50 p-4 rounded-lg border">
        <h3 className="text-lg font-semibold mb-4 flex items-center text-green-700">
          <School className="mr-2" size={20} />
          学校推荐方案
        </h3>

        <div className="space-y-4">
          {Object.entries(recommendations).map(([tier, schools]) => (
            <div key={tier} className="bg-white p-3 rounded-md">
              <h4 className="font-medium mb-2 capitalize">
                {tier === 'reach' ? '🎯 冲刺档' : tier === 'match' ? '🎯 匹配档' : '🎯 保底档'}
                ({schools.length}所)
              </h4>
              <div className="space-y-2">
                {schools.slice(0, 3).map((school, index) => (
                  <div key={index} className="text-sm border-l-2 border-gray-200 pl-3">
                    <div className="font-medium">{school.name}</div>
                    <div className="text-gray-600">{school.recommendation_reason}</div>
                    <div className="text-xs text-green-600">
                      录取概率: {Math.round(school.success_probability * 100)}%
                    </div>
                  </div>
                ))}
                {schools.length > 3 && (
                  <div className="text-xs text-gray-500">
                    +{schools.length - 3} 所其他学校...
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>

        <div className="mt-4 p-3 bg-blue-50 rounded-md">
          <p className="text-sm text-blue-700">
            💡 建议申请 12-15 所学校，保持合理的档次分布。点击每所学校可查看详细信息和申请要求。
          </p>
        </div>
      </div>
    );
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* 标题栏 */}
      <div className="bg-white border-b border-gray-200 p-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-xl font-semibold text-gray-800">留学申请AI咨询</h1>
            <p className="text-sm text-gray-500">
              {chatPhase === 'greeting' ? '欢迎使用AI咨询服务' :
                chatPhase === 'profile' ? '正在收集背景信息...' :
                  chatPhase === 'analysis' ? '正在分析背景档案...' :
                    chatPhase === 'recommendations' ? '正在生成学校推荐...' :
                      '智能咨询进行中'}
            </p>
          </div>
          <div className="flex items-center space-x-2">
            <div className={`w-2 h-2 rounded-full ${isLoading ? 'bg-yellow-400' : 'bg-green-400'}`}></div>
            <span className="text-xs text-gray-500">
              {isLoading ? '思考中...' : '在线'}
            </span>
          </div>
        </div>
      </div>

      {/* 聊天区域 */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map(message => (
          <MessageComponent key={message.id} message={message} />
        ))}

        {isLoading && (
          <div className="flex items-center space-x-3 mb-4">
            <div className="flex-shrink-0 w-8 h-8 rounded-full bg-green-500 flex items-center justify-center">
              <Bot size={16} className="text-white" />
            </div>
            <div className="bg-white border border-gray-200 rounded-lg px-4 py-2">
              <div className="flex space-x-1">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* 输入区域 */}
      <div className="bg-white border-t border-gray-200 p-4">
        <div className="flex items-center space-x-2">
          <div className="flex-1 relative">
            <textarea
              ref={inputRef}
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="输入你的问题..."
              className="w-full p-3 border border-gray-300 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
              rows="1"
              style={{ maxHeight: '120px' }}
            />
          </div>
          <button
            onClick={sendMessage}
            disabled={!inputMessage.trim() || isLoading}
            className="bg-blue-500 text-white p-3 rounded-lg hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
          >
            <Send size={20} />
          </button>
        </div>

        <div className="mt-2 flex items-center space-x-4 text-xs text-gray-500">
          <span>按 Enter 发送，Shift+Enter 换行</span>
          {sessionId && (
            <span>会话ID: {sessionId.slice(-8)}</span>
          )}
        </div>
      </div>
    </div>
  );
};

export default AIConsultationChat;
