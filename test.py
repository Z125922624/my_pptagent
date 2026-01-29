import requests


def check_deepseek_balance():
    """检查DeepSeek API余额"""
    api_key = "sk-bfd54b338b5f4601992e5505c737bff1"  # 替换为您的API密钥

    # 尝试不同的余额查询端点
    endpoints = [
        "https://api.deepseek.com/dashboard/billing/credit_grants",
        "https://api.deepseek.com/user/balance",
        "https://api.deepseek.com/billing/credit_grants"
    ]

    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    for endpoint in endpoints:
        print(f"\n尝试端点: {endpoint}")
        try:
            response = requests.get(endpoint, headers=headers, timeout=10)
            print(f"状态码: {response.status_code}")

            if response.status_code == 200:
                print("✅ 获取余额信息成功:")
                print(response.text[:500])  # 显示部分内容
                break
            elif response.status_code == 404:
                print("❌ 端点不存在，尝试下一个...")
                continue
            else:
                print(f"响应: {response.text[:200]}")
        except Exception as e:
            print(f"错误: {e}")

    # 如果以上端点都不行，使用计费API
    print("\n" + "=" * 50)
    print("通过计费API测试密钥有效性:")

    test_url = "https://api.deepseek.com/chat/completions"
    test_data = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": "test"}],
        "max_tokens": 1
    }
    test_headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    try:
        response = requests.post(test_url, json=test_data, headers=test_headers, timeout=10)
        print(f"测试状态码: {response.status_code}")

        if response.status_code == 200:
            print("✅ API密钥有效！")
            result = response.json()
            if 'error' in result:
                error_msg = result['error'].get('message', '未知错误')
                if 'quota' in error_msg.lower():
                    print("⚠️  余额不足，请充值")
                else:
                    print(f"错误信息: {error_msg}")
        elif response.status_code == 401:
            print("❌ API密钥无效")
        elif response.status_code == 429:
            print("⚠️  频率限制，但密钥有效")
        else:
            print(f"响应: {response.text[:200]}")

    except Exception as e:
        print(f"测试异常: {e}")


# 运行余额检查
check_deepseek_balance()

# 使用您的API密钥
api_key = "sk-bfd54b338b5f4601992e5505c737bff1"
