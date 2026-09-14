# -*- coding: utf-8 -*-
"""
生成 O2O/B2C 模拟数据：连锁咖啡/新零售场景
输出:
  data/users.csv
  data/orders.csv
  data/reviews.csv
"""
import random
import csv
from datetime import datetime, timedelta

SEED = 42
random.seed(SEED)

N_USERS = 800
N_ORDERS = 4000
N_REVIEWS = 600

CITIES = ["上海", "北京", "深圳", "杭州", "成都"]
CHANNELS = ["小程序", "APP", "门店", "美团", "饿了么"]
PRODUCTS = {
    "拿铁": (28, 45),
    "美式": (22, 35),
    "生椰拿铁": (30, 48),
    "冷萃": (32, 50),
    "烘焙早餐": (18, 38),
    "轻食沙拉": (25, 45),
    "周边杯": (49, 89),
}
PRODUCT_NAMES = list(PRODUCTS.keys())
CATEGORIES = {
    "拿铁": "咖啡", "美式": "咖啡", "生椰拿铁": "咖啡", "冷萃": "咖啡",
    "烘焙早餐": "烘焙", "轻食沙拉": "轻食", "周边杯": "周边",
}

START = datetime(2025, 7, 1)
END = datetime(2026, 6, 30)
DAYS = (END - START).days

REVIEW_POOL = {
    "positive": [
        "新品很好喝，出杯也快。",
        "配送很快，包装完整，会回购。",
        "咖啡豆很香，门店环境不错。",
        "服务态度好，优惠券也能正常使用。",
        "早餐搭配咖啡很划算。",
    ],
    "neutral": [
        "味道还可以，但没有特别惊艳。",
        "等餐时间稍长，整体能接受。",
        "价格小贵，偶尔喝一次。",
        "包装一般，咖啡没洒。",
    ],
    "negative": [
        "配送太慢了，咖啡都凉了。",
        "口味偏苦，不太适合我。",
        "门店排队太久，服务一般。",
        "杯子漏了，体验很差。",
        "优惠券规则复杂，客服解释不清。",
    ],
}

def random_date(start, end):
    return start + timedelta(days=random.randint(0, (end - start).days))


def generate_users():
    rows = []
    for i in range(1, N_USERS + 1):
        signup = random_date(START, END)
        rows.append({
            "user_id": f"U{i:04d}",
            "city": random.choice(CITIES),
            "channel": random.choice(CHANNELS),
            "member_months": max(1, int((END - signup).days // 30)),
            "signup_date": signup.strftime("%Y-%m-%d"),
        })
    return rows


def generate_orders(users):
    rows = []
    # 让部分用户更活跃，形成可分层结构
    for idx, user in enumerate(users):
        uid = user["user_id"]
        signup = datetime.strptime(user["signup_date"], "%Y-%m-%d")
        # 不同用户活跃度差异
        if idx < 150:  # 高价值/高活跃
            n = random.randint(18, 35)
        elif idx < 350:  # 中等活跃
            n = random.randint(6, 14)
        elif idx < 550:  # 低频
            n = random.randint(2, 5)
        else:  # 沉睡/新客
            n = random.randint(1, 2)

        for _ in range(n):
            order_date = random_date(max(signup, START), END)
            product = random.choice(PRODUCT_NAMES)
            low, high = PRODUCTS[product]
            price = round(random.uniform(low, high), 1)
            qty = random.choices([1, 2, 3], weights=[70, 25, 5])[0]
            rows.append({
                "order_id": f"O{len(rows) + 1:05d}",
                "user_id": uid,
                "order_date": order_date.strftime("%Y-%m-%d"),
                "product": product,
                "category": CATEGORIES[product],
                "quantity": qty,
                "amount": round(price * qty, 1),
                "channel": random.choice(CHANNELS),
            })
    return rows


def generate_reviews(orders):
    rows = []
    sampled = random.sample(orders, min(N_REVIEWS, len(orders)))
    for order in sampled:
        r = random.random()
        if r < 0.55:
            sentiment = "positive"
        elif r < 0.80:
            sentiment = "neutral"
        else:
            sentiment = "negative"
        rating_map = {"positive": [4, 5], "neutral": [3, 4], "negative": [1, 2, 3]}
        rows.append({
            "review_id": f"R{len(rows) + 1:04d}",
            "user_id": order["user_id"],
            "order_id": order["order_id"],
            "rating": random.choice(rating_map[sentiment]),
            "sentiment": sentiment,
            "review_text": random.choice(REVIEW_POOL[sentiment]),
            "review_date": order["order_date"],
        })
    return rows


def write_csv(path, fieldnames, rows):
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    users = generate_users()
    orders = generate_orders(users)
    reviews = generate_reviews(orders)

    write_csv("data/users.csv", list(users[0].keys()), users)
    write_csv("data/orders.csv", list(orders[0].keys()), orders)
    write_csv("data/reviews.csv", list(reviews[0].keys()), reviews)

    print(f"users: {len(users)}")
    print(f"orders: {len(orders)}")
    print(f"reviews: {len(reviews)}")


if __name__ == "__main__":
    main()
