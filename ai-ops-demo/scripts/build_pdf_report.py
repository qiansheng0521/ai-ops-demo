# -*- coding: utf-8 -*-
"""生成项目 PDF 报告。"""
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle,
    PageBreak, HRFlowable, KeepTogether
)
import pandas as pd

# ---------- 字体 ----------
pdfmetrics.registerFont(TTFont("MSYH", r"C:/Windows/Fonts/msyh.ttc"))
pdfmetrics.registerFont(TTFont("MSYHBD", r"C:/Windows/Fonts/msyhbd.ttf"))

# ---------- 数据 ----------
SEG = pd.read_csv("data/segment_summary.csv", encoding="utf-8-sig")
ORDERS = pd.read_csv("data/orders.csv", encoding="utf-8-sig", parse_dates=["order_date"])
REVIEWS = pd.read_csv("data/reviews.csv", encoding="utf-8-sig")
INSIGHTS = pd.read_csv("outputs/review_insights.csv", encoding="utf-8-sig")

ANALYSIS_DATE = pd.Timestamp("2026-06-30")
LAST30 = ORDERS[ORDERS["order_date"] >= ANALYSIS_DATE - pd.Timedelta(days=30)]
GMV30 = round(LAST30["amount"].sum(), 1)
ORDERS30 = len(LAST30)
AOV = round(GMV30 / ORDERS30, 1)
NEG_REVIEWS = int((REVIEWS["sentiment"] == "negative").sum())
TOTAL_GMV = round(ORDERS["amount"].sum(), 1)
TOTAL_ORDERS = len(ORDERS)
USERS = len(REVIEWS)  # placeholder never used; users from segment
N_USERS = int(SEG["用户数"].sum())
TOP_PRODUCTS = LAST30.groupby("product")["amount"].sum().sort_values(ascending=False).head(5)

# ---------- 样式 ----------
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="CNTitle", fontName="MSYHBD", fontSize=24, leading=30, alignment=TA_CENTER, textColor=colors.HexColor("#1E293B")))
styles.add(ParagraphStyle(name="CNSubtitle", fontName="MSYH", fontSize=12, leading=18, alignment=TA_CENTER, textColor=colors.HexColor("#64748B")))
styles.add(ParagraphStyle(name="CNH1", fontName="MSYHBD", fontSize=16, leading=22, textColor=colors.HexColor("#2563EB"), spaceBefore=12, spaceAfter=6))
styles.add(ParagraphStyle(name="CNH2", fontName="MSYHBD", fontSize=12.5, leading=18, textColor=colors.HexColor("#0F172A"), spaceBefore=8, spaceAfter=4))
styles.add(ParagraphStyle(name="CNBody", fontName="MSYH", fontSize=10.5, leading=17, alignment=TA_JUSTIFY, textColor=colors.HexColor("#1E293B")))
styles.add(ParagraphStyle(name="CNBullet", fontName="MSYH", fontSize=10.5, leading=17, leftIndent=14, bulletIndent=4, alignment=TA_LEFT, textColor=colors.HexColor("#1E293B")))
styles.add(ParagraphStyle(name="CNCell", fontName="MSYH", fontSize=9, leading=13, alignment=TA_CENTER, textColor=colors.HexColor("#1E293B")))
styles.add(ParagraphStyle(name="CNCellLeft", fontName="MSYH", fontSize=9, leading=13, alignment=TA_LEFT, textColor=colors.HexColor("#1E293B")))

# ---------- 页面函数 ----------
def draw_page(canvas, doc):
    canvas.saveState()
    # 页眉
    canvas.setFillColor(colors.HexColor("#E2E8F0"))
    canvas.rect(0, A4[1]-1.1*cm, A4[0], 1.1*cm, fill=1, stroke=0)
    canvas.setFillColor(colors.HexColor("#64748B"))
    canvas.setFont("MSYH", 8)
    canvas.drawString(2*cm, A4[1]-0.7*cm, "AI 驱动的新零售用户运营提效项目报告")
    # 页脚
    canvas.setFillColor(colors.HexColor("#94A3B8"))
    canvas.drawString(2*cm, 1.0*cm, "个人项目 / Portfolio Demo")
    canvas.drawRightString(A4[0]-2*cm, 1.0*cm, f"第 {doc.page} 页")
    canvas.restoreState()

