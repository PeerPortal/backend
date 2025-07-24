"""
主测试运行器 - 运行所有测试
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
        print("请在项目根目录创建 .env 文件，包含以下内容:")
        print("SUPABASE_URL=your_supabase_url")
        print("SUPABASE_KEY=your_supabase_anon_key")
        return False
    return True

def run_api_tests():
    """运行 API 测试"""
    print("\n" + "="*60)
    print("🌐 API 接口测试")
    print("="*60)
    
    try:
        from test_api import run_api_tests
        run_api_tests()
    except Exception as e:
        print(f"❌ API 测试失败: {e}")

def run_database_tests():
    """运行数据库相关测试"""
    print("\n" + "="*60)
    print("🗄️  数据库测试")
    print("="*60)
    
    try:
        from test_supabase import supabase
        print("✅ Supabase 客户端导入成功")
    except Exception as e:
        print(f"❌ Supabase 客户端导入失败: {e}")
        return
    
    try:
        from test_table_creation import run_all_tests
        run_all_tests()
    except Exception as e:
        print(f"❌ 表操作测试失败: {e}")

async def run_websocket_tests():
    """运行 WebSocket 测试"""
    print("\n" + "="*60)
    print("🔌 WebSocket 测试")
    print("="*60)
    
    try:
        from test_ws import run_all_ws_tests
        await run_all_ws_tests()
    except Exception as e:
        print(f"❌ WebSocket 测试失败: {e}")

async def main():
    """主测试函数"""
    print("🚀 开始运行所有测试...")
    
    # 检查环境
    if not check_environment():
        print("\n❌ 环境检查失败，请配置 .env 文件后重试")
        return
    
    # 运行 API 测试
    run_api_tests()
    
    # 运行数据库测试
    run_database_tests()
    
    # 运行 WebSocket 测试
    await run_websocket_tests()
    
    print("\n" + "="*60)
    print("✨ 所有测试完成!")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main()) 