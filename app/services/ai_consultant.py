"""
AI留学申请咨询服务
提供智能背景分析、学校推荐和申请策略
"""
from typing import Dict, List, Optional, Any
from pydantic import BaseModel
from enum import Enum
import json
import openai
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# 枚举定义
class TargetDegree(str, Enum):
    BACHELOR = "bachelor"
    MASTER = "master"
    PHD = "phd"
    MBA = "mba"

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class MessageType(str, Enum):
    TEXT = "text"
    ANALYSIS = "analysis"
    RECOMMENDATION = "recommendation"
    STRATEGY = "strategy"

# 数据模型
class AcademicBackground(BaseModel):
    undergraduate_school: str
    undergraduate_major: str
    gpa: float
    school_ranking: Optional[int] = None
    core_courses: List[str] = []

class TestScores(BaseModel):
    gre_total: Optional[int] = None
    gre_verbal: Optional[int] = None
    gre_quantitative: Optional[int] = None
    gre_writing: Optional[float] = None
    toefl_total: Optional[int] = None
    ielts_total: Optional[float] = None

class ResearchExperience(BaseModel):
    title: str
    institution: str
    duration: str
    description: str
    advisor: Optional[str] = None
    publications: List[str] = []

class WorkExperience(BaseModel):
    title: str
    company: str
    duration: str
    description: str
    skills_gained: List[str] = []

class UserProfile(BaseModel):
    name: str
    target_degree: TargetDegree
    target_major: str
    target_year: str
    
    academic_background: AcademicBackground
    test_scores: TestScores
    research_experiences: List[ResearchExperience] = []
    work_experiences: List[WorkExperience] = []
    awards: List[str] = []
    extracurriculars: List[str] = []

class ProfileAnalysis(BaseModel):
    competitiveness_score: float  # 1-10
    strengths: List[str]
    weaknesses: List[str]
    success_probability: Dict[str, float]  # {"reach": 0.2, "match": 0.7, "safety": 0.9}
    improvement_suggestions: List[str]
    overall_assessment: str

class SchoolRecommendation(BaseModel):
    name: str
    ranking: Optional[int]
    tier: str  # reach/match/safety
    recommendation_reason: str
    admission_requirements: Dict[str, Any]
    difficulty_assessment: str
    special_advantages: List[str]
    success_probability: float

class ApplicationStrategy(BaseModel):
    timeline: Dict[str, List[str]]  # 按月份组织的任务列表
    essay_themes: List[str]
    recommendation_letter_strategy: str
    interview_preparation: List[str]
    scholarship_opportunities: List[str]

class ChatMessage(BaseModel):
    role: MessageRole
    content: str
    message_type: MessageType = MessageType.TEXT
    timestamp: datetime = datetime.now()
    metadata: Dict[str, Any] = {}

class ConsultationSession(BaseModel):
    session_id: str
    user_profile: Optional[UserProfile] = None
    analysis: Optional[ProfileAnalysis] = None
    school_recommendations: List[SchoolRecommendation] = []
    strategy: Optional[ApplicationStrategy] = None
    chat_history: List[ChatMessage] = []
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

