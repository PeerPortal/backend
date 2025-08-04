import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from typing import Dict, Any, List
import random
import string

# 将项目根目录添加到 aync Path
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.main import app

# 共享状态，用于在测试用例之间传递数据
shared_data: Dict[str, Any] = {}

def random_string(length=10):
    """Generate a random string of fixed length."""
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

@pytest.fixture(scope="module")
async def client():
    """提供一个可复用的异步HTTP客户端"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

async def register_and_login(client: AsyncClient, user_details: Dict[str, str], user_role: str = "student") -> Dict[str, Any]:
    """辅助函数：注册并登录用户，返回认证头和用户ID"""
    # 注册
    register_payload = {**user_details, "role": user_role}
    reg_res = await client.post("/api/v1/auth/register", json=register_payload)
    assert reg_res.status_code == 201, f"注册失败: {reg_res.text}"
    
    # 登录
    login_payload = {"username": user_details["username"], "password": user_details["password"]}
    login_res = await client.post("/api/v1/auth/login", data=login_payload)
    
    assert login_res.status_code == 200, f"登录失败: {login_res.text}"
    token_data = login_res.json()
    
    # 获取用户信息
    headers = {"Authorization": f"Bearer {token_data['access_token']}"}
    user_res = await client.get("/api/v1/users/me", headers=headers)
    assert user_res.status_code == 200, f"获取用户信息失败: {user_res.text}"
    user_info = user_res.json()
    
    return {
        "headers": headers,
        "user_id": user_info["id"],
        "access_token": token_data["access_token"]
    }

@pytest.mark.asyncio
@pytest.mark.dependency()
async def test_register_and_login_users(client: AsyncClient):
    """测试：注册并登录两个用户，为后续测试做准备"""
    user_a_username = f"testuser_a_{random_string()}"
    user_b_username = f"testuser_b_{random_string()}"
    
    shared_data["user_a"] = {
        "username": user_a_username,
        "email": f"{user_a_username}@example.com",
        "password": "testpassword"
    }
    shared_data["user_b"] = {
        "username": user_b_username,
        "email": f"{user_b_username}@example.com",
        "password": "testpassword"
    }
    
    user_a_auth = await register_and_login(client, shared_data["user_a"], "student")
    user_b_auth = await register_and_login(client, shared_data["user_b"], "mentor")
    
    shared_data["user_a"]["auth"] = user_a_auth
    shared_data["user_b"]["auth"] = user_b_auth
    
    assert "headers" in user_a_auth
    assert "headers" in user_b_auth
    print(f"用户A ID: {user_a_auth['user_id']}, 用户B ID: {user_b_auth['user_id']}")

@pytest.mark.asyncio
@pytest.mark.dependency(depends=["test_register_and_login_users"])
async def test_send_first_message(client: AsyncClient):
    """测试：用户A向用户B发送第一条消息"""
    sender_auth = shared_data["user_a"]["auth"]
    recipient_id = shared_data["user_b"]["auth"]["user_id"]
    
    message_payload = {
        "recipient_id": recipient_id,
        "content": "你好，导师！这是我的第一条消息。",
        "message_type": "text"
    }
    
    res = await client.post("/api/v1/messages", json=message_payload, headers=sender_auth["headers"])
    
    assert res.status_code == 201, f"发送消息失败: {res.text}"
    message = res.json()
    
    assert message["sender_id"] == sender_auth["user_id"]
    assert message["recipient_id"] == recipient_id
    assert message["content"] == "你好，导师！这是我的第一条消息。"
    
    shared_data["conversation_id"] = message["conversation_id"]
    shared_data["last_message_id"] = message["id"]
    print(f"消息发送成功，对话ID: {message['conversation_id']}")

@pytest.mark.asyncio
@pytest.mark.dependency(depends=["test_send_first_message"])
async def test_get_conversations(client: AsyncClient):
    """测试：获取用户的对话列表"""
    # 检查用户A的对话列表
    user_a_headers = shared_data["user_a"]["auth"]["headers"]
    res_a = await client.get("/api/v1/messages/conversations", headers=user_a_headers)
    
    assert res_a.status_code == 200
    convos_a: List[Dict[str, Any]] = res_a.json()
    assert len(convos_a) > 0
    
    convo = convos_a[0]
    assert convo["id"] == shared_data["conversation_id"]
    assert convo["other_user"]["id"] == shared_data["user_b"]["auth"]["user_id"]
    assert "你好，导师！" in convo["last_message"]
    assert convo["unread_count"] == 0
    
    # 检查用户B的对话列表
    user_b_headers = shared_data["user_b"]["auth"]["headers"]
    res_b = await client.get("/api/v1/messages/conversations", headers=user_b_headers)
    
    assert res_b.status_code == 200
    convos_b: List[Dict[str, Any]] = res_b.json()
    assert len(convos_b) > 0
    
    convo_b = convos_b[0]
    assert convo_b["id"] == shared_data["conversation_id"]
    assert convo_b["other_user"]["id"] == shared_data["user_a"]["auth"]["user_id"]
    assert "你好，导师！" in convo_b["last_message"]
    assert convo_b["unread_count"] >= 1
    
    print("对话列表获取成功")

@pytest.mark.asyncio
@pytest.mark.dependency(depends=["test_send_first_message"])
async def test_get_conversation_messages(client: AsyncClient):
    """测试：获取特定对话的消息"""
    user_a_headers = shared_data["user_a"]["auth"]["headers"]
    conversation_id = shared_data["conversation_id"]
    
    res = await client.get(f"/api/v1/messages/conversations/{conversation_id}", headers=user_a_headers)
    
    assert res.status_code == 200
    messages: List[Dict[str, Any]] = res.json()
    assert len(messages) > 0
    
    last_message = messages[0]
    assert last_message["id"] == shared_data["last_message_id"]
    assert last_message["content"] == "你好，导师！这是我的第一条消息。"
    
    print("对话消息获取成功")

@pytest.mark.asyncio
@pytest.mark.dependency(depends=["test_get_conversation_messages"])
async def test_mark_message_as_read(client: AsyncClient):
    """测试：用户B将消息标记为已读"""
    user_b_headers = shared_data["user_b"]["auth"]["headers"]
    message_id = shared_data["last_message_id"]
    
    res = await client.put(f"/api/v1/messages/{message_id}/read", headers=user_b_headers)
    
    assert res.status_code == 200
    assert res.json()["message"] == "消息已标记为已读"
    
    await asyncio.sleep(0.5)
    res_b = await client.get("/api/v1/messages/conversations", headers=user_b_headers)
    assert res_b.status_code == 200
    convos_b: List[Dict[str, Any]] = res_b.json()
    assert convos_b[0]["unread_count"] == 0
    
    print("标记已读成功，未读计数已更新")

@pytest.mark.asyncio
@pytest.mark.dependency(depends=["test_mark_message_as_read"])
async def test_send_reply_message(client: AsyncClient):
    """测试：用户B回复消息"""
    sender_auth = shared_data["user_b"]["auth"]
    recipient_id = shared_data["user_a"]["auth"]["user_id"]
    
    message_payload = {
        "recipient_id": recipient_id,
        "content": "你好，同学。很高兴认识你！",
        "message_type": "text",
        "conversation_id": shared_data["conversation_id"]
    }
    
    res = await client.post("/api/v1/messages", json=message_payload, headers=sender_auth["headers"])
    
    assert res.status_code == 201, f"回复消息失败: {res.text}"
    
    await asyncio.sleep(0.5)
    user_a_headers = shared_data["user_a"]["auth"]["headers"]
    res_a = await client.get("/api/v1/messages/conversations", headers=user_a_headers)
    
    assert res_a.status_code == 200
    convos_a: List[Dict[str, Any]] = res_a.json()
    assert "很高兴认识你" in convos_a[0]["last_message"]
    assert convos_a[0]["unread_count"] >= 1
    
    print("回复消息成功，对话列表已更新")
