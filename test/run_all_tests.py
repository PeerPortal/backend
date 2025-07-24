"""
主测试运行器 - 针对新架构的完整测试套件
"""
import sys
import os
import asyncio
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def check_environment():
    """检查环境配置"""
    env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    if not os.path.exists(env_file):
        print("⚠️  警告: 未找到 .env 文件")
        print("请在项目根目录创建 .env 文件，参考 env_example.txt")
        return False
    return True

def run_new_api_tests():
    """运行新架构的 API 测试"""
    print("\n" + "="*60)
    print("🌐 新架构 API 测试")
    print("="*60)
    
    try:
        from test_new_api import run_all_new_api_tests
        success = run_all_new_api_tests()
        return success
    except Exception as e:
        print(f"❌ 新架构 API 测试失败: {e}")
        return False

def run_database_tests():
    """运行数据库相关测试"""
    print("\n" + "="*60)
    print("🗄️  数据库测试")
    print("="*60)
    
    try:
        from check_database import main as check_db
        check_db()
        
        from setup_database import setup_database
        setup_database()
        return True
    except Exception as e:
        print(f"❌ 数据库测试失败: {e}")
        return False

async def run_websocket_tests():
    """运行 WebSocket 测试"""
    print("\n" + "="*60)
    print("🔌 WebSocket 测试")
    print("="*60)
    
    try:
        from test_ws import run_all_ws_tests
        await run_all_ws_tests()
        return True
    except Exception as e:
        print(f"❌ WebSocket 测试失败: {e}")
        return False

async def main():
    """主测试函数"""
    print("🚀 开始运行完整测试套件...")
    print("针对新的企业级架构")
    
    # 检查环境
    if not check_environment():
        print("\n❌ 环境检查失败，请配置 .env 文件后重试")
        return False
    
    success_count = 0
    total_tests = 3
    
    # 运行新架构 API 测试
    if run_new_api_tests():
        success_count += 1
    
    # 运行数据库测试
    if run_database_tests():
        success_count += 1
    
    # 运行 WebSocket 测试
    if await run_websocket_tests():
        success_count += 1
    
    print("\n" + "="*60)
    print(f"✨ 测试完成! 成功: {success_count}/{total_tests}")
    print("="*60)
    
    if success_count == total_tests:
        print("🎉 所有测试通过!")
        return True
    else:
        print(f"⚠️  {total_tests - success_count} 个测试失败")
        return False

if __name__ == "__main__":
    asyncio.run(main()) 