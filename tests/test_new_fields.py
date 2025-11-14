"""测试新增字段的E2E测试"""
import sys
sys.path.insert(0, r"d:\pygithub\TimeKeeper\TimeKeeper")

from fastapi.testclient import TestClient
from main import app
from datetime import datetime, timedelta
import json

def test_all_new_fields():
    """测试所有新增字段功能"""
    client = TestClient(app)
    
    # 1. 注册新用户
    timestamp = datetime.now().timestamp()
    register_data = {
        "phone": f"138{int(timestamp % 100000000)}",
        "password": "Password123!",
        "nickname": f"测试用户{int(timestamp)}"
    }
    register_response = client.post("/api/v1/users/register", json=register_data)
    print("✅ 用户注册:")
    print(f"   状态码: {register_response.status_code}")
    if register_response.status_code in [200, 201]:
        user_data = register_response.json()
        print(f"   phone: {user_data.get('phone')}")
        print(f"   is_active: {user_data.get('is_active', 'N/A')}")
        print(f"   updated_at: {user_data.get('updated_at', 'N/A')}")
    else:
        print(f"   错误: {register_response.json()}")
        raise Exception("注册失败")
    
    # 2. 登录获取token
    login_data = {
        "phone": register_data["phone"],
        "password": register_data["password"]
    }
    login_response = client.post("/api/v1/users/login", json=login_data)
    print("\n✅ 用户登录:")
    print(f"   状态码: {login_response.status_code}")
    if login_response.status_code != 200:
        print(f"   错误: {login_response.json()}")
        raise Exception("登录失败")
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 3. 创建带所有新字段的提醒
    reminder_data = {
        "title": "房租支付提醒",
        "description": "每月15号支付房租，需要提前准备转账",
        "category": "finance",
        "recurrence_type": "monthly",
        "recurrence_config": {"day_of_month": 15},
        "first_remind_time": (datetime.now() + timedelta(days=1)).isoformat(),
        "remind_channels": ["push", "email"],
        "advance_minutes": 1440,
        "priority": 3,  # 高优先级
        "amount": 250000,  # 2500.00元（分）
        "location": {
            "address": "北京市朝阳区建国路1号",
            "latitude": 39.9087,
            "longitude": 116.3975
        },
        "attachments": [
            {
                "type": "image",
                "url": "https://example.com/contract.jpg",
                "filename": "租房合同.jpg"
            },
            {
                "type": "pdf",
                "url": "https://example.com/receipt.pdf",
                "filename": "上月收据.pdf"
            }
        ]
    }
    
    create_response = client.post("/api/v1/reminders/", json=reminder_data, headers=headers)
    reminder = create_response.json()
    
    print("\n✅ 创建提醒（所有新字段）:")
    print(f"   ID: {reminder['id']}")
    print(f"   Title: {reminder['title']}")
    print(f"   Priority: {reminder['priority']} (1=低 2=中 3=高)")
    print(f"   Amount: ¥{reminder['amount']/100:.2f} (原始: {reminder['amount']} 分)")
    print(f"   Location: {json.dumps(reminder['location'], ensure_ascii=False)}")
    print(f"   Attachments: {len(reminder['attachments'])} 个附件")
    for i, att in enumerate(reminder['attachments'], 1):
        print(f"      - 附件{i}: {att['filename']} ({att['type']})")
    print(f"   is_completed: {reminder['is_completed']}")
    print(f"   completed_at: {reminder['completed_at']}")
    
    # 4. 验证所有字段类型和值
    assert reminder['priority'] == 3, "priority应为3"
    assert reminder['amount'] == 250000, "amount应为250000分"
    assert reminder['location']['address'] == "北京市朝阳区建国路1号", "location应包含正确地址"
    assert len(reminder['attachments']) == 2, "应有2个附件"
    assert not reminder['is_completed'], "新创建的提醒应未完成"
    assert reminder['completed_at'] is None, "未完成的提醒completed_at应为None"
    
    print("\n🎉 所有字段验证通过！")
    print("\n📊 新增字段功能汇总:")
    print("   ✓ priority: 支持1-3级优先级")
    print("   ✓ amount: 支持金额记录（分为单位）")
    print("   ✓ location: 支持JSON位置信息（地址+经纬度）")
    print("   ✓ attachments: 支持JSON附件列表")
    print("   ✓ is_completed: 支持完成状态")
    print("   ✓ completed_at: 支持完成时间记录")

if __name__ == "__main__":
    test_all_new_fields()
