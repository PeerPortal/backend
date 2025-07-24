"""
数据库初始化脚本 - 创建所需的表结构
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from supabase_client import supabase

def check_table_exists(table_name):
    """检查表是否存在"""
    try:
        # 尝试查询表，如果表不存在会抛出异常
        result = supabase.table(table_name).select('*').limit(1).execute()
        print(f"✅ 表 '{table_name}' 已存在")
        return True
    except Exception as e:
        error_msg = str(e)
        if 'does not exist' in error_msg:
            print(f"❌ 表 '{table_name}' 不存在")
        else:
            print(f"❌ 检查表 '{table_name}' 时出错: {e}")
        return False

def create_test_user():
    """创建测试用户"""
    try:
        # 尝试插入一个测试用户
        test_user = {
            "username": "test_setup_user",
            "password_hash": "test_hash_setup"
        }
        
        result = supabase.table('users').insert(test_user).execute()
        print("✅ 成功创建测试用户")
        return True
        
    except Exception as e:
        error_msg = str(e)
        if "duplicate key" in error_msg.lower():
            print("ℹ️  测试用户已存在")
            return True
        elif "does not exist" in error_msg:
            print("❌ users 表不存在，请在 Supabase 中手动创建")
            print("请在 Supabase SQL Editor 中执行 db_schema.sql 文件")
            return False
        else:
            print(f"❌ 创建测试用户失败: {e}")
            return False

def create_test_message():
    """创建测试消息"""
    try:
        # 首先获取现有用户
        users_result = supabase.table('users').select('id').limit(2).execute()
        
        if len(users_result.data) < 2:
            print("⚠️  需要至少2个用户才能创建测试消息")
            return True
        
        test_message = {
            "sender_id": users_result.data[0]["id"],
            "receiver_id": users_result.data[1]["id"],
            "content": "测试消息 - 数据库初始化"
        }
        
        result = supabase.table('messages').insert(test_message).execute()
        print("✅ 成功创建测试消息")
        return True
        
    except Exception as e:
        error_msg = str(e)
        if "does not exist" in error_msg:
            print("❌ messages 表不存在，请在 Supabase 中手动创建")
            return False
        else:
            print(f"❌ 创建测试消息失败: {e}")
            return False

def setup_database():
    """设置数据库"""
    print("🚀 开始数据库检查和初始化...")
    print("=" * 50)
    
    print("\n📋 检查表结构:")
    users_exists = check_table_exists('users')
    messages_exists = check_table_exists('messages')
    friends_exists = check_table_exists('friends')
    
    if not (users_exists and messages_exists and friends_exists):
        print("\n❌ 某些表不存在！")
        print("📝 请按照以下步骤手动创建表:")
        print("1. 登录 Supabase 项目")
        print("2. 进入 SQL Editor")
        print("3. 执行项目根目录下的 db_schema.sql 文件内容")
        print("4. 重新运行此脚本")
        return False
    
    print("\n✅ 所有必需的表都存在！")
    
    print("\n📝 测试数据操作:")
    user_test = create_test_user()
    
    if user_test:
        message_test = create_test_message()
        
        if user_test and message_test:
            print("\n🎉 数据库测试完成！所有功能正常")
            return True
    
    print("\n⚠️  数据库功能测试未完全通过")
    return False

def show_database_info():
    """显示数据库信息"""
    try:
        print("\n📊 数据库统计:")
        
        # 统计用户数量
        users_count = supabase.table('users').select('id', count='exact').execute()
        print(f"  👥 用户总数: {len(users_count.data)}")
        
        # 统计消息数量
        messages_count = supabase.table('messages').select('id', count='exact').execute()
        print(f"  💬 消息总数: {len(messages_count.data)}")
        
        # 显示最近的几个用户
        recent_users = supabase.table('users').select('username, created_at').order('created_at', desc=True).limit(3).execute()
        print(f"  📝 最近的用户:")
        for user in recent_users.data:
            print(f"    - {user['username']}")
            
    except Exception as e:
        print(f"❌ 获取数据库信息失败: {e}")

if __name__ == "__main__":
    success = setup_database()
    if success:
        show_database_info() 