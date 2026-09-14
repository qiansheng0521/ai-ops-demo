# -*- coding: utf-8 -*-
"""
Dify 运营文案工作流本地演示
模拟 Dify 画布中的节点：开始 -> LLM -> 代码 -> 条件分支 -> 结束
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from ai_copy_generator import call_llm


def start_node():
    """开始节点：接收业务输入。"""
    return {
        "segment": "重要唤回客户",
        "product": "生椰拿铁",
        "channel": "短信",
    }


def llm_node(inputs):
    """LLM 节点：生成文案。"""
    prompt = f"""你是新零售品牌高级运营文案。请为「{inputs['segment']}」人群，
在「{inputs['channel']}」渠道，为产品「{inputs['product']}」写 3 条 40 字以内的营销文案。
要求口语化、有行动指令、突出利益点。"""
    return call_llm(prompt)


def code_node(text):
    """代码节点：把文本清洗成可投放的 JSON 数组。"""
    lines = [line.strip(" -") for line in text.splitlines() if line.strip()]
    return {"copies": lines[:3]}


def condition_node(payload, inputs):
    """条件分支：短信渠道追加合规后缀。"""
    if inputs["channel"] == "短信":
        payload["copies"] = [c + "（退订回T）" for c in payload["copies"]]
    return payload


def end_node(payload):
    """结束节点：输出最终结果。"""
    return payload


def main():
    inputs = start_node()
    llm_text = llm_node(inputs)
    payload = code_node(llm_text)
    payload = condition_node(payload, inputs)
    result = end_node(payload)

    out_path = Path("outputs/dify_demo.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    print("输入：", json.dumps(inputs, ensure_ascii=False))
    print("输出：", json.dumps(result, ensure_ascii=False, indent=2))
    print("已写入 outputs/dify_demo.json")


if __name__ == "__main__":
    main()
