# -*- coding: utf-8 -*-
"""生成项目文档所需图片：架构图、RFM 结果图、Dify 工作流图。"""
from PIL import Image, ImageDraw, ImageFont
import pandas as pd

FONT_PATH = r"C:/Windows/Fonts/msyh.ttc"
FALLBACK = r"C:/Windows/Fonts/simhei.ttf"
try:
    FONT = ImageFont.truetype(FONT_PATH, 28)
    FONT_S = ImageFont.truetype(FONT_PATH, 22)
    FONT_TITLE = ImageFont.truetype(FONT_PATH, 36)
except Exception:
    FONT = ImageFont.truetype(FALLBACK, 28)
    FONT_S = ImageFont.truetype(FALLBACK, 22)
    FONT_TITLE = ImageFont.truetype(FALLBACK, 36)

BG = (250, 250, 252)
DARK = (30, 41, 59)
BLUE = (37, 99, 235)
GREEN = (22, 163, 74)
ORANGE = (234, 88, 12)
PURPLE = (124, 58, 237)
GRAY = (100, 116, 139)


def rounded(draw, box, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def text_center(draw, xy, text, font, fill):
    w = draw.textlength(text, font=font)
    draw.text((xy[0] - w / 2, xy[1]), text, font=font, fill=fill)


def architecture():
    w, h = 1280, 720
    img = Image.new("RGB", (w, h), BG)
    d = ImageDraw.Draw(img)
    text_center(d, (w / 2, 40), "AI 驱动的新零售用户运营提效 Demo", FONT_TITLE, DARK)
    text_center(d, (w / 2, 92), "SQL + Python + 大模型 + Agent 工作流", FONT_S, GRAY)

    nodes = [
        (120, 180, "1. 数据生成", "800 用户 / 7000+ 订单", BLUE),
        (420, 180, "2. RFM 用户分层", "SQL + pandas", PURPLE),
        (720, 180, "3. AI 内容生成", "分人群文案 / Prompt", GREEN),
        (1020, 180, "4. 评论洞察", "情感 + 问题分类", ORANGE),
        (270, 460, "5. Agent 日报", "数据 -> 洞察 -> 行动", DARK),
        (720, 460, "6. 产出报告", "MD / CSV / 图表", GREEN),
    ]
    for x, y, title, sub, color in nodes:
        rounded(d, (x, y, x + 240, y + 170), 18, color)
        text_center(d, (x + 120, y + 60), title, FONT_S, (255, 255, 255))
        text_center(d, (x + 120, y + 105), sub, ImageFont.truetype(FONT_PATH, 18), (240, 240, 240))

    arrows = [(360, 265, 420, 265), (660, 265, 720, 265), (960, 265, 1020, 265),
              (390, 350, 390, 460), (510, 545, 720, 545), (720, 460, 960, 460)]
    for x1, y1, x2, y2 in arrows:
        d.line((x1, y1, x2, y2), fill=GRAY, width=4)
        d.ellipse((x2 - 6, y2 - 6, x2 + 6, y2 + 6), fill=GRAY)

    img.save("docs/architecture.png")


def rfm_chart():
    df = pd.read_csv("data/segment_summary.csv", encoding="utf-8-sig")
    df = df.sort_values("用户数", ascending=True)
    w, h = 1200, 640
    img = Image.new("RGB", (w, h), BG)
    d = ImageDraw.Draw(img)
    text_center(d, (w / 2, 30), "RFM 用户分层结果", FONT_TITLE, DARK)
    text_center(d, (w / 2, 78), "按用户数排序", FONT_S, GRAY)

    y0, bar_h, gap = 130, 52, 34
    max_v = max(df["用户数"])
    for i, (_, row) in enumerate(df.iterrows()):
        y = y0 + i * (bar_h + gap)
        label = str(row["segment"])
        d.text((150, y + 10), label, font=FONT_S, fill=DARK)
        w_bar = int((row["用户数"] / max_v) * 720)
        rounded(d, (340, y, 340 + w_bar, y + bar_h), 10, BLUE)
        d.text((350 + w_bar, y + 10), str(row["用户数"]), font=FONT_S, fill=DARK)
    img.save("docs/rfm_chart.png")


def dify_workflow():
    w, h = 1280, 720
    img = Image.new("RGB", (w, h), BG)
    d = ImageDraw.Draw(img)
    text_center(d, (w / 2, 40), "Dify 运营文案工作流", FONT_TITLE, DARK)
    text_center(d, (w / 2, 90), "输入人群/产品/渠道 -> 自动输出多版本文案", FONT_S, GRAY)

    nodes = [
        (90, 260, "开始节点", "segment / product / channel", BLUE),
        (320, 260, "LLM 节点", "生成 3 条营销文案", GREEN),
        (560, 260, "代码节点", "清洗为 JSON", PURPLE),
        (800, 260, "条件分支", "短信追加合规后缀", ORANGE),
        (1030, 260, "结束节点", "输出 final_copies", DARK),
    ]
    for x, y, title, sub, color in nodes:
        rounded(d, (x, y, x + 230, y + 170), 18, color)
        text_center(d, (x + 115, y + 60), title, FONT_S, (255, 255, 255))
        text_center(d, (x + 115, y + 108), sub, ImageFont.truetype(FONT_PATH, 18), (240, 240, 240))

    for x in [320, 550, 790, 1020]:
        d.line((x - 10, 345, x, 345), fill=GRAY, width=4)
        d.ellipse((x - 6, 339, x + 6, 351), fill=GRAY)

    rounded(d, (340, 480, 940, 610), 14, (241, 245, 249), outline=GRAY, width=2)
    d.text((370, 500), "进阶节点：知识库检索 + HTTP 请求（写入飞书/企微）", font=FONT_S, fill=DARK)
    img.save("docs/dify_workflow.png")


if __name__ == "__main__":
    import os
    os.makedirs("docs", exist_ok=True)
    architecture()
    rfm_chart()
    dify_workflow()
    print("images generated")