# ---------- 内容构建 ----------
story = []

# 封面
story.append(Spacer(1, 3.2*cm))
story.append(Paragraph("AI 驱动的新零售", styles["CNTitle"]))
story.append(Paragraph("用户运营提效项目报告", styles["CNTitle"]))
story.append(Spacer(1, 0.4*cm))
story.append(Paragraph("SQL + Python + 大模型 + Agent 工作流", styles["CNSubtitle"]))
story.append(Spacer(1, 2.0*cm))
story.append(HRFlowable(width="70%", thickness=0.8, color=colors.HexColor("#CBD5E1"), hAlign="CENTER"))
story.append(Spacer(1, 0.5*cm))
story.append(Paragraph("GitHub: github.com/qiansheng0521/ai-ops-demo", styles["CNSubtitle"]))
story.append(Spacer(1, 0.2*cm))
story.append(Paragraph("报告日期：2026-09-14", styles["CNSubtitle"]))
story.append(PageBreak())

# 1. 项目背景
story.append(Paragraph("一、项目背景", styles["CNH1"]))
story.append(HRFlowable(width="100%", thickness=0.7, color=colors.HexColor("#BFDBFE"), spaceAfter=6))
story.append(Paragraph("当前 O2O/B2C 行业的运营工作，正在从“经验驱动”转向“数据驱动 + AI 提效”。运营同学不仅需要完成拉新、促活、复购、召回等业务动作，还需要快速处理用户数据、批量产出内容、识别用户反馈，并沉淀可复用的自动化流程。", styles["CNBody"]))
story.append(Spacer(1, 0.15*cm))
story.append(Paragraph("本项目以“连锁咖啡新零售”为模拟业务场景，围绕岗位 JD 中强调的 SQL/Python 数据分析能力、AI 工具使用意愿，以及 LangChain/Dify 等 Agent 框架认知，设计并完整跑通一条运营工作链路：", styles["CNBody"]))
story.append(Spacer(1, 0.15*cm))
for t in [
    "数据生成：模拟 800 名用户、7,000+ 订单、600 条评论；",
    "用户分层：使用 SQL 与 Python 完成 RFM 模型，识别 6 类用户；",
    "AI 内容生成：基于人群与渠道批量生成营销文案；",
    "用户洞察：自动完成评论情感与业务问题分类；",
    "Agent 工作流：自动汇总销售数据并生成运营日报。",
]:
    story.append(Paragraph(t, styles["CNBullet"], bulletText="-"))
story.append(Spacer(1, 0.2*cm))
story.append(Paragraph("目标是通过一个可运行、可展示的 Demo，证明“数据 + AI + 运营”的复合能力，并可直接用于简历与面试讲解。", styles["CNBody"]))

# 2. 业务场景与数据说明
story.append(Paragraph("二、业务场景与数据说明", styles["CNH1"]))
story.append(HRFlowable(width="100%", thickness=0.7, color=colors.HexColor("#BFDBFE"), spaceAfter=6))
story.append(Paragraph("业务场景", styles["CNH2"]))
story.append(Paragraph("模拟某连锁咖啡品牌的 O2O/B2C 运营：用户通过小程序、APP、门店、美团、饿了么等渠道下单，涉及咖啡、烘焙、轻食、周边等品类。运营目标是提升用户活跃、复购与 GMV，同时降低内容生产和日报整理的人工成本。", styles["CNBody"]))
story.append(Spacer(1, 0.15*cm))
story.append(Paragraph("数据规模", styles["CNH2"]))
data_table = [
    ["指标", "数值"],
    ["用户数", f"{N_USERS} 人"],
    ["订单数", f"{TOTAL_ORDERS:,} 单"],
    ["评论数", f"{len(REVIEWS)} 条"],
    ["累计 GMV", f"{TOTAL_GMV:,.1f} 元"],
    ["近 30 天 GMV", f"{GMV30:,.1f} 元"],
    ["近 30 天订单数", f"{ORDERS30:,} 单"],
    ["近 30 天客单价", f"{AOV:.1f} 元"],
    ["近 30 天负面评论", f"{NEG_REVIEWS} 条"],
]
t = Table(data_table, colWidths=[6.5*cm, 7.5*cm], hAlign="CENTER")
t.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#2563EB")),
    ("TEXTCOLOR", (0,0), (-1,0), colors.white),
    ("FONTNAME", (0,0), (-1,0), "MSYHBD"),
    ("FONTNAME", (0,1), (-1,-1), "MSYH"),
    ("FONTSIZE", (0,0), (-1,-1), 9.5),
    ("LEADING", (0,0), (-1,-1), 14),
    ("ALIGN", (0,0), (-1,-1), "CENTER"),
    ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
    ("GRID", (0,0), (-1,-1), 0.4, colors.HexColor("#CBD5E1")),
    ("TOPPADDING", (0,0), (-1,-1), 5),
    ("BOTTOMPADDING", (0,0), (-1,-1), 5),
]))
story.append(t)

