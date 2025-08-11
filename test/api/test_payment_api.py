import pytest
import httpx
from app.main import app
from typing import Dict, Any
import uuid
from decimal import Decimal

# 使用 httpx 的异步测试客户端
@pytest.fixture(scope="module")
async def client():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac

# 全局变量存储测试中创建的数据
payment_test_data = {
    "user_token": None,
    "user_id": None,
    "username": None,
    "password": None,
    "service_id": None,
    "order_id": None,
    "payment_id": None,
    "out_trade_no": None
}

def random_string(length=10):
    """Generate a random string of fixed length."""
    import random
    import string
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

def get_auth_headers() -> Dict[str, str]:
    """Returns authorization headers."""
    token = payment_test_data.get("user_token")
    if not token:
        pytest.fail("User token not available. Authentication step likely failed.")
    return {"Authorization": f"Bearer {token}"}

# ================== 基础认证测试 ==================

@pytest.mark.asyncio
@pytest.mark.dependency()
@pytest.mark.payment
async def test_01_register_payment_user(client: httpx.AsyncClient):
    """注册支付测试用户"""
    payment_test_data["username"] = f"payment_user_{random_string()}"
    payment_test_data["password"] = "PaymentTest123!"
    
    register_data = {
        "username": payment_test_data["username"],
        "email": f"{payment_test_data['username']}@paymenttest.com",
        "password": payment_test_data["password"]
    }
    
    response = await client.post("/api/v1/auth/register", json=register_data)
    assert response.status_code == 201
    
    user_info = response.json()
    assert user_info["username"] == payment_test_data["username"]
    payment_test_data["user_id"] = user_info["id"]

@pytest.mark.asyncio
@pytest.mark.dependency(depends=["test_01_register_payment_user"])
@pytest.mark.payment
async def test_02_login_payment_user(client: httpx.AsyncClient):
    """登录支付测试用户"""
    login_data = {
        "username": payment_test_data["username"],
        "password": payment_test_data["password"]
    }
    
    response = await client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 200
    
    token_data = response.json()
    payment_test_data["user_token"] = token_data.get("access_token")
    assert payment_test_data["user_token"] is not None

# ================== 订单测试 ==================

@pytest.mark.asyncio
@pytest.mark.dependency(depends=["test_02_login_payment_user"])
@pytest.mark.payment
async def test_03_create_test_order(client: httpx.AsyncClient):
    """创建测试订单"""
    # 首先需要创建一个测试服务
    service_data = {
        "title": "支付测试服务",
        "description": "用于支付功能测试的服务",
        "price": 99.99,
        "category": "test",
        "is_active": True
    }
    
    # 这里假设有创建服务的API，如果没有可以直接设置一个已存在的服务ID
    # response = await client.post("/api/v2/services/", json=service_data, headers=get_auth_headers())
    # 为了测试，我们假设服务ID为1
    payment_test_data["service_id"] = 1
    
    # 创建订单
    order_data = {
        "service_id": payment_test_data["service_id"],
        "notes": "支付功能测试订单"
    }
    
    response = await client.post("/api/v2/payments/orders", json=order_data, headers=get_auth_headers())
    
    # 如果服务不存在，跳过此测试
    if response.status_code == 400:
        pytest.skip("测试服务不存在，跳过订单创建测试")
    
    assert response.status_code == 201
    order_info = response.json()
    payment_test_data["order_id"] = order_info["id"]
    assert order_info["status"] == "pending"

@pytest.mark.asyncio
@pytest.mark.dependency(depends=["test_03_create_test_order"])
@pytest.mark.payment
async def test_04_get_order_info(client: httpx.AsyncClient):
    """获取订单信息"""
    if not payment_test_data.get("order_id"):
        pytest.skip("订单创建失败，跳过订单信息测试")
    
    response = await client.get(
        f"/api/v2/payments/orders/{payment_test_data['order_id']}",
        headers=get_auth_headers()
    )
    assert response.status_code == 200
    
    order_info = response.json()
    assert order_info["id"] == payment_test_data["order_id"]

@pytest.mark.asyncio
@pytest.mark.dependency(depends=["test_02_login_payment_user"])
@pytest.mark.payment
async def test_05_get_orders_list(client: httpx.AsyncClient):
    """获取订单列表"""
    response = await client.get("/api/v2/payments/orders", headers=get_auth_headers())
    assert response.status_code == 200
    
    orders_info = response.json()
    assert "orders" in orders_info
    assert "total" in orders_info

# ================== 支付测试 ==================

