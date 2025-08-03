import pytest
import httpx
from app.main import app
from app.core.config import settings
from typing import Dict, Any, Optional
import random
import string

# 使用 httpx 的异步测试客户端
@pytest.fixture(scope="module")
async def client():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac

# 全局变量存储测试中创建的数据
test_data = {
    "post_id": None,
    "reply_id": None,
    "user_token": None,
    "user_id": None,
    "username": None,
    "password": None
}

def random_string(length=10):
    """Generate a random string of fixed length."""
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

@pytest.mark.asyncio
@pytest.mark.dependency()
async def test_register_user(client: httpx.AsyncClient):
    """Register a new user for testing."""
    test_data["username"] = f"testuser_{random_string()}"
    test_data["password"] = "a_strong_password"
    
    register_data = {
        "username": test_data["username"],
        "email": f"{test_data['username']}@example.com",
        "password": test_data["password"]
    }
    
    response = await client.post("/api/v1/auth/register", json=register_data)
    assert response.status_code == 201
    user_info = response.json()
    assert user_info["username"] == test_data["username"]
    test_data["user_id"] = user_info["id"]

@pytest.mark.asyncio
@pytest.mark.dependency(depends=["test_register_user"])
async def test_get_token(client: httpx.AsyncClient):
    """Test getting a user token."""
    auth_url = "/api/v1/auth/login"
    login_data = {"username": test_data["username"], "password": test_data["password"]}
    
    response = await client.post(auth_url, data=login_data)
    assert response.status_code == 200, f"Login failed with response: {response.text}"
    
    token_data = response.json()
    test_data["user_token"] = token_data.get("access_token")
    assert test_data["user_token"] is not None

def get_auth_headers() -> Dict[str, str]:
    """Returns authorization headers."""
    token = test_data.get("user_token")
    if not token:
        pytest.fail("User token not available. Authentication step likely failed.")
    return {"Authorization": f"Bearer {token}"}

@pytest.mark.asyncio
@pytest.mark.dependency(depends=["test_get_token"])
async def test_create_post(client: httpx.AsyncClient):
    """Test creating a new post."""
    post_data = {
        "title": "My Test Post from Automated Test",
        "content": "This is the content of the test post.",
        "category": "qna",
        "tags": ["testing", "fastapi"],
        "is_anonymous": False
    }
    response = await client.post("/api/v1/forum/posts", json=post_data, headers=get_auth_headers())
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == post_data["title"]
    assert data["author"]["id"] == test_data["user_id"]
    test_data["post_id"] = data["id"]

@pytest.mark.asyncio
@pytest.mark.dependency(depends=["test_create_post"])
async def test_get_post_by_id(client: httpx.AsyncClient):
    """Test retrieving a single post by its ID."""
    post_id = test_data.get("post_id")
    response = await client.get(f"/api/v1/forum/posts/{post_id}", headers=get_auth_headers())
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == post_id

@pytest.mark.asyncio
@pytest.mark.dependency(depends=["test_create_post"])
async def test_get_posts_list(client: httpx.AsyncClient):
    """Test retrieving a list of posts."""
    author_id = test_data["user_id"]
    response = await client.get(f"/api/v1/forum/posts?author_id={author_id}", headers=get_auth_headers())
    assert response.status_code == 200
    data = response.json()
    assert "posts" in data
    assert "total" in data
    assert isinstance(data["posts"], list)
    assert any(p["id"] == test_data["post_id"] for p in data["posts"])

@pytest.mark.asyncio
@pytest.mark.dependency(depends=["test_create_post"])
async def test_update_post(client: httpx.AsyncClient):
    """Test updating an existing post."""
    post_id = test_data.get("post_id")
    update_data = {"title": "My Updated Test Post Title"}
    response = await client.put(f"/api/v1/forum/posts/{post_id}", json=update_data, headers=get_auth_headers())
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == update_data["title"]
    assert data["id"] == post_id

@pytest.mark.asyncio
@pytest.mark.dependency(depends=["test_create_post"])
async def test_toggle_post_like(client: httpx.AsyncClient):
    """Test liking and unliking a post."""
    post_id = test_data.get("post_id")
    # Like the post
    response_like = await client.post(f"/api/v1/forum/posts/{post_id}/like", headers=get_auth_headers())
    assert response_like.status_code == 200
    data_like = response_like.json()
    assert data_like["is_liked"] is True
    assert data_like["likes_count"] >= 0

    # Unlike the post
    response_unlike = await client.post(f"/api/v1/forum/posts/{post_id}/like", headers=get_auth_headers())
    assert response_unlike.status_code == 200
    data_unlike = response_unlike.json()
    assert data_unlike["is_liked"] is False
    assert data_unlike["likes_count"] == data_like["likes_count"] - 1

@pytest.mark.asyncio
@pytest.mark.dependency(depends=["test_create_post"])
async def test_create_reply(client: httpx.AsyncClient):
    """Test creating a reply to a post."""
    post_id = test_data.get("post_id")
    reply_data = {
        "content": "This is a test reply.",
        "parent_id": None
    }
    response = await client.post(f"/api/v1/forum/posts/{post_id}/replies", json=reply_data, headers=get_auth_headers())
    assert response.status_code == 201
    data = response.json()
    assert data["content"] == reply_data["content"]
    assert data["post_id"] == post_id
    test_data["reply_id"] = data["id"]

@pytest.mark.asyncio
@pytest.mark.dependency(depends=["test_create_reply"])
async def test_get_post_replies(client: httpx.AsyncClient):
    """Test getting replies for a post."""
    post_id = test_data.get("post_id")
    response = await client.get(f"/api/v1/forum/posts/{post_id}/replies", headers=get_auth_headers())
    assert response.status_code == 200
    data = response.json()
    assert "replies" in data
    assert "total" in data
    assert any(r["id"] == test_data["reply_id"] for r in data["replies"])

@pytest.mark.asyncio
@pytest.mark.dependency(depends=["test_create_reply"])
async def test_delete_reply(client: httpx.AsyncClient):
    """Test deleting a reply."""
    reply_id = test_data.get("reply_id")
    response = await client.delete(f"/api/v1/forum/replies/{reply_id}", headers=get_auth_headers())
    assert response.status_code == 200
    assert response.json()["message"] == "删除成功"

@pytest.mark.asyncio
@pytest.mark.dependency(depends=["test_create_post"])
async def test_delete_post(client: httpx.AsyncClient):
    """Test deleting a post at the end of all tests."""
    post_id = test_data.get("post_id")
    response = await client.delete(f"/api/v1/forum/posts/{post_id}", headers=get_auth_headers())
    assert response.status_code == 200
    assert response.json()["message"] == "删除成功"

    # Verify deletion
    try:
        response_get = await client.get(f"/api/v1/forum/posts/{post_id}")
        assert response_get.status_code == 404
    except Exception as e:
        pytest.fail(f"An unexpected error occurred: {e}")
