# -*- coding: utf-8 -*-
"""
AI 内容生成：基于 RFM 人群分层，批量生成多渠道运营文案
支持 OpenAI 兼容 API；未配置 key 时自动使用本地 Mock 模板，保证 Demo 可运行。
"""
import os
import json
import pandas as pd

try:
    from openai import OpenAI
except Exception:  # pragma: no cover
    OpenAI = None

CHANNELS = ["小程序 push", "短信", "社群", "朋友圈"]


def call_llm(prompt):
    """调用 OpenAI 兼容接口；失败或未配置时回退到 Mock。"""
    api_key = os.getenv("OPENAI_API_KEY", "")
    base_url = os.getenv("OPENAI_BASE_URL", "")
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    if api_key and OpenAI:
        client = OpenAI(api_key=api_key, base_url=base_url or None)
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        return resp.choices[0].message.content.strip()

    return mock_generate(prompt)


def mock_generate(prompt):
    """无 API Key 时的规则化生成，便于本地演示流程。"""
    if "咖啡" in prompt:
        product = "咖啡"
    else:
        product = "轻食/周边"
    if any(w in prompt for w in ["召回", "沉睡", "唤回"]):
        hook = "好久不见，你的专属回归券已到账"
    elif "新客" in prompt or "潜力" in prompt:
        hook = "新人首杯 9.9 元，本周限定"
    elif "价值" in prompt:
        hook = "会员专属：新品抢先尝 + 双倍积分"
    else:
        hook = "今日限时：满 59 减 12"
    return f"{hook}｜{product}套餐搭配推荐｜点击立即领取"


def build_prompt(segment, product, channel):
    return f"""你是新零售品牌的高级运营文案。请为「{segment}」人群，在「{channel}」渠道，
为产品「{product}」写一条 40 字以内的营销文案。要求：口语化、有行动指令、突出利益点。"""


def main():
    rfm = pd.read_csv("data/rfm_segments.csv", encoding="utf-8-sig")
    segments = rfm["segment"].unique()

    rows = []
    products = ["生椰拿铁", "冷萃咖啡", "烘焙早餐"]
    for segment in segments:
        for channel in CHANNELS:
            product = products[hash(segment) % len(products)]
            prompt = build_prompt(segment, product, channel)
            copy = call_llm(prompt)
            rows.append({"segment": segment, "channel": channel, "product": product, "copy": copy})

    out = pd.DataFrame(rows)
    out.to_csv("outputs/campaign_copy.csv", index=False, encoding="utf-8-sig")

    with open("outputs/campaign_copy.md", "w", encoding="utf-8") as f:
        f.write("# 分人群运营文案生成结果\n\n")
        f.write("> 未配置 OPENAI_API_KEY 时使用本地 Mock；配置后自动切换为真实大模型。\n\n")
        f.write(out.to_string(index=False))

    print(out.to_string(index=False))
    print("\n已输出 outputs/campaign_copy.csv 与 outputs/campaign_copy.md")


if __name__ == "__main__":
    main()
