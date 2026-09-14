# -*- coding: utf-8 -*-
"""
用户评论洞察：情感分类 + 业务问题归类
配置 OPENAI_API_KEY 时调用大模型；否则使用关键词规则回退。
"""
import os
import json
import pandas as pd

try:
    from openai import OpenAI
except Exception:
    OpenAI = None

CATEGORY_KEYWORDS = {
    "口味": ["味道", "好喝", "苦", "香", "惊艳"],
    "价格": ["价格", "贵", "划算", "优惠券", "9.9"],
    "配送": ["配送", "慢", "凉", "快", "包装", "漏"],
    "服务": ["服务", "客服", "排队", "态度"],
}


def classify_by_llm(text):
    prompt = f"""请判断下面这条用户评论的情绪，并从["正面","中性","负面"]中选择一个；
再从["口味","价格","配送","服务","其他"]中选择最相关的一个业务问题。
只输出 JSON，格式：{{"sentiment":"正面","category":"口味"}}

评论：{text}"""
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not (api_key and OpenAI):
        return None
    base_url = os.getenv("OPENAI_BASE_URL", "")
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    client = OpenAI(api_key=api_key, base_url=base_url or None)
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )
    content = resp.choices[0].message.content.strip()
    try:
        return json.loads(content)
    except Exception:
        return None


def classify_by_rules(text, rating):
    sentiment = "positive" if rating >= 4 else ("negative" if rating <= 2 else "neutral")
    category = "其他"
    for cat, words in CATEGORY_KEYWORDS.items():
        if any(w in text for w in words):
            category = cat
            break
    return {"sentiment": sentiment, "category": category}


def main():
    reviews = pd.read_csv("data/reviews.csv", encoding="utf-8-sig")
    results = []
    for _, row in reviews.iterrows():
        r = classify_by_llm(row["review_text"]) or classify_by_rules(row["review_text"], row["rating"])
        results.append({
            "review_id": row["review_id"],
            "rating": row["rating"],
            "sentiment": r["sentiment"],
            "category": r["category"],
            "review_text": row["review_text"],
        })

    df = pd.DataFrame(results)
    df.to_csv("outputs/review_insights.csv", index=False, encoding="utf-8-sig")

    summary = df.groupby(["sentiment", "category"]).size().reset_index(name="数量")
    summary = summary.sort_values("数量", ascending=False)

    with open("outputs/review_insights.md", "w", encoding="utf-8") as f:
        f.write("# 用户评论洞察报告\n\n")
        f.write(summary.to_string(index=False))
        f.write("\n\n## 建议行动\n\n")
        f.write("- 针对「配送」类负面反馈：优化骑手时效提示，增加超时补偿机制。\n")
        f.write("- 针对「价格」类反馈：测试 9.9 元引流款与满减组合。\n")
        f.write("- 针对「服务」类反馈：加强门店排队管理和客服话术培训。\n")

    print(summary.to_string(index=False))
    print("\n已输出 outputs/review_insights.csv 与 outputs/review_insights.md")


if __name__ == "__main__":
    main()
