#!/usr/bin/env python3
"""
Supabase 数据库推送工具
"""
import os
import sys
from pathlib import Path

def read_sql_file(file_path):
    """读取 SQL 文件内容"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"❌ 文件不存在: {file_path}")
        return None
    except Exception as e:
        print(f"❌ 读取文件失败: {e}")
        return None

def split_sql_statements(sql_content):
    """将 SQL 内容分割成单独的语句"""
    # 简单的分割方法，按分号分割
    statements = []
    current_statement = []
    
    for line in sql_content.split('\n'):
        line = line.strip()
        
        # 跳过注释和空行
        if not line or line.startswith('--') or line.startswith('/*'):
            continue
            
        current_statement.append(line)
        
        # 如果行以分号结尾，表示语句结束
        if line.endswith(';'):
            statement = ' '.join(current_statement).strip()
            if statement and not statement.startswith('COMMENT'):
                statements.append(statement)
            current_statement = []
    
    return statements

def generate_supabase_migration():
    """生成 Supabase 迁移文件"""
    
    print("🔧 Supabase 数据库推送工具")
    print("=" * 50)
    
    # 读取现有的数据库架构
    schema_files = [
        'db_schema.sql',
        'mentorship_schema.sql'
    ]
    
    all_sql = []
    
    for file_name in schema_files:
        if os.path.exists(file_name):
            print(f"📖 读取文件: {file_name}")
            content = read_sql_file(file_name)
            if content:
                all_sql.append(f"-- ==================== {file_name} ====================")
                all_sql.append(content)
                all_sql.append("")
        else:
            print(f"⚠️ 文件不存在，跳过: {file_name}")
    
    if not all_sql:
        print("❌ 没有找到可用的 SQL 文件")
        return
    
    # 生成完整的迁移脚本
    migration_content = '\n'.join(all_sql)
    
    # 保存到迁移文件
    migration_file = 'supabase_migration.sql'
    try:
        with open(migration_file, 'w', encoding='utf-8') as f:
            f.write(migration_content)
        print(f"✅ 迁移文件已生成: {migration_file}")
    except Exception as e:
        print(f"❌ 生成迁移文件失败: {e}")
        return
    
    # 生成分步执行脚本
    statements = split_sql_statements(migration_content)
    
    step_by_step_file = 'supabase_migration_steps.sql'
    try:
        with open(step_by_step_file, 'w', encoding='utf-8') as f:
            for i, statement in enumerate(statements, 1):
                f.write(f"-- Step {i}\n")
                f.write(f"{statement}\n\n")
        print(f"✅ 分步执行文件已生成: {step_by_step_file}")
    except Exception as e:
        print(f"❌ 生成分步文件失败: {e}")
    
    print("\n📋 接下来的步骤:")
    print("1. 登录 Supabase Dashboard")
    print("2. 选择你的项目")
    print("3. 进入 SQL Editor")
    print("4. 复制 supabase_migration.sql 的内容")
    print("5. 粘贴到 SQL Editor 并执行")
    print("\n💡 如果遇到错误，可以使用 supabase_migration_steps.sql 逐步执行")

def test_connection():
    """测试 Supabase 连接"""
    try:
        import psycopg2
        from dotenv import load_dotenv
        
        load_dotenv()
        
        # 构建连接字符串
        supabase_url = os.getenv('SUPABASE_URL')
        database_url = os.getenv('DATABASE_URL')
        
        if not database_url:
            print("❌ DATABASE_URL 未配置")
            return False
        
        print("🔗 测试 Supabase 连接...")
        
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # 测试查询
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        
        print(f"✅ 连接成功!")
        print(f"PostgreSQL 版本: {version[0][:50]}...")
        
        # 检查现有表
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name;
        """)
        
        tables = cursor.fetchall()
        print(f"\n📊 当前数据库中的表 ({len(tables)} 个):")
        for table in tables:
            print(f"  - {table[0]}")
        
        cursor.close()
        conn.close()
        return True
        
    except ImportError:
        print("❌ 缺少依赖: pip install psycopg2-binary")
        return False
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return False

def push_to_supabase():
    """直接推送到 Supabase（如果连接可用）"""
    if not test_connection():
        print("\n💡 无法直接推送，请使用手动方式:")
        print("1. 使用 generate_supabase_migration() 生成迁移文件")
        print("2. 在 Supabase Dashboard 中手动执行")
        return
    
    try:
        import psycopg2
        from dotenv import load_dotenv
        
        load_dotenv()
        database_url = os.getenv('DATABASE_URL')
        
        # 读取迁移文件
        if not os.path.exists('mentorship_schema.sql'):
            print("❌ 迁移文件不存在，请先运行 generate_supabase_migration()")
            return
        
        migration_content = read_sql_file('mentorship_schema.sql')
        if not migration_content:
            return
        
        print("🚀 开始推送到 Supabase...")
        
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        try:
            # 执行迁移
            cursor.execute(migration_content)
            conn.commit()
            print("✅ 迁移执行成功!")
            
            # 验证结果
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name LIKE '%skill%' OR table_name LIKE '%mentor%'
                ORDER BY table_name;
            """)
            
            new_tables = cursor.fetchall()
            print(f"\n📊 新增的表:")
            for table in new_tables:
                print(f"  - {table[0]}")
                
        except Exception as e:
            conn.rollback()
            print(f"❌ 迁移执行失败: {e}")
            print("💡 建议使用手动方式执行")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ 推送失败: {e}")

def main():
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "test":
            test_connection()
        elif command == "push":
            push_to_supabase()
        elif command == "generate":
            generate_supabase_migration()
        else:
            print("可用命令: test, push, generate")
    else:
        print("请选择操作:")
        print("1. 测试连接 (test)")
        print("2. 生成迁移文件 (generate)")
        print("3. 直接推送 (push)")
        
        choice = input("输入选择 (1/2/3): ").strip()
        
        if choice == "1":
            test_connection()
        elif choice == "2":
            generate_supabase_migration()
        elif choice == "3":
            push_to_supabase()
        else:
            print("无效选择")

if __name__ == "__main__":
    main()
