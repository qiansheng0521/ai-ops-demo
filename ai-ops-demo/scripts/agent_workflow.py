# -*- coding: utf-8 -*-
"""
运营 Agent 工作流：自动汇总销售数据 -> 识别重点人群 -> 生成日报与行动建议
此脚本演示 LangChain/Dify 等 Agent 框架中常见的“数据 -> 洞察 -> 文案/日报”编排逻辑。
"""
import pandas as pd
from datetime import datetime, timedelta
from ai_copy_generator import call_llm

ANALYSIS_DATE = None


def sales_kpis(orders):
    last30 = orders[orders["order_date"] >= ANALYSIS_DATE - pd.Timedelta(days=30)]
    gmv = last30["amount"].sum()
    orders_cnt = len(last30)
    aov = gmv / orders_cnt if orders_cnt else 0
    top_products = last30.groupby("product")["amount"].sum().sort_values(ascending=False).head(5)
    return {
        "gmv_30d": round(gmv, 1),
        "orders_30d": orders_cnt,
        "aov": round(aov, 1),
        "top_products": top_products,
    }


def main():
    orders = pd.read_csv("data/orders.csv", encoding="utf-8-sig", parse_dates=["order_date"])
    rfm = pd.read_csv("data/rfm_segments.csv", encoding="utf-8-sig")
    reviews = pd.read_csv("outputs/review_insights.csv", encoding="utf-8-sig")

    global ANALYSIS_DATE
    ANALYSIS_DATE = orders["order_date"].max()
    kpi = sales_kpis(orders)
    seg_summary = rfm.groupby("segment").agg(用户数=("user_id", "count"), 平均消费=("monetary", "mean")).round(1)
    neg_reviews = reviews[reviews["sentiment"] == "negative"].shape[0]

    # 让大模型生成一段行动建议；无 Key 时回退到 Mock
    context = f"""近30天 GMV {kpi['gmv_30d']} 元，订单 {kpi['orders_30d']} 单，客单价 {kpi['aov']} 元。
重点人群：{', '.join(rfm['segment'].unique())}。负面评论 {neg_reviews} 条。"""
    suggestion = call_llm("你是运营负责人，请基于以下数据给出一句话行动建议：" + context)

    with open("outputs/daily_report.md", "w", encoding="utf-8") as f:
        f.write("# 运营日报（自动生成）\n\n")
        f.write(f"- 统计周期：近 30 天（截至 {ANALYSIS_DATE.date()}）\n")
        f.write(f"- GMV：{kpi['gmv_30d']} 元\n")
        f.write(f"- 订单数：{kpi['orders_30d']}\n")
        f.write(f"- 客单价：{kpi['aov']} 元\n")
        f.write(f"- 负面评论：{neg_reviews} 条\n\n")
        f.write("## 热销商品 TOP5\n\n")
        f.write(kpi["top_products"].to_frame().to_string())
        f.write("\n\n## 重点人群\n\n")
        f.write(seg_summary.to_string())
        f.write("\n\n## Agent 行动建议\n\n")
        f.write(suggestion + "\n")

    print("已生成 outputs/daily_report.md")
    print(suggestion)


if __name__ == "__main__":
    main()