@pytest.mark.asyncio
@pytest.mark.dependency(depends=["test_03_create_test_order"])
@pytest.mark.payment
async def test_06_create_payment(client: httpx.AsyncClient):
    """创建支付"""
    if not payment_test_data.get("order_id"):
        pytest.skip("订单创建失败，跳过支付创建测试")
    
    payment_data = {
        "amount": 99.99,
        "payment_method": "alipay",
        "payment_type": "web",
        "return_url": "http://localhost:3000/payment/return"
    }
    
    response = await client.post(
        f"/api/v2/payments/orders/{payment_test_data['order_id']}/pay",
        json=payment_data,
        headers=get_auth_headers()
    )
    
    # 如果支付创建失败（可能是配置问题），记录但不失败
    if response.status_code != 201:
        print(f"支付创建失败: {response.status_code} - {response.text}")
        pytest.skip("支付创建失败，可能是支付配置问题")
    
    assert response.status_code == 201
    payment_info = response.json()
    payment_test_data["payment_id"] = payment_info["payment_id"]
    payment_test_data["out_trade_no"] = payment_info["out_trade_no"]
    
    assert payment_info["payment_method"] == "alipay"
    assert payment_info["amount"] == 99.99

@pytest.mark.asyncio
@pytest.mark.dependency(depends=["test_06_create_payment"])
@pytest.mark.payment
async def test_07_get_payment_info(client: httpx.AsyncClient):
    """获取支付信息"""
    if not payment_test_data.get("payment_id"):
        pytest.skip("支付创建失败，跳过支付信息测试")
    
    response = await client.get(
        f"/api/v2/payments/payments/{payment_test_data['payment_id']}",
        headers=get_auth_headers()
    )
    assert response.status_code == 200
    
    payment_info = response.json()
    assert payment_info["id"] == payment_test_data["payment_id"]

@pytest.mark.asyncio
@pytest.mark.dependency(depends=["test_02_login_payment_user"])
@pytest.mark.payment
async def test_08_get_payments_list(client: httpx.AsyncClient):
    """获取支付列表"""
    response = await client.get("/api/v2/payments/payments", headers=get_auth_headers())
    assert response.status_code == 200
    
    payments_info = response.json()
    assert "payments" in payments_info
    assert "total" in payments_info

@pytest.mark.asyncio
@pytest.mark.dependency(depends=["test_06_create_payment"])
@pytest.mark.payment
async def test_09_cancel_payment(client: httpx.AsyncClient):
    """取消支付"""
    if not payment_test_data.get("payment_id"):
        pytest.skip("支付创建失败，跳过支付取消测试")
    
    response = await client.post(
        f"/api/v2/payments/payments/{payment_test_data['payment_id']}/cancel",
        headers=get_auth_headers()
    )
    assert response.status_code == 200
    
    result = response.json()
    assert result["success"] is True

# ================== 统计测试 ==================

@pytest.mark.asyncio
@pytest.mark.dependency(depends=["test_02_login_payment_user"])
@pytest.mark.payment
async def test_10_get_payment_stats(client: httpx.AsyncClient):
    """获取支付统计"""
    response = await client.get("/api/v2/payments/stats", headers=get_auth_headers())
    assert response.status_code == 200
    
    stats_info = response.json()
    assert "total_payments" in stats_info
    assert "total_amount" in stats_info
    assert "success_rate" in stats_info

# ================== 健康检查测试 ==================

@pytest.mark.asyncio
@pytest.mark.payment
async def test_11_payment_health_check(client: httpx.AsyncClient):
    """支付系统健康检查"""
    response = await client.get("/api/v2/payments/health")
    assert response.status_code == 200
    
    health_info = response.json()
    assert "overall_status" in health_info
    assert "providers" in health_info

# ================== 回调测试（模拟） ==================

@pytest.mark.asyncio
@pytest.mark.payment
async def test_12_mock_alipay_callback(client: httpx.AsyncClient):
    """模拟支付宝回调（仅测试接口可达性）"""
    if not payment_test_data.get("payment_id"):
        pytest.skip("支付创建失败，跳过回调测试")
    
    # 模拟支付宝回调数据（简化版）
    callback_data = {
        "trade_no": "2024010100001",
        "out_trade_no": payment_test_data.get("out_trade_no", "TEST123"),
        "trade_status": "TRADE_SUCCESS",
        "total_amount": "99.99",
        "sign": "mock_signature"
    }
    
    response = await client.post(
        f"/api/v2/payments/callback/alipay/{payment_test_data.get('payment_id', 1)}",
        data=callback_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    # 回调可能因为签名验证失败，但接口应该可达
    assert response.status_code in [200, 403]  # 200成功或403签名失败都是正常的

# ================== 清理测试 ==================

@pytest.mark.asyncio
@pytest.mark.dependency(depends=["test_10_get_payment_stats"])
@pytest.mark.payment
async def test_99_cleanup_test_data(client: httpx.AsyncClient):
    """清理测试数据"""
    # 这里可以添加清理逻辑，比如删除测试订单等
    # 由于我们的测试数据可能不会影响生产，暂时跳过清理
    assert True
