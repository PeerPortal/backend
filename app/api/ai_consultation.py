"""
AI留学申请咨询API路由
提供背景分析、学校推荐、申请策略和智能对话功能
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
import uuid
from datetime import datetime

from app.services.ai_consultant import (
    AIConsultantService, UserProfile, ProfileAnalysis, 
    SchoolRecommendation, ApplicationStrategy, ConsultationSession,
    ChatMessage, MessageRole, MessageType
)
from app.core.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/v1/consultation", tags=["AI咨询"])

# 全局服务实例（在实际项目中应该通过依赖注入）
ai_service = AIConsultantService(openai_api_key="your-openai-api-key")

# 内存存储（在实际项目中应该使用数据库）
sessions_store: Dict[str, ConsultationSession] = {}

@router.post("/sessions/", summary="创建新的咨询会话")
async def create_consultation_session(
    current_user: User = Depends(get_current_user)
):
    """创建新的AI咨询会话"""
    session_id = str(uuid.uuid4())
    session = ConsultationSession(session_id=session_id)
    sessions_store[session_id] = session
    
    return {
        "session_id": session_id,
        "message": "咨询会话创建成功",
        "created_at": session.created_at
    }

@router.get("/sessions/", summary="获取用户的咨询会话列表")
async def get_user_sessions(
    current_user: User = Depends(get_current_user)
):
    """获取当前用户的所有咨询会话"""
    # 在实际实现中，应该根据用户ID从数据库查询
    user_sessions = [
        {
            "session_id": session.session_id,
            "title": f"咨询会话 - {session.created_at.strftime('%Y-%m-%d')}",
            "has_profile": session.user_profile is not None,
            "has_analysis": session.analysis is not None,
            "message_count": len(session.chat_history),
            "created_at": session.created_at,
            "updated_at": session.updated_at
        }
        for session in sessions_store.values()
    ]
    
    return {"sessions": user_sessions}

@router.get("/sessions/{session_id}", summary="获取咨询会话详情")
async def get_consultation_session(
    session_id: str,
    current_user: User = Depends(get_current_user)
):
    """获取指定咨询会话的详细信息"""
    if session_id not in sessions_store:
        raise HTTPException(status_code=404, detail="咨询会话不存在")
    
    session = sessions_store[session_id]
    return {
        "session_id": session.session_id,
        "user_profile": session.user_profile,
        "analysis": session.analysis,
        "school_recommendations": session.school_recommendations,
        "strategy": session.strategy,
        "chat_history": session.chat_history[-20:],  # 返回最近20条消息
        "created_at": session.created_at,
        "updated_at": session.updated_at
    }

@router.post("/analysis/profile", summary="提交背景信息并进行分析")
async def submit_profile_for_analysis(
    session_id: str,
    profile: UserProfile,
    current_user: User = Depends(get_current_user)
):
    """提交用户背景信息并进行AI分析"""
    if session_id not in sessions_store:
        raise HTTPException(status_code=404, detail="咨询会话不存在")
    
    session = sessions_store[session_id]
    
    try:
        # 保存用户档案
        session.user_profile = profile
        
        # 进行背景分析
        analysis = await ai_service.analyze_profile(profile)
        session.analysis = analysis
        
        # 更新时间戳
        session.updated_at = datetime.now()
        
        # 添加分析消息到聊天历史
        session.chat_history.append(ChatMessage(
            role=MessageRole.SYSTEM,
            content="已完成背景分析",
            message_type=MessageType.ANALYSIS,
            metadata={"analysis_score": analysis.competitiveness_score}
        ))
        
        return {
            "message": "背景分析完成",
            "analysis": analysis,
            "session_id": session_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")

@router.get("/analysis/{session_id}", summary="获取背景分析结果")
async def get_profile_analysis(
    session_id: str,
    current_user: User = Depends(get_current_user)
):
    """获取指定会话的背景分析结果"""
    if session_id not in sessions_store:
        raise HTTPException(status_code=404, detail="咨询会话不存在")
    
    session = sessions_store[session_id]
    
    if not session.analysis:
        raise HTTPException(status_code=404, detail="尚未进行背景分析")
    
    return {
        "session_id": session_id,
        "analysis": session.analysis,
        "profile": session.user_profile
    }

@router.post("/analysis/{session_id}/reanalyze", summary="重新分析背景")
async def reanalyze_profile(
    session_id: str,
    current_user: User = Depends(get_current_user)
):
    """基于更新的信息重新分析用户背景"""
    if session_id not in sessions_store:
        raise HTTPException(status_code=404, detail="咨询会话不存在")
    
    session = sessions_store[session_id]
    
    if not session.user_profile:
        raise HTTPException(status_code=400, detail="请先提交背景信息")
    
    try:
        # 重新分析
        analysis = await ai_service.analyze_profile(session.user_profile)
        session.analysis = analysis
        session.updated_at = datetime.now()
        
        # 添加重新分析消息
        session.chat_history.append(ChatMessage(
            role=MessageRole.SYSTEM,
            content="已重新完成背景分析",
            message_type=MessageType.ANALYSIS,
            metadata={"analysis_score": analysis.competitiveness_score}
        ))
        
        return {
            "message": "重新分析完成",
            "analysis": analysis,
            "session_id": session_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"重新分析失败: {str(e)}")

@router.get("/recommendations/{session_id}/schools", summary="获取学校推荐")
async def get_school_recommendations(
    session_id: str,
    current_user: User = Depends(get_current_user)
):
    """获取基于背景分析的学校推荐"""
    if session_id not in sessions_store:
        raise HTTPException(status_code=404, detail="咨询会话不存在")
    
    session = sessions_store[session_id]
    
    if not session.user_profile or not session.analysis:
        raise HTTPException(status_code=400, detail="请先完成背景分析")
    
    try:
        # 如果还没有推荐结果，生成推荐
        if not session.school_recommendations:
            recommendations = await ai_service.recommend_schools(
                session.user_profile, session.analysis
            )
            session.school_recommendations = recommendations
            session.updated_at = datetime.now()
            
            # 添加推荐消息
            session.chat_history.append(ChatMessage(
                role=MessageRole.SYSTEM,
                content="已生成学校推荐",
                message_type=MessageType.RECOMMENDATION,
                metadata={"school_count": len(recommendations)}
            ))
        
        # 按档次分组
        recommendations_by_tier = {
            "reach": [r for r in session.school_recommendations if r.tier == "reach"],
            "match": [r for r in session.school_recommendations if r.tier == "match"],
            "safety": [r for r in session.school_recommendations if r.tier == "safety"]
        }
        
        return {
            "session_id": session_id,
            "recommendations_by_tier": recommendations_by_tier,
            "total_count": len(session.school_recommendations),
            "analysis_summary": {
                "score": session.analysis.competitiveness_score,
                "strengths": session.analysis.strengths[:3],
                "weaknesses": session.analysis.weaknesses[:3]
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"学校推荐失败: {str(e)}")

@router.get("/recommendations/{session_id}/strategy", summary="获取申请策略")
async def get_application_strategy(
    session_id: str,
    current_user: User = Depends(get_current_user)
):
    """获取个性化的申请策略"""
    if session_id not in sessions_store:
        raise HTTPException(status_code=404, detail="咨询会话不存在")
    
    session = sessions_store[session_id]
    
    if not session.user_profile or not session.analysis:
        raise HTTPException(status_code=400, detail="请先完成背景分析")
    
    try:
        # 确保有学校推荐
        if not session.school_recommendations:
            recommendations = await ai_service.recommend_schools(
                session.user_profile, session.analysis
            )
            session.school_recommendations = recommendations
        
        # 如果还没有策略，生成策略
        if not session.strategy:
            strategy = await ai_service.generate_strategy(
                session.user_profile, session.analysis, session.school_recommendations
            )
            session.strategy = strategy
            session.updated_at = datetime.now()
            
            # 添加策略消息
            session.chat_history.append(ChatMessage(
                role=MessageRole.SYSTEM,
                content="已生成申请策略",
                message_type=MessageType.STRATEGY,
                metadata={"timeline_months": len(strategy.timeline)}
            ))
        
        return {
            "session_id": session_id,
            "strategy": session.strategy,
            "target_info": {
                "degree": session.user_profile.target_degree,
                "major": session.user_profile.target_major,
                "year": session.user_profile.target_year
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"策略生成失败: {str(e)}")

@router.post("/chat/{session_id}/message", summary="发送聊天消息")
async def send_chat_message(
    session_id: str,
    message: str,
    current_user: User = Depends(get_current_user)
):
    """与AI助手进行对话咨询"""
    if session_id not in sessions_store:
        raise HTTPException(status_code=404, detail="咨询会话不存在")
    
    session = sessions_store[session_id]
    
    try:
        # 调用AI对话服务
        ai_response = await ai_service.chat_consultation(session, message)
        
        # 更新时间戳
        session.updated_at = datetime.now()
        
        return {
            "session_id": session_id,
            "user_message": message,
            "ai_response": ai_response,
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"对话失败: {str(e)}")

@router.get("/chat/{session_id}/history", summary="获取聊天历史")
async def get_chat_history(
    session_id: str,
    limit: int = 50,
    current_user: User = Depends(get_current_user)
):
    """获取指定会话的聊天历史记录"""
    if session_id not in sessions_store:
        raise HTTPException(status_code=404, detail="咨询会话不存在")
    
    session = sessions_store[session_id]
    
    # 返回最近的聊天记录
    chat_history = session.chat_history[-limit:] if session.chat_history else []
    
    return {
        "session_id": session_id,
        "chat_history": chat_history,
        "total_messages": len(session.chat_history),
        "returned_count": len(chat_history)
    }

@router.post("/recommendations/{session_id}/feedback", summary="提供推荐反馈")
async def provide_recommendation_feedback(
    session_id: str,
    feedback: Dict[str, Any],
    current_user: User = Depends(get_current_user)
):
    """用户对推荐结果提供反馈"""
    if session_id not in sessions_store:
        raise HTTPException(status_code=404, detail="咨询会话不存在")
    
    session = sessions_store[session_id]
    
    # 保存反馈到聊天历史
    feedback_message = f"用户反馈: {feedback.get('comment', '满意')}"
    session.chat_history.append(ChatMessage(
        role=MessageRole.USER,
        content=feedback_message,
        metadata={"feedback_type": "recommendation", "rating": feedback.get("rating")}
    ))
    
    session.updated_at = datetime.now()
    
    return {
        "message": "感谢您的反馈",
        "session_id": session_id,
        "feedback_received": feedback
    }

# 特殊功能端点
@router.get("/demo/sample-profile", summary="获取示例档案")
async def get_sample_profile():
    """获取示例用户档案用于演示"""
    from app.services.ai_consultant import AcademicBackground, TestScores, ResearchExperience, WorkExperience
    
    sample_profile = UserProfile(
        name="张小明",
        target_degree="master",
        target_major="Computer Science",
        target_year="2025Fall",
        
        academic_background=AcademicBackground(
            undergraduate_school="北京理工大学",
            undergraduate_major="计算机科学与技术",
            gpa=3.7,
            school_ranking=30,
            core_courses=["数据结构", "算法设计", "机器学习", "数据库系统"]
        ),
        
        test_scores=TestScores(
            gre_total=325,
            gre_verbal=155,
            gre_quantitative=170,
            gre_writing=4.0,
            toefl_total=105
        ),
        
        research_experiences=[
            ResearchExperience(
                title="深度学习在图像识别中的应用研究",
                institution="北京理工大学AI实验室",
                duration="2023.03-2024.03",
                description="参与导师的国家自然科学基金项目，负责数据预处理和模型训练",
                advisor="李教授",
                publications=["ICCV 2024 Workshop论文一篇（第二作者）"]
            )
        ],
        
        work_experiences=[
            WorkExperience(
                title="算法工程师实习生",
                company="字节跳动",
                duration="2023.07-2023.09",
                description="参与推荐系统优化项目，提升CTR 15%",
                skills_gained=["推荐算法", "大数据处理", "Python", "TensorFlow"]
            )
        ],
        
        awards=["ACM-ICPC亚洲区域赛银奖", "国家奖学金"],
        extracurriculars=["学生会技术部部长", "开源项目贡献者"]
    )
    
    return {
        "sample_profile": sample_profile,
        "message": "这是一个示例档案，您可以参考格式填写自己的信息"
    }

@router.get("/demo/quick-analysis", summary="快速分析演示")
async def quick_analysis_demo():
    """快速分析演示，不需要真实调用LLM API"""
    demo_analysis = ProfileAnalysis(
        competitiveness_score=7.5,
        strengths=[
            "GPA和标准化考试成绩优秀",
            "有顶会论文发表经历", 
            "知名互联网公司实习背景",
            "竞赛获奖证明算法能力",
            "本科院校知名度较高"
        ],
        weaknesses=[
            "研究经历相对较短",
            "TOEFL成绩可以进一步提升",
            "缺乏海外交流经历"
        ],
        success_probability={
            "reach": 0.3,
            "match": 0.75,
            "safety": 0.95
        },
        improvement_suggestions=[
            "考虑刷高TOEFL到110+",
            "增加研究项目的深度和独立性",
            "寻找暑期海外交流机会",
            "准备更多技术项目展示编程能力"
        ],
        overall_assessment="整体背景较为优秀，在CS硕士申请中具有较强竞争力。GPA和GRE成绩都很不错，有论文发表和大厂实习经历是很大的加分项。建议重点提升语言成绩和研究深度。"
    )
    
    return {
        "analysis": demo_analysis,
        "message": "这是基于示例档案的分析结果演示"
    }
