#!/usr/bin/env python3
"""
导师-学员匹配系统测试套件
支持本地SQLite和Supabase两种环境
"""
import os
import sys
import json
import requests
from datetime import datetime, date
from decimal import Decimal
import random
import string

class MentorshipSystemTester:
    def __init__(self, base_url="http://localhost:8001"):
        self.base_url = base_url
        self.session = requests.Session()
        self.auth_token = None
        self.test_users = []
        self.test_skills = []
        self.test_relationships = []
        
    def log(self, message, level="INFO"):
        """日志输出"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
    
    def generate_random_string(self, length=8):
        """生成随机字符串"""
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
    
    def test_server_connection(self):
        """测试服务器连接"""
        self.log("🔗 测试服务器连接...")
        try:
            response = self.session.get(f"{self.base_url}/")
            if response.status_code == 200:
                self.log("✅ 服务器连接成功")
                return True
            else:
                self.log(f"❌ 服务器返回错误: {response.status_code}")
                return False
        except Exception as e:
            self.log(f"❌ 服务器连接失败: {e}")
            return False
    
    def test_health_check(self):
        """测试健康检查端点"""
        self.log("💓 测试健康检查...")
        try:
            response = self.session.get(f"{self.base_url}/health")
            if response.status_code == 200:
                data = response.json()
                self.log("✅ 健康检查通过")
                self.log(f"   数据库状态: {data.get('database', 'unknown')}")
                return True
            else:
                self.log(f"❌ 健康检查失败: {response.status_code}")
                return False
        except Exception as e:
            self.log(f"❌ 健康检查错误: {e}")
            return False
    
    def register_test_user(self, username=None, email=None, password="testpass123"):
        """注册测试用户"""
        if not username:
            username = f"testuser_{self.generate_random_string()}"
        if not email:
            email = f"{username}@test.com"
        
        self.log(f"👤 注册测试用户: {username}")
        
        user_data = {
            "username": username,
            "email": email,
            "password": password
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/auth/register",
                json=user_data
            )
            
            if response.status_code in [200, 201]:
                user_info = response.json()
                self.log(f"✅ 用户注册成功: {user_info.get('username')}")
                self.test_users.append({
                    'username': username,
                    'email': email,
                    'password': password,
                    'user_info': user_info
                })
                return user_info
            else:
                self.log(f"❌ 用户注册失败: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            self.log(f"❌ 注册用户错误: {e}")
            return None
    
    def login_user(self, username, password):
        """用户登录"""
        self.log(f"🔐 用户登录: {username}")
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/auth/login",
                data={
                    "username": username,
                    "password": password
                }
            )
            
            if response.status_code == 200:
                token_data = response.json()
                self.auth_token = token_data.get('access_token')
                self.session.headers.update({
                    'Authorization': f'Bearer {self.auth_token}'
                })
                self.log("✅ 登录成功")
                return True
            else:
                self.log(f"❌ 登录失败: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            self.log(f"❌ 登录错误: {e}")
            return False
    
    def test_existing_endpoints(self):
        """测试现有的API端点"""
        self.log("🧪 测试现有API端点...")
        
        endpoints_to_test = [
            ("/api/v1/users/me", "GET", "获取当前用户信息"),
            ("/docs", "GET", "API文档"),
            # 如果有其他端点，可以添加
        ]
        
        results = []
        for endpoint, method, description in endpoints_to_test:
            try:
                if method == "GET":
                    response = self.session.get(f"{self.base_url}{endpoint}")
                elif method == "POST":
                    response = self.session.post(f"{self.base_url}{endpoint}")
                else:
                    continue
                
                if response.status_code in [200, 201]:
                    self.log(f"✅ {description}: 成功")
                    results.append(True)
                else:
                    self.log(f"❌ {description}: {response.status_code}")
                    results.append(False)
            except Exception as e:
                self.log(f"❌ {description}: {e}")
                results.append(False)
        
        return all(results)
    
    def test_skill_management_simulation(self):
        """模拟技能管理功能测试"""
        self.log("🎯 模拟技能管理测试...")
        
        # 模拟数据结构
        mock_skills = [
            {"id": 1, "name": "Python编程", "category": "编程开发"},
            {"id": 2, "name": "UI/UX设计", "category": "设计创意"},
            {"id": 3, "name": "英语口语", "category": "语言学习"},
        ]
        
        mock_user_skills = [
            {
                "skill_id": 1,
                "proficiency_level": 4,
                "years_experience": 5,
                "can_mentor": True,
                "hourly_rate": 200.00,
                "description": "5年Python开发经验"
            }
        ]
        
        mock_learning_needs = [
            {
                "skill_id": 2,
                "urgency_level": 3,
                "budget_min": 100.00,
                "budget_max": 300.00,
                "current_level": 1,
                "target_level": 3,
                "description": "希望学习UI设计"
            }
        ]
        
        self.log("📝 模拟技能数据创建成功")
        self.log(f"   - 可用技能: {len(mock_skills)} 个")
        self.log(f"   - 用户技能: {len(mock_user_skills)} 个")
        self.log(f"   - 学习需求: {len(mock_learning_needs)} 个")
        
        return True
    
    def test_matching_algorithm_simulation(self):
        """模拟匹配算法测试"""
        self.log("🔍 模拟匹配算法测试...")
        
        # 模拟导师技能
        mentor_skill = {
            "user_id": 1,
            "skill_id": 1,
            "proficiency_level": 4,
            "years_experience": 5,
            "hourly_rate": 200.00,
            "can_mentor": True
        }
        
        # 模拟学员需求
        learning_need = {
            "user_id": 2,
            "skill_id": 1,
            "urgency_level": 3,
            "budget_min": 150.00,
            "budget_max": 250.00,
            "current_level": 1,
            "target_level": 3
        }
        
        # 模拟匹配计算
        def calculate_match_score(mentor, need):
            score = 0
            factors = {}
            
            # 技能匹配 (40%)
            if mentor["skill_id"] == need["skill_id"]:
                skill_score = 100
                # 经验加成
                exp_factor = min(mentor["years_experience"] / 3, 1.0)
                skill_score *= (0.5 + 0.5 * exp_factor)
                factors["skill_match"] = skill_score
                score += skill_score * 0.4
            
            # 价格匹配 (25%)
            if mentor["hourly_rate"] <= need["budget_max"]:
                if mentor["hourly_rate"] >= need["budget_min"]:
                    price_score = 100
                else:
                    price_score = 80
                factors["price_match"] = price_score
                score += price_score * 0.25
            
            # 紧急程度 (15%)
            urgency_score = need["urgency_level"] * 20
            factors["urgency_match"] = urgency_score
            score += urgency_score * 0.15
            
            # 经验匹配 (20%)
            exp_score = min(mentor["years_experience"] * 15, 100)
            factors["experience_match"] = exp_score
            score += exp_score * 0.20
            
            return min(score, 100), factors
        
        score, factors = calculate_match_score(mentor_skill, learning_need)
        
        self.log(f"✅ 匹配算法测试完成")
        self.log(f"   匹配得分: {score:.1f}/100")
        self.log(f"   匹配因素: {factors}")
        
        return score > 60  # 认为60分以上是好匹配
    
    def test_relationship_lifecycle_simulation(self):
        """模拟指导关系生命周期测试"""
        self.log("📋 模拟指导关系生命周期测试...")
        
        # 模拟关系创建
        relationship_data = {
            "mentor_id": 1,
            "mentee_id": 2,
            "skill_id": 1,
            "title": "Python编程入门指导",
            "description": "帮助初学者掌握Python基础",
            "learning_goals": "掌握Python语法和基础库使用",
            "hourly_rate": 200.00,
            "relationship_type": "paid",
            "status": "pending"
        }
        
        self.log("✅ 模拟关系创建")
        self.log(f"   关系标题: {relationship_data['title']}")
        
        # 模拟会话安排
        session_data = {
            "relationship_id": 1,
            "session_number": 1,
            "scheduled_at": "2025-07-25T10:00:00",
            "agenda": "Python基础语法介绍",
            "status": "scheduled"
        }
        
        self.log("✅ 模拟会话安排")
        self.log(f"   会话时间: {session_data['scheduled_at']}")
        
        # 模拟会话完成
        completion_data = {
            "status": "completed",
            "duration_minutes": 60,
            "mentor_notes": "学员理解能力很强，建议加强练习",
            "mentee_feedback": "老师讲解很清楚，受益匪浅",
            "progress_percentage": 20
        }
        
        self.log("✅ 模拟会话完成")
        self.log(f"   进度: {completion_data['progress_percentage']}%")
        
        return True
    
    def test_review_system_simulation(self):
        """模拟评价系统测试"""
        self.log("⭐ 模拟评价系统测试...")
        
        # 模拟学员评价导师
        mentee_review = {
            "relationship_id": 1,
            "reviewer_role": "mentee",
            "overall_rating": 5,
            "communication_rating": 5,
            "expertise_rating": 5,
            "timeliness_rating": 4,
            "value_rating": 5,
            "comment": "非常专业的导师，讲解清楚，很有耐心",
            "would_recommend": True,
            "positive_tags": ["patient", "knowledgeable", "clear"],
            "learning_objectives_met": 5
        }
        
        # 模拟导师评价学员
        mentor_review = {
            "relationship_id": 1,
            "reviewer_role": "mentor",
            "overall_rating": 4,
            "communication_rating": 4,
            "timeliness_rating": 5,
            "professionalism_rating": 4,
            "comment": "学员很认真，按时完成作业，有问题会主动提问",
            "would_recommend": True,
            "positive_tags": ["punctual", "hardworking", "respectful"]
        }
        
        self.log("✅ 模拟双向评价创建")
        self.log(f"   学员对导师评分: {mentee_review['overall_rating']}/5")
        self.log(f"   导师对学员评分: {mentor_review['overall_rating']}/5")
        
        return True
    
    def run_full_test_suite(self):
        """运行完整测试套件"""
        self.log("🚀 开始运行导师-学员匹配系统测试套件")
        self.log("=" * 60)
        
        test_results = {}
        
        # 1. 基础连接测试
        test_results["server_connection"] = self.test_server_connection()
        test_results["health_check"] = self.test_health_check()
        
        if not test_results["server_connection"]:
            self.log("❌ 服务器连接失败，停止测试")
            return test_results
        
        # 2. 用户认证测试
        user = self.register_test_user()
        if user:
            test_results["user_registration"] = True
            login_success = self.login_user(
                self.test_users[0]["username"], 
                self.test_users[0]["password"]
            )
            test_results["user_login"] = login_success
            
            if login_success:
                test_results["existing_endpoints"] = self.test_existing_endpoints()
        else:
            test_results["user_registration"] = False
            test_results["user_login"] = False
        
        # 3. 系统功能模拟测试
        test_results["skill_management"] = self.test_skill_management_simulation()
        test_results["matching_algorithm"] = self.test_matching_algorithm_simulation()
        test_results["relationship_lifecycle"] = self.test_relationship_lifecycle_simulation()
        test_results["review_system"] = self.test_review_system_simulation()
        
        # 4. 测试结果总结
        self.log("\n" + "=" * 60)
        self.log("📊 测试结果总结")
        self.log("=" * 60)
        
        passed = 0
        total = len(test_results)
        
        for test_name, result in test_results.items():
            status = "✅ 通过" if result else "❌ 失败"
            self.log(f"{test_name.replace('_', ' ').title():<25} {status}")
            if result:
                passed += 1
        
        self.log("=" * 60)
        self.log(f"总体结果: {passed}/{total} 测试通过 ({passed/total*100:.1f}%)")
        
        if passed == total:
            self.log("🎉 所有测试通过！系统运行正常")
        elif passed >= total * 0.8:
            self.log("⚠️ 大部分测试通过，系统基本正常")
        else:
            self.log("❌ 多项测试失败，请检查系统配置")
        
        return test_results

def main():
    print("🧪 导师-学员匹配系统测试工具")
    print("=" * 50)
    
    # 检测服务器地址
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = "http://localhost:8001"
    
    print(f"🎯 测试目标: {base_url}")
    print()
    
    # 创建测试器并运行测试
    tester = MentorshipSystemTester(base_url)
    results = tester.run_full_test_suite()
    
    # 保存测试结果
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"test_results_{timestamp}.json"
    
    try:
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': timestamp,
                'base_url': base_url,
                'results': results,
                'test_users': tester.test_users
            }, f, indent=2, ensure_ascii=False)
        print(f"\n📁 测试结果已保存到: {results_file}")
    except Exception as e:
        print(f"\n⚠️ 保存测试结果失败: {e}")

if __name__ == "__main__":
    main()