# 3. 项目架构
story.append(Paragraph("三、项目整体架构", styles["CNH1"]))
story.append(HRFlowable(width="100%", thickness=0.7, color=colors.HexColor("#BFDBFE"), spaceAfter=6))
story.append(Image("docs/architecture.png", width=15*cm, height=15*cm*720/1280, hAlign="CENTER"))
story.append(Spacer(1, 0.15*cm))
story.append(Paragraph("整个项目按照“数据准备 → 用户分层 → AI 内容生成与评论洞察 → Agent 日报”四个层次组织，输入输出均可复现。", styles["CNBody"]))
story.append(PageBreak())

# 4. 方法一：RFM
story.append(Paragraph("四、用户分层：SQL + Python RFM 模型", styles["CNH1"]))
story.append(HRFlowable(width="100%", thickness=0.7, color=colors.HexColor("#BFDBFE"), spaceAfter=6))
story.append(Paragraph("通过 SQL 从订单表聚合用户最近购买时间（Recency）、购买频次（Frequency）、消费金额（Monetary），再用 Python 对 R/F/M 分别做四分位打分，最后映射为 6 类人群。", styles["CNBody"]))
story.append(Spacer(1, 0.15*cm))
story.append(Image("docs/rfm_chart.png", width=15*cm, height=15*cm*640/1200, hAlign="CENTER"))
story.append(Spacer(1, 0.15*cm))
seg_rows = [["用户分层", "用户数", "平均消费（元）", "平均订单数", "平均最近购买天数"]]
for _, r in SEG.iterrows():
    seg_rows.append([str(r["segment"]), str(r["用户数"]), f"{r['平均消费']:.1f}", f"{r['平均订单数']:.1f}", f"{r['平均最近购买天数']:.1f}"])
tseg = Table(seg_rows, colWidths=[4.4*cm, 2.4*cm, 3.2*cm, 2.6*cm, 3.2*cm], hAlign="CENTER", repeatRows=1)
tseg.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#7C3AED")),
    ("TEXTCOLOR", (0,0), (-1,0), colors.white),
    ("FONTNAME", (0,0), (-1,0), "MSYHBD"),
    ("FONTNAME", (0,1), (-1,-1), "MSYH"),
    ("FONTSIZE", (0,0), (-1,-1), 9),
    ("LEADING", (0,0), (-1,-1), 13),
    ("ALIGN", (0,0), (-1,-1), "CENTER"),
    ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#F5F3FF")]),
    ("GRID", (0,0), (-1,-1), 0.4, colors.HexColor("#DDD6FE")),
    ("TOPPADDING", (0,0), (-1,-1), 4),
    ("BOTTOMPADDING", (0,0), (-1,-1), 4),
]))
story.append(tseg)
story.append(Spacer(1, 0.2*cm))
story.append(Paragraph("策略建议", styles["CNH2"]))
for t in [
    "重要价值客户：专属会员权益、新品优先体验、高客单组合推荐；",
    "重要唤回客户：大额优惠券 + 限时唤醒 push，降低流失；",
    "重要发展客户：提升频次的签到/集章活动，培养消费习惯；",
    "新客/潜力客户：首单转化、新手礼包、社群种草。",
]:
    story.append(Paragraph(t, styles["CNBullet"], bulletText="-"))

