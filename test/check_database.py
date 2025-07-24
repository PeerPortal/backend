"""
简单的数据库连接和状态检查脚本
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from supabase_client import supabase

def main():
    print("🔍 Supabase 连接检查")
    print("=" * 40)
    
    try:
        # 检查连接状态
        print("📡 测试 Supabase 连接...")
        
        # 列出可用的表
        print("📋 检查可用表:")
        tables_to_check = ['users', 'messages', 'friends']
        
        for table in tables_to_check:
            try:
                result = supabase.table(table).select('*').limit(1).execute()
                print(f"  ✅ {table} 表存在")
            except Exception as e:
                if 'does not exist' in str(e):
                    print(f"  ❌ {table} 表不存在")
                else:
                    print(f"  ⚠️  {table} 表检查出错: {str(e)[:50]}...")
        
        print("\n📝 建议:")
        print("如果表不存在，请在 Supabase SQL Editor 中执行以下 SQL:")
        print("-" * 40)
        
        # 读取并显示 schema 文件内容
        schema_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'db_schema.sql')
        if os.path.exists(schema_file):
            with open(schema_file, 'r', encoding='utf-8') as f:
                schema_content = f.read()
            print(schema_content)
        else:
            print("❌ 找不到 db_schema.sql 文件")
        
    except Exception as e:
        print(f"❌ 连接失败: {e}")

if __name__ == "__main__":
    main() 