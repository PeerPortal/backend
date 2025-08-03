import pytest
from httpx import AsyncClient
from app.main import app
from app.api.deps import get_db
from app.schemas.user_schema import User
from app.api.deps import get_current_user

# 使用测试数据库
from test.database.setup_database import get_test_db, override_get_db

app.dependency_overrides[get_db] = override_get_db

# 模拟用户数据
user1 = User(id=1, username="user1", email="user1@example.com", role="student", is_active=True)
user2 = User(id=2, username="user2", email="user2@example.com", role="mentor", is_active=True)

@pytest.fixture
def set_current_user():
    original_overrides = app.dependency_overrides.copy()
    def _set_user(user: User):
        app.dependency_overrides[get_current_user] = lambda: user
    yield _set_user
    app.dependency_overrides = original_overrides

@pytest.fixture(scope="function")
async def client() -> AsyncClient:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture(scope="module")
def test_db():
    db = next(get_test_db())
    yield db


@pytest.mark.asyncio
async def test_send_message_to_other(test_db, client: AsyncClient, set_current_user):
    """测试用户1向用户2发送消息"""
    
    set_current_user(user1)
    response = await client.post(
        "/api/messages/",
        json={"recipient_id": 2, "content": "你好，user2！"}
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["sender_id"] == 1
    assert data["recipient_id"] == 2
    assert data["content"] == "你好，user2！"
    assert "id" in data
    assert "conversation_id" in data
    
    # 保存 conversation_id 以供后续测试使用
    pytest.conversation_id = data["conversation_id"]

@pytest.mark.asyncio
async def test_send_message_to_self_fails(test_db, client: AsyncClient, set_current_user):
    """测试用户不能给自己发送消息"""
    
    set_current_user(user1)
    response = await client.post(
        "/api/messages/",
        json={"recipient_id": 1, "content": "自言自语"}
    )
    
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_get_conversations_for_user1(test_db, client: AsyncClient, set_current_user):
    """测试获取用户1的对话列表"""
    # 让用户2也回复一条消息，以形成完整对话
    set_current_user(user2)
    await client.post("/api/messages/", json={"recipient_id": 1, "content": "你好，user1！"})
    
    # 切换回用户1来获取对话列表
    set_current_user(user1)
    response = await client.get("/api/messages/conversations")
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] > 0
    conversation = data["conversations"][0]
    assert conversation["other_user"]["id"] == 2
    assert conversation["last_message"] == "你好，user1！"

@pytest.mark.asyncio
async def test_get_conversation_messages(test_db, client: AsyncClient, set_current_user):
    """测试获取特定对话的消息"""
    assert hasattr(pytest, 'conversation_id'), "conversation_id 未在之前的测试中设置"
    
    set_current_user(user1)
    response = await client.get(f"/api/messages/{pytest.conversation_id}/messages")
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 2
    assert data["messages"][0]["content"] == "你好，user1！"
    assert data["messages"][1]["content"] == "你好，user2！"

@pytest.mark.asyncio
async def test_unauthorized_access_to_messages(test_db, client: AsyncClient, set_current_user):
    """测试未授权用户无法访问对话消息"""
    # 创建一个新用户并设置为当前用户
    user3 = User(id=3, username="user3", email="user3@example.com", role="student", is_active=True)
    set_current_user(user3)
    
    response = await client.get(f"/api/messages/{pytest.conversation_id}/messages")
    
    # 应该返回空列表，因为用户3不是参与者
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert len(data["messages"]) == 0