# 5. 方法二：AI 文案
story.append(Paragraph("五、AI 内容生成：分人群多渠道文案", styles["CNH1"]))
story.append(HRFlowable(width="100%", thickness=0.7, color=colors.HexColor("#BFDBFE"), spaceAfter=6))
story.append(Paragraph("基于 RFM 分层结果，针对不同人群和渠道生成差异化的营销文案。配置 OpenAI 兼容 API 后调用真实大模型；未配置时使用本地 Mock 模板，确保 Demo 始终可运行。", styles["CNBody"]))
story.append(Spacer(1, 0.15*cm))
copy_rows = [["人群", "渠道", "产品", "文案"]]
for _, r in pd.read_csv("outputs/campaign_copy.csv", encoding="utf-8-sig").head(6).iterrows():
    copy_rows.append([str(r["segment"]), str(r["channel"]), str(r["product"]), str(r["copy"])])
tcopy = Table(copy_rows, colWidths=[3.0*cm, 2.4*cm, 2.4*cm, 7.2*cm], hAlign="CENTER", repeatRows=1)
tcopy.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#16A34A")),
    ("TEXTCOLOR", (0,0), (-1,0), colors.white),
    ("FONTNAME", (0,0), (-1,0), "MSYHBD"),
    ("FONTNAME", (0,1), (-1,-1), "MSYH"),
    ("FONTSIZE", (0,0), (-1,-1), 8.5),
    ("LEADING", (0,0), (-1,-1), 12),
    ("ALIGN", (0,0), (-1,-1), "CENTER"),
    ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#F0FDF4")]),
    ("GRID", (0,0), (-1,-1), 0.4, colors.HexColor("#BBF7D0")),
    ("TOPPADDING", (0,0), (-1,-1), 4),
    ("BOTTOMPADDING", (0,0), (-1,-1), 4),
]))
story.append(tcopy)
story.append(Spacer(1, 0.2*cm))
story.append(Paragraph("关键能力点：Prompt 模板设计、多渠道适配、人工审核机制，以及将大模型 API 与实际运营数据结合的能力。", styles["CNBody"]))

# 6. 方法三：评论洞察
story.append(Paragraph("六、用户评论洞察", styles["CNH1"]))
story.append(HRFlowable(width="100%", thickness=0.7, color=colors.HexColor("#BFDBFE"), spaceAfter=6))
story.append(Paragraph("对 600 条评论进行情感分类和业务问题归类。配置大模型时调用 LLM 分类；未配置时使用关键词规则回退。", styles["CNBody"]))
story.append(Spacer(1, 0.15*cm))
insight_summary = INSIGHTS.groupby(["sentiment", "category"]).size().reset_index(name="数量").sort_values("数量", ascending=False).head(10)
ins_rows = [["情感", "业务问题", "数量"]]
for _, r in insight_summary.iterrows():
    ins_rows.append([str(r["sentiment"]), str(r["category"]), str(r["数量"])])
tins = Table(ins_rows, colWidths=[4.4*cm, 4.4*cm, 4.4*cm], hAlign="CENTER", repeatRows=1)
tins.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#EA580C")),
    ("TEXTCOLOR", (0,0), (-1,0), colors.white),
    ("FONTNAME", (0,0), (-1,0), "MSYHBD"),
    ("FONTNAME", (0,1), (-1,-1), "MSYH"),
    ("FONTSIZE", (0,0), (-1,-1), 9),
    ("LEADING", (0,0), (-1,-1), 13),
    ("ALIGN", (0,0), (-1,-1), "CENTER"),
    ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#FFF7ED")]),
    ("GRID", (0,0), (-1,-1), 0.4, colors.HexColor("#FED7AA")),
    ("TOPPADDING", (0,0), (-1,-1), 4),
    ("BOTTOMPADDING", (0,0), (-1,-1), 4),
]))
story.append(tins)
story.append(Spacer(1, 0.2*cm))
story.append(Paragraph("洞察价值：将散落的用户反馈自动归类到“口味 / 价格 / 配送 / 服务 / 其他”等可行动维度，为产品、客服、门店运营提供数据依据。", styles["CNBody"]))

