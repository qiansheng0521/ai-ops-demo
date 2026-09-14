# -*- coding: utf-8 -*-
"""
从公开真实数据集生成项目所需的标准表：
- 订单/销售：data/real/coffee_sales_2024_2025.csv
- 用户评论：data/real/starbucks_reviews.csv

输出：
- data/users.csv
- data/orders.csv
- data/reviews.csv
"""
import pandas as pd

CATEGORY_MAP = {
    "Latte": "咖啡", "Cappuccino": "咖啡", "Americano": "咖啡",
    "Espresso": "咖啡", "Macchiato": "咖啡", "Mocha": "咖啡",
    "Hot Chocolate": "热饮", "Chocolate with coffee": "热饮",
    "Tea": "茶饮", "Herbal Tea": "茶饮", "Iced Coffee": "冰饮",
    "Cold Brew": "冰饮", "Frappe": "冰饮", "Smoothie": "冰饮",
    "Juice": "果汁", "Water": "水", "Soda": "汽水",
}

def category_of(name):
    for key, cat in CATEGORY_MAP.items():
        if key.lower() in str(name).lower():
            return cat
    return "其他"


def build_orders_users():
    sales = pd.read_csv("data/real/coffee_sales_2024_2025.csv", encoding="utf-8")
    sales = sales.rename(columns={"date": "order_date", "cash_type": "channel", "money": "amount", "coffee_name": "product"})
    sales["order_date"] = pd.to_datetime(sales["order_date"], errors="coerce")
    sales = sales.dropna(subset=["order_date", "amount", "product"])
    sales = sales.sort_values("order_date").reset_index(drop=True)

    # 匿名卡号作为客户 ID；现金交易无法识别客户，单独生成一次性 ID
    user_ids = []
    cash_n = 0
    for card in sales["card"]:
        if pd.notna(card) and str(card).strip():
            user_ids.append(str(card).strip())
        else:
            cash_n += 1
            user_ids.append(f"CASH_{cash_n:05d}")
    sales["user_id"] = user_ids
    sales["order_id"] = [f"SALE_{i+1:05d}" for i in range(len(sales))]
    sales["category"] = sales["product"].apply(category_of)
    sales["quantity"] = 1

    users = sales.groupby("user_id").agg(
        signup_date=("order_date", "min"),
        last_order=("order_date", "max"),
        channel=("channel", lambda x: x.mode()[0] if not x.mode().empty else "unknown"),
    ).reset_index()
    users["member_months"] = ((users["last_order"] - users["signup_date"]).dt.days // 30).clip(lower=1)
    users["city"] = "公开数据未提供"
    users["signup_date"] = users["signup_date"].dt.strftime("%Y-%m-%d")
    users = users[["user_id", "city", "channel", "member_months", "signup_date"]]

    orders = sales[["order_id", "user_id", "order_date", "product", "category", "quantity", "amount", "channel"]]
    orders["order_date"] = orders["order_date"].dt.strftime("%Y-%m-%d")

    users.to_csv("data/users.csv", index=False, encoding="utf-8-sig")
    orders.to_csv("data/orders.csv", index=False, encoding="utf-8-sig")
    return len(users), len(orders)


def build_reviews():
    raw = pd.read_csv("data/real/starbucks_reviews.csv", encoding="utf-8")
    raw = raw.rename(columns={"Rating": "rating", "Review": "review_text"})
    raw = raw.dropna(subset=["rating", "review_text"])
    raw["rating"] = raw["rating"].astype(int)
    raw["review_id"] = [f"R{i+1:04d}" for i in range(len(raw))]
    reviews = raw[["review_id", "rating", "review_text"]]
    reviews.to_csv("data/reviews.csv", index=False, encoding="utf-8-sig")
    return len(reviews)


if __name__ == "__main__":
    nu, no = build_orders_users()
    nr = build_reviews()
    print(f"users: {nu}")
    print(f"orders: {no}")
    print(f"reviews: {nr}")
