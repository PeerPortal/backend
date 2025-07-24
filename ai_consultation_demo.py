#!/usr/bin/env python3
"""
留学申请AI咨询系统演示脚本
展示系统核心功能和工作流程
"""
import asyncio
import json
import uuid
from datetime import datetime
from typing import Dict, Any, List

# 模拟AI服务（用于演示，实际使用时需要真实的OpenAI API）
class MockAIService:
    """模拟AI服务用于演示"""
    
    async def analyze_profile(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """模拟背景分析"""
        gpa = profile.get("academic_background", {}).get("gpa", 3.0)
        gre = profile.get("test_scores", {}).get("gre_total", 300)
        
        # 基于GPA和GRE计算竞争力评分
        score = min(10, (gpa - 2.0) * 2.5 + (gre - 280) / 10)
        
        return {
            "competitiveness_score": round(score, 1),
            "strengths": [
                f"GPA {gpa} 表现优秀" if gpa >= 3.5 else f"GPA {gpa} 有提升空间",
                f"GRE {gre} 成绩良好" if gre >= 320 else f"GRE {gre} 建议再次备考",
                "有相关专业背景",
                "申请目标明确"
            ],
            "weaknesses": [
                "语言成绩可以进一步提升",
                "实习经历相对较少",
                "研究经历需要加强"
            ],
            "success_probability": {
                "reach": min(0.5, score / 20),
                "match": min(0.8, score / 12),
                "safety": min(0.95, score / 8)
            },
            "improvement_suggestions": [
                "建议提升TOEFL/IELTS成绩到目标分数",
                "寻找相关领域的实习或研究机会",
                "准备有说服力的个人陈述",
                "提前联系推荐信老师"
            ],
            "overall_assessment": f"基于您的背景，竞争力评分为{score:.1}/10。建议在保持现有优势的基础上，重点提升薄弱环节。"
        }
    
    async def recommend_schools(self, profile: Dict[str, Any], analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """模拟学校推荐"""
        major = profile.get("target_major", "Computer Science")
        score = analysis.get("competitiveness_score", 5.0)
        
        # 根据竞争力评分推荐不同档次的学校
        schools = {
            "reach": [
                {"name": "Massachusetts Institute of Technology", "ranking": 1},
                {"name": "Stanford University", "ranking": 2},
                {"name": "Harvard University", "ranking": 3},
                {"name": "California Institute of Technology", "ranking": 4},
                {"name": "University of Chicago", "ranking": 6}
            ],
            "match": [
                {"name": "University of California, Berkeley", "ranking": 22},
                {"name": "Carnegie Mellon University", "ranking": 25},
                {"name": "University of Michigan", "ranking": 24},
                {"name": "New York University", "ranking": 30},
                {"name": "Boston University", "ranking": 41},
                {"name": "University of Rochester", "ranking": 34},
                {"name": "Case Western Reserve University", "ranking": 44}
            ],
            "safety": [
                {"name": "University of California, Davis", "ranking": 38},
                {"name": "University of California, San Diego", "ranking": 34},
                {"name": "Pennsylvania State University", "ranking": 63}
            ]
        }
        
        recommendations = []
        
        for tier, school_list in schools.items():
            for school in school_list:
                prob = analysis["success_probability"][tier]
                recommendations.append({
                    "name": school["name"],
                    "ranking": school["ranking"],
                    "tier": tier,
                    "recommendation_reason": f"基于您的背景，这所学校的{major}项目很适合您的申请目标",
                    "admission_requirements": {
                        "min_gpa": 3.5 if tier == "reach" else 3.2 if tier == "match" else 3.0,
                        "min_gre": 320 if tier == "reach" else 310 if tier == "match" else 300,
                        "min_toefl": 100 if tier == "reach" else 95 if tier == "match" else 90
                    },
                    "difficulty_assessment": tier,
                    "special_advantages": [
                        "知名度高" if tier == "reach" else "性价比好",
                        "就业前景优秀",
                        "师资力量强"
                    ],
                    "success_probability": prob
                })
        
        return recommendations
    
    async def generate_strategy(self, profile: Dict[str, Any], analysis: Dict[str, Any], schools: List[Dict[str, Any]]) -> Dict[str, Any]:
        """模拟申请策略生成"""
        target_year = profile.get("target_year", "2025Fall")
        
        return {
            "timeline": {
                "2024年8月": [
                    "开始准备申请材料",
                    "制定学校申请清单",
                    "联系推荐信老师"
                ],
                "2024年9月": [
                    "完成个人陈述初稿",
                    "准备简历和成绩单",
                    "开始网申注册"
                ],
                "2024年10月": [
                    "完善申请文书",
                    "提交早期申请",
                    "准备面试"
                ],
                "2024年11月": [
                    "提交常规申请",
                    "跟进推荐信",
                    "参加面试"
                ],
                "2024年12月": [
                    "完成所有申请提交",
                    "跟进申请状态",
                    "准备奖学金申请"
                ]
            },
            "essay_themes": [
                "学术兴趣和研究方向",
                "个人成长和挑战经历",
                "未来职业规划和目标",
                "为什么选择这个项目"
            ],
            "recommendation_letter_strategy": "建议选择3位推荐人：1位学术导师（重点突出研究能力），1位实习主管（强调实践经验），1位任课老师（证明学术表现）",
            "interview_preparation": [
                "准备常见问题回答",
                "了解项目详细信息",
                "练习英语口语表达",
                "准备技术问题解答"
            ],
            "scholarship_opportunities": [
                "Merit-based奖学金",
                "Research Assistantship",
                "Teaching Assistantship",
                "外部奖学金项目"
            ]
        }
    
    async def chat_response(self, message: str, context: Dict[str, Any]) -> str:
        """模拟聊天回复"""
        # 简单的关键词匹配回复
        message_lower = message.lower()
        
        if "gpa" in message_lower:
            return "GPA是申请中最重要的指标之一。一般来说，申请Top 20学校建议GPA在3.7以上，Top 50学校建议3.5以上。如果GPA不够理想，可以通过其他方面来弥补。"
        elif "gre" in message_lower:
            return "GRE成绩对于理工科申请很重要。Top 20学校通常要求320+，Top 50学校要求310+。数学部分对中国学生相对容易，重点是提升语文部分。"
        elif "托福" in message_lower or "toefl" in message_lower:
            return "TOEFL成绩是国际学生的必要条件。Top学校通常要求100+，一般学校要求90+。建议尽早考出目标分数，为申请留出充足时间。"
        elif "文书" in message_lower or "ps" in message_lower:
            return "个人陈述是展现个人特色的重要材料。要突出学术兴趣、相关经历和未来规划。建议多次修改，请有经验的人提意见。"
        elif "推荐信" in message_lower:
            return "推荐信最好选择了解你的老师或主管。建议提前2-3个月联系，提供详细的个人信息和申请目标，帮助推荐人写出有针对性的推荐信。"
        elif "面试" in message_lower:
            return "面试主要考察英语表达能力、专业知识和个人品格。要提前了解项目信息，准备常见问题，练习清晰表达自己的观点。"
        else:
            return "感谢您的问题！我会尽力为您提供专业的建议。如果您有具体的申请问题，请告诉我更多细节，我可以给出更有针对性的建议。"

class AIConsultationDemo:
    """AI咨询系统演示"""
    
    def __init__(self):
        self.ai_service = MockAIService()
        self.session_id = str(uuid.uuid4())
        self.chat_history = []
    
    def print_header(self, title: str):
        """打印标题"""
        print(f"\n{'='*60}")
        print(f" {title}")
        print(f"{'='*60}")
    
    def print_section(self, title: str):
        """打印章节标题"""
        print(f"\n{'-'*40}")
        print(f" {title}")
        print(f"{'-'*40}")
    
    async def demo_profile_analysis(self):
        """演示背景分析功能"""
        self.print_header("🎯 背景分析演示")
        
        # 示例用户档案
        sample_profile = {
            "name": "张小明",
            "target_degree": "master",
            "target_major": "Computer Science", 
            "target_year": "2025Fall",
            "academic_background": {
                "undergraduate_school": "北京理工大学",
                "undergraduate_major": "计算机科学与技术",
                "gpa": 3.7,
                "school_ranking": 30,
                "core_courses": ["数据结构", "算法设计", "机器学习", "数据库系统"]
            },
            "test_scores": {
                "gre_total": 325,
                "gre_verbal": 155,
                "gre_quantitative": 170,
                "gre_writing": 4.0,
                "toefl_total": 105
            },
            "research_experiences": [
                {
                    "title": "深度学习在图像识别中的应用研究",
                    "institution": "北京理工大学AI实验室",
                    "duration": "2023.03-2024.03",
                    "description": "参与导师的国家自然科学基金项目",
                    "publications": ["ICCV 2024 Workshop论文一篇（第二作者）"]
                }
            ],
            "work_experiences": [
                {
                    "title": "算法工程师实习生",
                    "company": "字节跳动",
                    "duration": "2023.07-2023.09",
                    "description": "参与推荐系统优化项目，提升CTR 15%"
                }
            ],
            "awards": ["ACM-ICPC亚洲区域赛银奖", "国家奖学金"],
            "extracurriculars": ["学生会技术部部长", "开源项目贡献者"]
        }
        
        print("📋 用户档案信息:")
        print(f"姓名: {sample_profile['name']}")
        print(f"目标: {sample_profile['target_year']} {sample_profile['target_degree']} in {sample_profile['target_major']}")
        print(f"本科: {sample_profile['academic_background']['undergraduate_school']} - {sample_profile['academic_background']['undergraduate_major']}")
        print(f"GPA: {sample_profile['academic_background']['gpa']}/4.0")
        print(f"考试成绩: GRE {sample_profile['test_scores']['gre_total']}, TOEFL {sample_profile['test_scores']['toefl_total']}")
        
        print("\n🔄 正在进行AI背景分析...")
        await asyncio.sleep(1)  # 模拟处理时间
        
        analysis = await self.ai_service.analyze_profile(sample_profile)
        
        self.print_section("📊 分析结果")
        print(f"竞争力评分: {analysis['competitiveness_score']}/10")
        
        print(f"\n✅ 主要优势:")
        for strength in analysis['strengths']:
            print(f"  • {strength}")
        
        print(f"\n⚠️ 需要改进:")
        for weakness in analysis['weaknesses']:
            print(f"  • {weakness}")
        
        print(f"\n📈 录取概率评估:")
        probs = analysis['success_probability']
        print(f"  冲刺档: {probs['reach']*100:.0f}%")
        print(f"  匹配档: {probs['match']*100:.0f}%") 
        print(f"  保底档: {probs['safety']*100:.0f}%")
        
        print(f"\n💡 改进建议:")
        for suggestion in analysis['improvement_suggestions']:
            print(f"  • {suggestion}")
        
        print(f"\n📝 总体评估:")
        print(f"  {analysis['overall_assessment']}")
        
        return sample_profile, analysis
    
    async def demo_school_recommendations(self, profile: Dict[str, Any], analysis: Dict[str, Any]):
        """演示学校推荐功能"""
        self.print_header("🏫 学校推荐演示")
        
        print("🔄 正在生成个性化学校推荐...")
        await asyncio.sleep(1)
        
        recommendations = await self.ai_service.recommend_schools(profile, analysis)
        
        # 按档次分组显示
        by_tier = {}
        for rec in recommendations:
            tier = rec['tier']
            if tier not in by_tier:
                by_tier[tier] = []
            by_tier[tier].append(rec)
        
        tier_names = {
            'reach': '🎯 冲刺档 (录取难度较高)',
            'match': '🎯 匹配档 (背景较为匹配)', 
            'safety': '🎯 保底档 (录取概率较高)'
        }
        
        for tier in ['reach', 'match', 'safety']:
            if tier in by_tier:
                self.print_section(f"{tier_names[tier]} - {len(by_tier[tier])}所学校")
                
                for i, school in enumerate(by_tier[tier][:3], 1):  # 只显示前3所
                    print(f"\n{i}. {school['name']} (排名: #{school['ranking']})")
                    print(f"   推荐理由: {school['recommendation_reason']}")
                    print(f"   录取概率: {school['success_probability']*100:.0f}%")
                    print(f"   基本要求: GPA {school['admission_requirements']['min_gpa']}+, "
                          f"GRE {school['admission_requirements']['min_gre']}+, "
                          f"TOEFL {school['admission_requirements']['min_toefl']}+")
                
                if len(by_tier[tier]) > 3:
                    print(f"   ... 还有 {len(by_tier[tier]) - 3} 所其他学校")
        
        print(f"\n📌 推荐总结:")
        print(f"  • 总计推荐 {len(recommendations)} 所学校")
        print(f"  • 建议重点关注匹配档学校，同时申请部分冲刺档和保底档")
        print(f"  • 可根据个人偏好（地理位置、专业排名、费用等）进一步筛选")
        
        return recommendations
    
    async def demo_application_strategy(self, profile: Dict[str, Any], analysis: Dict[str, Any], recommendations: List[Dict[str, Any]]):
        """演示申请策略功能"""
        self.print_header("📅 申请策略演示")
        
        print("🔄 正在制定个性化申请策略...")
        await asyncio.sleep(1)
        
        strategy = await self.ai_service.generate_strategy(profile, analysis, recommendations)
        
        self.print_section("⏰ 申请时间线")
        for month, tasks in strategy['timeline'].items():
            print(f"\n{month}:")
            for task in tasks:
                print(f"  • {task}")
        
        self.print_section("📝 文书主题建议")
        for i, theme in enumerate(strategy['essay_themes'], 1):
            print(f"{i}. {theme}")
        
        self.print_section("📨 推荐信策略")
        print(f"  {strategy['recommendation_letter_strategy']}")
        
        self.print_section("🎤 面试准备要点")
        for point in strategy['interview_preparation']:
            print(f"  • {point}")
        
        self.print_section("💰 奖学金机会")
        for opportunity in strategy['scholarship_opportunities']:
            print(f"  • {opportunity}")
        
        return strategy
    
    async def demo_chat_consultation(self, profile: Dict[str, Any], analysis: Dict[str, Any]):
        """演示智能对话咨询功能"""
        self.print_header("💬 智能对话咨询演示")
        
        print("🤖 小申: 你好！我是你的留学申请AI助手。基于你的背景分析，我可以回答各种申请相关问题。")
        
        # 模拟用户问题
        sample_questions = [
            "我的GPA 3.7算高吗？",
            "GRE 325分能申请什么学校？",
            "如何写好个人陈述？",
            "推荐信应该找谁写？",
            "面试时要注意什么？"
        ]
        
        context = {
            "profile": profile,
            "analysis": analysis
        }
        
        for question in sample_questions:
            print(f"\n👤 用户: {question}")
            
            # 模拟思考时间
            print("🤖 小申: [思考中...]")
            await asyncio.sleep(0.5)
            
            response = await self.ai_service.chat_response(question, context)
            print(f"🤖 小申: {response}")
        
        print(f"\n💡 对话特点:")
        print(f"  • 基于用户档案提供个性化建议")
        print(f"  • 支持多轮对话和上下文理解")
        print(f"  • 涵盖申请全流程的各类问题")
        print(f"  • 友好的对话界面和实时响应")
    
    async def demo_full_workflow(self):
        """演示完整的咨询工作流程"""
        self.print_header("🚀 AI留学申请咨询系统完整演示")
        
        print("欢迎使用AI留学申请咨询系统！")
        print("本系统提供智能背景分析、个性化学校推荐、申请策略制定和实时对话咨询服务。")
        
        input("\n按 Enter 键开始演示...")
        
        # 1. 背景分析演示
        profile, analysis = await self.demo_profile_analysis()
        input("\n按 Enter 键继续学校推荐演示...")
        
        # 2. 学校推荐演示
        recommendations = await self.demo_school_recommendations(profile, analysis)
        input("\n按 Enter 键继续申请策略演示...")
        
        # 3. 申请策略演示
        strategy = await self.demo_application_strategy(profile, analysis, recommendations)
        input("\n按 Enter 键继续智能对话演示...")
        
        # 4. 智能对话演示
        await self.demo_chat_consultation(profile, analysis)
        
        self.print_header("🎉 演示完成")
        print("感谢体验AI留学申请咨询系统！")
        print("\n系统特色:")
        print("✅ 智能背景分析 - 多维度评估申请竞争力")
        print("✅ 个性化推荐 - 基于背景匹配合适学校")  
        print("✅ 申请策略制定 - 详细时间规划和准备指导")
        print("✅ 实时智能对话 - 随时解答申请疑问")
        print("✅ 数据驱动决策 - 基于大量申请数据优化建议")
        
        print("\n📞 如需了解更多信息或开始正式咨询，请联系我们的团队！")

async def main():
    """主函数"""
    demo = AIConsultationDemo()
    await demo.demo_full_workflow()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n演示已停止。感谢您的体验！")
    except Exception as e:
        print(f"\n演示过程中出现错误: {e}")
        print("请联系技术支持团队。")
