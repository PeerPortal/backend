#!/usr/bin/env python3
"""
获取并验证Supabase表结构信息
"""
import requests
import os
from dotenv import load_dotenv
import uuid

load_dotenv()

def analyze_table_schema():
    """通过插入和查询操作来验证表结构"""
    base_url = os.getenv('SUPABASE_URL')
    api_key = os.getenv('SUPABASE_KEY')
    
    if not base_url or not api_key:
        print("❌ 错误: SUPABASE_URL 或 SUPABASE_KEY 未在 .env 文件中设置。")
        return

    headers = {
        "apikey": api_key,
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    
    table_name = 'forum_posts'
    url = f"{base_url}/rest/v1/{table_name}"

    print(f"\n🔬 对 '{table_name}' 表进行深度验证...")
    
    # 步骤 1: 尝试插入一条包含所有预期字段的测试数据
    test_post_data = {
        'title': f'Schema Test Post {uuid.uuid4()}',
        'content': 'This is a test to verify table schema.',
        'author_id': 1, # 假设ID为1的用户存在 (通常是第一个注册的用户)
        'category': 'qna',
        'tags': ['schema-test'],
        'is_anonymous': False
    }

    inserted_id = None
    try:
        print(f"  - 步骤 1: 尝试向 '{table_name}' 插入测试数据...")
        response = requests.post(url, headers=headers, json=test_post_data)
        response.raise_for_status()
        
        inserted_data = response.json()
        if isinstance(inserted_data, list) and inserted_data:
            inserted_id = inserted_data[0].get('id')
            print(f"    ✅ 插入成功！记录 ID: {inserted_id}")
            print(f"    ✅ 表中存在的字段包括: {list(inserted_data[0].keys())}")
        else:
            print(f"    🟡 插入操作未按预期返回数据: {inserted_data}")

    except requests.exceptions.HTTPError as e:
        error_info = e.response.json()
        error_message = error_info.get('message', str(error_info))
        print(f"    ❌ 插入失败! HTTP Status: {e.response.status_code}")
        if "does not exist" in error_message:
            print(f"    👉 根本原因: 表 '{table_name}' 可能不存在。")
        elif "column" in error_message and "does not exist" in error_message:
             print(f"    👉 根本原因: {error_message}")
             print(f"    👉 解决方案: 请检查您的数据库迁移脚本，确保已添加该列。")
        elif "foreign key constraint" in error_message:
             print(f"    👉 根本原因: 外键约束失败。请确保 'users' 表中存在 ID 为 1 的用户。")
        else:
             print(f"    👉 错误详情: {error_message}")

    except Exception as e:
        print(f"    ❌ 插入时发生未知异常: {str(e)}")

    # 步骤 2: 如果插入成功，立即删除测试数据以保持数据库清洁
    if inserted_id:
        try:
            print(f"  - 步骤 2: 清理测试数据 (ID: {inserted_id})...")
            delete_url = f"{url}?id=eq.{inserted_id}"
            delete_response = requests.delete(delete_url, headers=headers)
            delete_response.raise_for_status()
            print("    ✅ 清理成功。")
        except Exception as e:
            print(f"    ⚠️ 清理失败: {str(e)}。请手动删除 ID 为 {inserted_id} 的记录。")

def main():
    print("📊 Supabase 表结构深度分析")
    print("=" * 60)
    analyze_table_schema()
    print("=" * 60)

if __name__ == "__main__":
    main()