class AIConsultantService:
    """AI留学申请咨询服务"""
    
    def __init__(self, openai_api_key: str, model: str = "gpt-4"):
        self.openai_api_key = openai_api_key
        self.model = model
        openai.api_key = openai_api_key
    
    async def analyze_profile(self, profile: UserProfile) -> ProfileAnalysis:
        """分析用户背景"""
        prompt = self._build_analysis_prompt(profile)
        
        try:
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt("analysis")},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1500
            )
            
            # 解析AI响应
            analysis_text = response.choices[0].message.content
            analysis_data = self._parse_analysis_response(analysis_text)
            
            return ProfileAnalysis(**analysis_data)
            
        except Exception as e:
            logger.error(f"背景分析失败: {e}")
            raise
    
    async def recommend_schools(self, profile: UserProfile, analysis: ProfileAnalysis) -> List[SchoolRecommendation]:
        """推荐学校"""
        prompt = self._build_recommendation_prompt(profile, analysis)
        
        try:
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt("recommendation")},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,
                max_tokens=2000
            )
            
            recommendations_text = response.choices[0].message.content
            recommendations_data = self._parse_recommendations_response(recommendations_text)
            
            return [SchoolRecommendation(**rec) for rec in recommendations_data]
            
        except Exception as e:
            logger.error(f"学校推荐失败: {e}")
            raise
    
    async def generate_strategy(self, profile: UserProfile, analysis: ProfileAnalysis, 
                              schools: List[SchoolRecommendation]) -> ApplicationStrategy:
        """生成申请策略"""
        prompt = self._build_strategy_prompt(profile, analysis, schools)
        
        try:
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt("strategy")},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1800
            )
            
            strategy_text = response.choices[0].message.content
            strategy_data = self._parse_strategy_response(strategy_text)
            
            return ApplicationStrategy(**strategy_data)
            
        except Exception as e:
            logger.error(f"策略生成失败: {e}")
            raise
    
    async def chat_consultation(self, session: ConsultationSession, 
                              user_message: str) -> str:
        """智能对话咨询"""
        # 构建对话上下文
        messages = [
            {"role": "system", "content": self._get_system_prompt("chat")},
        ]
        
        # 添加用户档案上下文
        if session.user_profile:
            context = self._build_profile_context(session.user_profile)
            messages.append({"role": "system", "content": f"用户背景信息: {context}"})
        
        # 添加分析结果上下文
        if session.analysis:
            analysis_context = self._build_analysis_context(session.analysis)
            messages.append({"role": "system", "content": f"背景分析结果: {analysis_context}"})
        
        # 添加历史对话
        for msg in session.chat_history[-10:]:  # 保留最近10条消息
            messages.append({
                "role": msg.role.value,
                "content": msg.content
            })
        
        # 添加当前用户消息
        messages.append({"role": "user", "content": user_message})
        
        try:
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=messages,
                temperature=0.6,
                max_tokens=1000
            )
            
            assistant_response = response.choices[0].message.content
            
            # 更新会话历史
            session.chat_history.append(ChatMessage(
                role=MessageRole.USER,
                content=user_message
            ))
            session.chat_history.append(ChatMessage(
                role=MessageRole.ASSISTANT,
                content=assistant_response
            ))
            
            return assistant_response
            
        except Exception as e:
            logger.error(f"对话咨询失败: {e}")
            raise
    
    def _get_system_prompt(self, task_type: str) -> str:
        """获取系统提示词"""
        prompts = {
            "analysis": """你是一位资深的留学申请顾问，拥有15年的申请指导经验。
            你需要客观、专业地分析学生的申请背景，识别优势和劣势，提供实用的改进建议。
            请以JSON格式返回结构化的分析结果。""",
            
            "recommendation": """你是一位经验丰富的留学顾问，熟悉全球各大学的录取要求和特点。
            请基于学生背景推荐合适的学校，确保推荐的学校层次合理，既有冲刺又有保底。
            请以JSON格式返回结构化的推荐结果。""",
            
            "strategy": """你是一位留学申请策略专家，擅长制定详细的申请计划和时间安排。
            请为学生制定个性化的申请策略，包括时间规划、文书主题、面试准备等。
            请以JSON格式返回结构化的策略方案。""",
            
            "chat": """你是一位亲切、专业的留学申请顾问AI助手，名字叫"小申"。
            你要用温暖、鼓励的语气与学生对话，回答他们关于留学申请的各种问题。
            你可以基于学生的背景信息和分析结果提供个性化的建议。
            请用中文回答，语气要友好专业。"""
        }
        return prompts.get(task_type, prompts["chat"])
    
    def _build_analysis_prompt(self, profile: UserProfile) -> str:
        """构建背景分析提示"""
        return f"""
        请分析以下学生的留学申请背景：

        基本信息：
        - 姓名: {profile.name}
        - 目标: {profile.target_degree.value} in {profile.target_major}
        - 申请年份: {profile.target_year}

        学术背景：
        - 本科院校: {profile.academic_background.undergraduate_school}
        - 专业: {profile.academic_background.undergraduate_major}
        - GPA: {profile.academic_background.gpa}/4.0
        - 院校排名: {profile.academic_background.school_ranking or '未知'}
        - 核心课程: {', '.join(profile.academic_background.core_courses)}

        标准化考试：
        - GRE总分: {profile.test_scores.gre_total or '未考'}
        - GRE各项: V{profile.test_scores.gre_verbal or '?'} Q{profile.test_scores.gre_quantitative or '?'} W{profile.test_scores.gre_writing or '?'}
        - TOEFL: {profile.test_scores.toefl_total or '未考'}
        - IELTS: {profile.test_scores.ielts_total or '未考'}

        研究经历：
        {self._format_experiences(profile.research_experiences)}

        工作/实习经历：
        {self._format_work_experiences(profile.work_experiences)}

        其他背景：
        - 获奖情况: {', '.join(profile.awards) if profile.awards else '无'}
        - 课外活动: {', '.join(profile.extracurriculars) if profile.extracurriculars else '无'}

        请从以下维度进行分析并以JSON格式返回：
        {{
            "competitiveness_score": 数值(1-10),
            "strengths": ["优势1", "优势2", ...],
            "weaknesses": ["劣势1", "劣势2", ...],
            "success_probability": {{"reach": 0.0-1.0, "match": 0.0-1.0, "safety": 0.0-1.0}},
            "improvement_suggestions": ["建议1", "建议2", ...],
            "overall_assessment": "总体评估文字"
        }}
        """
    
    def _build_recommendation_prompt(self, profile: UserProfile, analysis: ProfileAnalysis) -> str:
        """构建学校推荐提示"""
        return f"""
        基于以下学生背景和分析结果，请推荐15所适合的学校：

        学生目标：{profile.target_degree.value} in {profile.target_major}, {profile.target_year}
        竞争力评分：{analysis.competitiveness_score}/10

        主要优势：{', '.join(analysis.strengths)}
        主要劣势：{', '.join(analysis.weaknesses)}

        成功概率评估：
        - 冲刺档: {analysis.success_probability.get('reach', 0.2)*100}%
        - 匹配档: {analysis.success_probability.get('match', 0.7)*100}%
        - 保底档: {analysis.success_probability.get('safety', 0.9)*100}%

        请推荐学校并以JSON数组格式返回：
        [
            {{
                "name": "学校名称",
                "ranking": 排名数值或null,
                "tier": "reach/match/safety",
                "recommendation_reason": "推荐理由",
                "admission_requirements": {{"key": "value"}},
                "difficulty_assessment": "难度评估",
                "special_advantages": ["优势1", "优势2"],
                "success_probability": 0.0-1.0
            }},
            ...
        ]

        推荐分布：冲刺档5所，匹配档7所，保底档3所
        """
    
    def _build_strategy_prompt(self, profile: UserProfile, analysis: ProfileAnalysis, 
                             schools: List[SchoolRecommendation]) -> str:
        """构建申请策略提示"""
        school_list = [f"{school.name} ({school.tier})" for school in schools[:10]]
        
        return f"""
        请为以下学生制定详细的留学申请策略：

        学生目标：{profile.target_degree.value} in {profile.target_major}, {profile.target_year}
        申请学校：{', '.join(school_list)}

        背景分析：
        - 竞争力评分：{analysis.competitiveness_score}/10
        - 主要优势：{', '.join(analysis.strengths[:3])}
        - 需要改进：{', '.join(analysis.weaknesses[:3])}

        请制定申请策略并以JSON格式返回：
        {{
            "timeline": {{
                "2024年8月": ["任务1", "任务2"],
                "2024年9月": ["任务1", "任务2"],
                ...按月份到申请截止日期
            }},
            "essay_themes": ["文书主题1", "文书主题2", ...],
            "recommendation_letter_strategy": "推荐信策略描述",
            "interview_preparation": ["准备要点1", "准备要点2", ...],
            "scholarship_opportunities": ["奖学金机会1", "奖学金机会2", ...]
        }}
        """
    
    def _format_experiences(self, experiences: List[ResearchExperience]) -> str:
        """格式化研究经历"""
        if not experiences:
            return "无研究经历"
        
        formatted = []
        for exp in experiences:
            pub_info = f", 发表论文{len(exp.publications)}篇" if exp.publications else ""
            formatted.append(f"- {exp.title} ({exp.institution}, {exp.duration}){pub_info}")
        
        return '\n'.join(formatted)
    
    def _format_work_experiences(self, experiences: List[WorkExperience]) -> str:
        """格式化工作经历"""
        if not experiences:
            return "无实习/工作经历"
        
        formatted = []
        for exp in experiences:
            formatted.append(f"- {exp.title} ({exp.company}, {exp.duration})")
        
        return '\n'.join(formatted)
    
    def _build_profile_context(self, profile: UserProfile) -> str:
        """构建用户档案上下文"""
        return f"""
        用户：{profile.name}，目标申请{profile.target_year} {profile.target_degree.value} in {profile.target_major}
        本科：{profile.academic_background.undergraduate_school} {profile.academic_background.undergraduate_major} GPA:{profile.academic_background.gpa}
        考试：GRE {profile.test_scores.gre_total or '未考'}, TOEFL {profile.test_scores.toefl_total or '未考'}
        """
    
    def _build_analysis_context(self, analysis: ProfileAnalysis) -> str:
        """构建分析结果上下文"""
        return f"""
        竞争力评分：{analysis.competitiveness_score}/10
        主要优势：{', '.join(analysis.strengths[:3])}
        需要改进：{', '.join(analysis.weaknesses[:3])}
        """
    
    def _parse_analysis_response(self, response_text: str) -> Dict[str, Any]:
        """解析背景分析响应"""
        try:
            # 尝试直接解析JSON
            return json.loads(response_text)
        except json.JSONDecodeError:
            # 如果直接解析失败，尝试提取JSON部分
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                # 解析失败时返回默认结构
                return {
                    "competitiveness_score": 5.0,
                    "strengths": ["待分析"],
                    "weaknesses": ["待分析"],
                    "success_probability": {"reach": 0.2, "match": 0.6, "safety": 0.8},
                    "improvement_suggestions": ["请提供更详细的背景信息"],
                    "overall_assessment": "需要更多信息进行准确分析"
                }
    
    def _parse_recommendations_response(self, response_text: str) -> List[Dict[str, Any]]:
        """解析学校推荐响应"""
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            import re
            json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return []
    
    def _parse_strategy_response(self, response_text: str) -> Dict[str, Any]:
        """解析申请策略响应"""
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return {
                    "timeline": {},
                    "essay_themes": [],
                    "recommendation_letter_strategy": "",
                    "interview_preparation": [],
                    "scholarship_opportunities": []
                }
