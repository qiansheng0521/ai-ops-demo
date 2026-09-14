# -*- coding: utf-8 -*-
"""
RFM 用户分层分析
输入: data/orders.csv, data/users.csv
输出: data/rfm_segments.csv, outputs/rfm_summary.md
"""
import pandas as pd

ANALYSIS_DATE = pd.Timestamp("2026-06-30")


def segment_label(row):
    r, f, m = row["R_score"], row["F_score"], row["M_score"]
    if r >= 4 and f >= 4 and m >= 4:
        return "重要价值客户"
    if r >= 4 and f <= 2 and m >= 3:
        return "重要发展客户"
    if r <= 2 and f >= 4 and m >= 4:
        return "重要唤回客户"
    if r <= 2 and f <= 2 and m <= 2:
        return "流失风险客户"
    if r >= 3 and f <= 2 and m <= 3:
        return "新客/潜力客户"
    return "一般价值客户"


def main():
    orders = pd.read_csv("data/orders.csv", encoding="utf-8-sig", parse_dates=["order_date"])
    users = pd.read_csv("data/users.csv", encoding="utf-8-sig")

    rfm = orders.groupby("user_id").agg(
        last_order=("order_date", "max"),
        frequency=("order_id", "count"),
        monetary=("amount", "sum"),
    ).reset_index()
    rfm["recency"] = (ANALYSIS_DATE - rfm["last_order"]).dt.days

    # 1-4 分位打分（分数越高越有价值）
    rfm["R_score"] = pd.qcut(rfm["recency"], 4, labels=[4, 3, 2, 1])
    rfm["F_score"] = pd.qcut(rfm["frequency"].rank(method="first"), 4, labels=[1, 2, 3, 4])
    rfm["M_score"] = pd.qcut(rfm["monetary"].rank(method="first"), 4, labels=[1, 2, 3, 4])

    for col in ["R_score", "F_score", "M_score"]:
        rfm[col] = rfm[col].astype(int)

    rfm["segment"] = rfm.apply(segment_label, axis=1)
    rfm = rfm.merge(users[["user_id", "city", "channel"]], on="user_id", how="left")

    rfm.to_csv("data/rfm_segments.csv", index=False, encoding="utf-8-sig")

    summary = rfm.groupby("segment").agg(
        用户数=("user_id", "count"),
        平均消费=("monetary", "mean"),
        平均订单数=("frequency", "mean"),
        平均最近购买天数=("recency", "mean"),
    ).round(1).reset_index()

    summary.to_csv("data/segment_summary.csv", index=False, encoding="utf-8-sig")

    with open("outputs/rfm_summary.md", "w", encoding="utf-8") as f:
        f.write("# RFM 用户分层结果\n\n")
        f.write(summary.to_string(index=False))
        f.write("\n\n## 分层运营策略建议\n\n")
        f.write("- 重要价值客户：专属会员权益、新品优先体验、高客单组合推荐\n")
        f.write("- 重要唤回客户：大额优惠券 + 限时唤醒 push，降低流失\n")
        f.write("- 重要发展客户：提升频次的签到/集章活动，培养消费习惯\n")
        f.write("- 新客/潜力客户：首单转化、新手礼包、社群种草\n")

    print(summary.to_string(index=False))
    print("\n已输出 data/rfm_segments.csv 与 outputs/rfm_summary.md")


if __name__ == "__main__":
    main()
