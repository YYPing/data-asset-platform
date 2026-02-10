#!/usr/bin/env python3
"""
手动冒烟测试脚本
测试数据资产平台核心功能
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"
TOKEN = None

def print_test(name, status, details=""):
    """打印测试结果"""
    symbol = "✅" if status else "❌"
    print(f"{symbol} {name}")
    if details:
        print(f"   {details}")

def test_auth():
    """测试认证模块"""
    global TOKEN
    print("\n🔐 测试认证模块")
    print("=" * 50)

    # 测试 1.1: 正确密码登录
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/login",
            json={"username": "admin", "password": "Admin@123456"}
        )
        if response.status_code == 200:
            data = response.json()
            TOKEN = data["token"]["access_token"]
            print_test("1.1 管理员登录（正确密码）", True, f"Token: {TOKEN[:50]}...")
        else:
            print_test("1.1 管理员登录（正确密码）", False, f"状态码: {response.status_code}")
            return False
    except Exception as e:
        print_test("1.1 管理员登录（正确密码）", False, str(e))
        return False

    # 测试 1.2: 错误密码登录
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/login",
            json={"username": "admin", "password": "wrongpassword"}
        )
        if response.status_code == 401:
            print_test("1.2 错误密码登录", True, "正确拒绝")
        else:
            print_test("1.2 错误密码登录", False, f"状态码: {response.status_code}")
    except Exception as e:
        print_test("1.2 错误密码登录", False, str(e))

    # 测试 1.3: 不存在的用户
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/login",
            json={"username": "nonexistent", "password": "password"}
        )
        if response.status_code == 401:
            print_test("1.3 不存在的用户登录", True, "正确拒绝")
        else:
            print_test("1.3 不存在的用户登录", False, f"状态码: {response.status_code}")
    except Exception as e:
        print_test("1.3 不存在的用户登录", False, str(e))

    # 测试 1.4: 无 Token 访问受保护资源
    try:
        response = requests.get(f"{BASE_URL}/api/v1/assets/")
        if response.status_code == 401:
            print_test("1.4 无Token访问受保护资源", True, "正确拒绝")
        else:
            print_test("1.4 无Token访问受保护资源", False, f"状态码: {response.status_code}")
    except Exception as e:
        print_test("1.4 无Token访问受保护资源", False, str(e))

    # 测试 1.5: 无效 Token
    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/assets/",
            headers={"Authorization": "Bearer invalid_token"}
        )
        if response.status_code == 401:
            print_test("1.5 无效Token访问", True, "正确拒绝")
        else:
            print_test("1.5 无效Token访问", False, f"状态码: {response.status_code}")
    except Exception as e:
        print_test("1.5 无效Token访问", False, str(e))

    return True

def test_assets():
    """测试资产管理模块"""
    print("\n📊 测试资产管理模块")
    print("=" * 50)

    if not TOKEN:
        print_test("资产管理测试", False, "缺少认证Token")
        return False

    headers = {"Authorization": f"Bearer {TOKEN}"}
    asset_id = None

    # 测试 2.1: 创建资产
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/assets/",
            headers=headers,
            json={
                "asset_name": "测试数据资产",
                "asset_type": "database",
                "category": "structured",
                "data_classification": "internal",
                "sensitivity_level": "medium",
                "description": "这是一个测试数据资产",
                "data_source": "测试系统",
                "data_volume": "1GB",
                "data_format": "MySQL"
            }
        )
        if response.status_code == 200:
            data = response.json()
            asset_id = data.get("id")
            print_test("2.1 创建资产", True, f"资产ID: {asset_id}")
        else:
            print_test("2.1 创建资产", False, f"状态码: {response.status_code}, {response.text[:100]}")
            return False
    except Exception as e:
        print_test("2.1 创建资产", False, str(e))
        return False

    # 测试 2.2: 查询资产列表
    try:
        response = requests.get(f"{BASE_URL}/api/v1/assets/", headers=headers)
        if response.status_code == 200:
            data = response.json()
            count = data.get("total", 0)
            print_test("2.2 查询资产列表", True, f"找到 {count} 个资产")
        else:
            print_test("2.2 查询资产列表", False, f"状态码: {response.status_code}")
    except Exception as e:
        print_test("2.2 查询资产列表", False, str(e))

    # 测试 2.3: 查询单个资产
    if asset_id:
        try:
            response = requests.get(f"{BASE_URL}/api/v1/assets/{asset_id}", headers=headers)
            if response.status_code == 200:
                data = response.json()
                print_test("2.3 查询单个资产", True, f"资产名称: {data.get('asset_name')}")
            else:
                print_test("2.3 查询单个资产", False, f"状态码: {response.status_code}")
        except Exception as e:
            print_test("2.3 查询单个资产", False, str(e))

    # 测试 2.4: 更新资产
    if asset_id:
        try:
            response = requests.put(
                f"{BASE_URL}/api/v1/assets/{asset_id}",
                headers=headers,
                json={"description": "更新后的描述"}
            )
            if response.status_code == 200:
                print_test("2.4 更新资产", True, "更新成功")
            else:
                print_test("2.4 更新资产", False, f"状态码: {response.status_code}")
        except Exception as e:
            print_test("2.4 更新资产", False, str(e))

    # 测试 2.5: 搜索资产
    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/assets/",
            headers=headers,
            params={"keyword": "测试"}
        )
        if response.status_code == 200:
            data = response.json()
            print_test("2.5 搜索资产", True, f"找到 {data.get('total', 0)} 个结果")
        else:
            print_test("2.5 搜索资产", False, f"状态码: {response.status_code}")
    except Exception as e:
        print_test("2.5 搜索资产", False, str(e))

    return True

def test_materials():
    """测试材料管理模块"""
    print("\n📁 测试材料管理模块")
    print("=" * 50)

    if not TOKEN:
        print_test("材料管理测试", False, "缺少认证Token")
        return False

    headers = {"Authorization": f"Bearer {TOKEN}"}

    # 测试 3.1: 查询材料列表
    try:
        response = requests.get(f"{BASE_URL}/api/v1/materials/", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print_test("3.1 查询材料列表", True, f"状态码: {response.status_code}")
        else:
            print_test("3.1 查询材料列表", False, f"状态码: {response.status_code}")
    except Exception as e:
        print_test("3.1 查询材料列表", False, str(e))

    return True

def test_certificates():
    """测试证书管理模块"""
    print("\n📄 测试证书管理模块")
    print("=" * 50)

    if not TOKEN:
        print_test("证书管理测试", False, "缺少认证Token")
        return False

    headers = {"Authorization": f"Bearer {TOKEN}"}

    # 测试 4.1: 查询证书列表
    try:
        response = requests.get(f"{BASE_URL}/api/v1/certificates/", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print_test("4.1 查询证书列表", True, f"状态码: {response.status_code}")
        else:
            print_test("4.1 查询证书列表", False, f"状态码: {response.status_code}")
    except Exception as e:
        print_test("4.1 查询证书列表", False, str(e))

    return True

def main():
    """主测试函数"""
    print("\n" + "=" * 50)
    print("🧪 数据资产平台 - 手动冒烟测试")
    print("=" * 50)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"后端地址: {BASE_URL}")
    print("=" * 50)

    # 测试认证模块
    auth_ok = test_auth()

    # 测试资产管理模块
    if auth_ok:
        test_assets()

    # 测试材料管理模块
    if auth_ok:
        test_materials()

    # 测试证书管理模块
    if auth_ok:
        test_certificates()

    print("\n" + "=" * 50)
    print("✅ 冒烟测试完成")
    print("=" * 50)

if __name__ == "__main__":
    main()
