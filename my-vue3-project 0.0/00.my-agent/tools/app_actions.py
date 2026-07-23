"""App 端可执行动作：打开校园服务 / 跳转课表等。

工具返回 JSON 字符串，由 app.py 提取为响应中的 actions[]。
"""
from __future__ import annotations

import json
import os
from functools import lru_cache
from typing import Any, Dict, Optional

from langchain_core.tools import tool

_CATALOG_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "data",
    "service_catalog.json",
)


@lru_cache(maxsize=1)
def load_catalog() -> Dict[str, Any]:
    with open(_CATALOG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def catalog_keys_help() -> str:
    lines = []
    for key, item in load_catalog().items():
        title = item.get("title", key)
        aliases = "、".join(item.get("aliases") or [])
        lines.append(f"- {key}（{title}）别名：{aliases}")
    return "\n".join(lines)


def build_action(service_key: str) -> Optional[Dict[str, Any]]:
    catalog = load_catalog()
    key = (service_key or "").strip().lower()
    # 允许别名直接当 key 传入
    if key not in catalog:
        for k, item in catalog.items():
            aliases = [a.lower() for a in (item.get("aliases") or [])]
            if key == k.lower() or key in aliases or key == (item.get("title") or "").lower():
                key = k
                break
        else:
            return None

    item = catalog[key]
    action_type = item.get("type")
    if action_type == "switch_tab":
        return {
            "type": "switch_tab",
            "path": item.get("path") or "",
            "title": item.get("title") or key,
            "service_key": key,
        }
    if action_type == "navigate_to":
        return {
            "type": "navigate_to",
            "path": item.get("path") or "",
            "title": item.get("title") or key,
            "service_key": key,
        }
    if action_type == "open_campus_web":
        return {
            "type": "open_campus_web",
            "url": item.get("url") or "",
            "title": item.get("title") or key,
            "service_key": key,
        }
    if action_type == "open_webview":
        return {
            "type": "open_webview",
            "url": item.get("url") or "",
            "title": item.get("title") or key,
            "service_key": key,
        }
    return None


@tool
def open_campus_service(service_key: str) -> str:
    """打开鲤工助手 App 内的校园服务页面或跳转课表。

    当用户明确要求「打开 / 跳转 / 去查 / 进入」某个服务时调用本工具。
    不要在用户只是询问政策、流程、注意事项时调用。

    service_key 可选值（优先用英文 key）：
    - home：首页（签到）
    - timetable：我的课表（App 内 Tab）
    - art：立绘鉴赏（形象小姐姐）
    - emoji：Emoji 表情包
    - contact：联系开发者（用户页）
    - help：使用说明 / 怎么操作
    - feedback：一键反馈
    - grade：查分
    - gpa：GPA / 绩点
    - course_select：自主选课
    - jw_home：教务系统
    - webvpn：WebVPN / VPN
    - ecourse：课程中心
    - ecard：一卡通
    - jw_office：教务处网站
    - cnki：知网
    - wanfang：万方

    也可传入中文别名（如「查分」「课表」「签到」「立绘」），工具会尝试匹配。
    """
    action = build_action(service_key)
    if not action:
        keys = ", ".join(load_catalog().keys())
        return json.dumps(
            {
                "ok": False,
                "error": f"未知服务：{service_key}。可用 key：{keys}",
                "actions": [],
            },
            ensure_ascii=False,
        )

    title = action.get("title") or service_key
    return json.dumps(
        {
            "ok": True,
            "message": f"已为用户准备打开「{title}」，App 将自动跳转。",
            "actions": [action],
        },
        ensure_ascii=False,
    )


@tool
def list_campus_services() -> str:
    """列出 App 当前支持一键打开的校园服务及 service_key。不确定该用哪个 key 时先调用。"""
    return catalog_keys_help()