# 7. Agent 工作流
story.append(Paragraph("七、Agent 工作流与自动日报", styles["CNH1"]))
story.append(HRFlowable(width="100%", thickness=0.7, color=colors.HexColor("#BFDBFE"), spaceAfter=6))
story.append(Paragraph("参考 LangChain/Dify 的编排思路，将“数据汇总 → 指标计算 → 重点人群识别 → 行动建议生成 → 日报输出”串联为自动化流程。", styles["CNBody"]))
story.append(Spacer(1, 0.15*cm))
story.append(Image("docs/dify_workflow.png", width=15*cm, height=15*cm*720/1280, hAlign="CENTER"))
story.append(Spacer(1, 0.15*cm))
top_rows = [["热销商品 TOP5", "销售额（元）"]]
for product, amount in TOP_PRODUCTS.items():
    top_rows.append([str(product), f"{amount:,.1f}"])
ttop = Table(top_rows, colWidths=[7.0*cm, 6.0*cm], hAlign="CENTER")
ttop.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#0F172A")),
    ("TEXTCOLOR", (0,0), (-1,0), colors.white),
    ("FONTNAME", (0,0), (-1,0), "MSYHBD"),
    ("FONTNAME", (0,1), (-1,-1), "MSYH"),
    ("FONTSIZE", (0,0), (-1,-1), 9),
    ("LEADING", (0,0), (-1,-1), 13),
    ("ALIGN", (0,0), (-1,-1), "CENTER"),
    ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
    ("GRID", (0,0), (-1,-1), 0.4, colors.HexColor("#CBD5E1")),
    ("TOPPADDING", (0,0), (-1,-1), 4),
    ("BOTTOMPADDING", (0,0), (-1,-1), 4),
]))
story.append(ttop)

# 8. 运营策略与业务价值
story.append(Paragraph("八、运营策略与业务价值", styles["CNH1"]))
story.append(HRFlowable(width="100%", thickness=0.7, color=colors.HexColor("#BFDBFE"), spaceAfter=6))
for t in [
    "数据驱动：通过 RFM 分层，把资源优先投向重要价值客户与重要唤回客户，避免“广撒网式”运营；",
    "内容提效：AI 按人群/渠道批量生成文案，减少重复写作时间，预计内容产出效率提升约 70%；",
    "洞察闭环：自动识别负面评论的业务来源，推动配送、价格、服务等环节优化；",
    "自动化沉淀：Agent 日报将人工准备时间从小时级压缩到分钟级，可复制到日常运营中。",
]:
    story.append(Paragraph(t, styles["CNBullet"], bulletText="-"))

# 9. 技术栈与可复现性
story.append(Paragraph("九、技术栈与可复现步骤", styles["CNH1"]))
story.append(HRFlowable(width="100%", thickness=0.7, color=colors.HexColor("#BFDBFE"), spaceAfter=6))
story.append(Paragraph("技术栈：Python · pandas · SQL · OpenAI API · Prompt Engineering · Dify / LangChain 工作流设计", styles["CNBody"]))
story.append(Spacer(1, 0.15*cm))
story.append(Paragraph("可复现步骤", styles["CNH2"]))
for t in [
    "1. 运行 scripts/generate_data.py 生成模拟数据；",
    "2. 运行 scripts/rfm_analysis.py 完成用户分层；",
    "3. 运行 scripts/ai_copy_generator.py 生成分人群文案；",
    "4. 运行 scripts/review_insights.py 完成评论洞察；",
    "5. 运行 scripts/agent_workflow.py 生成运营日报；",
    "6. 运行 dify/demo_workflow.py 演示 Dify 类工作流。",
]:
    story.append(Paragraph(t, styles["CNBullet"], bulletText="-"))

# 10. 总结
story.append(Paragraph("十、总结", styles["CNH1"]))
story.append(HRFlowable(width="100%", thickness=0.7, color=colors.HexColor("#BFDBFE"), spaceAfter=6))
story.append(Paragraph("本项目用一个完整 Demo 覆盖了 O2O/B2C 运营岗位最看重的三类能力：业务数据分析、AI 工具落地、Agent 工作流设计。它既能作为简历中的项目经历，也能在面试时现场演示核心流程。", styles["CNBody"]))

# ---------- 输出 ----------
os.makedirs("output/pdf", exist_ok=True)
doc = SimpleDocTemplate(
    "output/pdf/AI_Ops_Project_Report.pdf",
    pagesize=A4,
    rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm,
    title="AI 驱动的新零售用户运营提效项目报告",
    author="qiansheng0521",
)
doc.build(story, onFirstPage=draw_page, onLaterPages=draw_page)
print("PDF generated")
