"""把 App 上报的 device_context 格式化为提示文本（按 scope 只展开需要的课）。"""


def _fmt_course(c):
    if not isinstance(c, dict):
        return ""
    name = c.get("name") or "未命名课程"
    section = c.get("section") or ""
    t0 = c.get("time_start") or ""
    t1 = c.get("time_end") or ""
    room = c.get("room") or ""
    teacher = c.get("teacher") or ""
    day_cn = c.get("day_cn") or ""
    weeks = c.get("weeks") or ""
    time_bit = ""
    if t0 and t1:
        time_bit = f"{t0}-{t1}"
    elif t0:
        time_bit = t0
    parts = []
    if day_cn:
        parts.append(day_cn)
    if section:
        parts.append(f"第{section}节")
    if time_bit:
        parts.append(time_bit)
    parts.append(name)
    line = " ".join(parts)
    extras = []
    if room:
        extras.append(f"@{room}")
    if teacher:
        extras.append(teacher)
    if weeks:
        extras.append(f"周次:{weeks}")
    if extras:
        line += " " + " ".join(extras)
    return line


def _append_course_list(lines, title, courses):
    lines.append(title)
    if not courses:
        lines.append("- （无课）")
        return
    for c in courses:
        line = _fmt_course(c)
        if line:
            lines.append(f"- {line}")


DAY_CN = {
    "1": "周一",
    "2": "周二",
    "3": "周三",
    "4": "周四",
    "5": "周五",
    "6": "周六",
    "7": "周日",
}


def format_device_context(ctx):
    if not ctx or not isinstance(ctx, dict):
        return ""

    scope = ctx.get("scope") or "none"
    lines = ["【设备上下文｜仅依据下列数据回答，严禁编造未列出的课程或签到结果】"]

    today = ctx.get("today") or ""
    weekday_cn = ctx.get("weekday_cn") or ""
    if today or weekday_cn:
        lines.append(f"今天：{today} {weekday_cn}".strip())

    tw = ctx.get("teaching_week")
    if tw:
        lines.append(f"当前教学周：第{tw}周")
    elif ctx.get("has_timetable") and not ctx.get("semester_set"):
        lines.append("开学日未设置：教学周可能不准，请提醒用户去课表页设置开学日。")

    mode = ctx.get("time_mode") or ""
    if mode == "wushan":
        lines.append("作息：五山校区时间")
    elif mode == "university":
        lines.append("作息：大学城/国际校区时间")

    # 签到（精简或详细都由前端决定字段）
    checkin = ctx.get("checkin") if isinstance(ctx.get("checkin"), dict) else None
    if checkin is not None:
        if checkin.get("signed_today") and checkin.get("caption") is not None:
            lines.append(
                f"今日签到：已签到；累计 {checkin.get('total_days') or 0} 天；"
                f"表情 {checkin.get('label') or checkin.get('emoji_index')}；"
                f"配语：{checkin.get('caption') or '（无）'}"
            )
        elif checkin.get("signed_today"):
            lines.append(f"今日签到：已签到；累计 {checkin.get('total_days') or 0} 天。")
        else:
            tip = f"今日签到：未签到；累计 {checkin.get('total_days') or 0} 天。"
            if scope in ("checkin", "none"):
                tip += "若用户要签到，可调用 open_campus_service('home')。"
            lines.append(tip)

    # 无关问题：到此为止
    if scope == "none":
        return "\n".join(lines)

    if not ctx.get("has_timetable"):
        if scope in ("day", "next", "week", "full"):
            lines.append(
                "本地课表：未导入。请说明需先导入，并调用 open_campus_service('timetable')。"
            )
        return "\n".join(lines)

    lines.append("本地课表：已导入。")

    # 某一天
    if scope in ("day", "next"):
        qdate = ctx.get("query_date") or ""
        qwd = ctx.get("query_weekday_cn") or ""
        qoff = ctx.get("query_day_offset")
        qtw = ctx.get("query_teaching_week")
        label = f"查询日：{qdate} {qwd}".strip()
        if qoff is not None:
            label += f"（相对今天 {qoff:+d} 天）"
        if qtw:
            label += f"；该日教学周第{qtw}周"
        lines.append(label)
        _append_course_list(lines, "该日课程：", ctx.get("day_courses") or [])
        nxt = ctx.get("next_course")
        if isinstance(nxt, dict) and nxt.get("name"):
            lines.append(f"下一节课：{_fmt_course(nxt)}")
        elif scope == "next":
            lines.append("下一节课：今日后续已无课。")
        return "\n".join(lines)

    # 本周
    if scope == "week":
        lines.append("本教学周课表：")
        week = ctx.get("week_courses") or {}
        if not week:
            lines.append("- （本周无课）")
        else:
            for d in ["1", "2", "3", "4", "5", "6", "7"]:
                courses = week.get(d) or []
                if not courses:
                    continue
                _append_course_list(lines, f"{DAY_CN.get(d, d)}：", courses)
        return "\n".join(lines)

    # 完整
    if scope == "full":
        lines.append("完整课表条目（含周次）：")
        all_courses = ctx.get("all_courses") or []
        if not all_courses:
            lines.append("- （无）")
        else:
            for c in all_courses:
                line = _fmt_course(c)
                if line:
                    lines.append(f"- {line}")
        week = ctx.get("week_courses") or {}
        if week:
            lines.append("另附本教学周展开：")
            for d in ["1", "2", "3", "4", "5", "6", "7"]:
                courses = week.get(d) or []
                if not courses:
                    continue
                _append_course_list(lines, f"{DAY_CN.get(d, d)}：", courses)
        return "\n".join(lines)

    if scope == "checkin":
        return "\n".join(lines)

    return "\n".join(lines)


def wrap_user_message(message: str, device_context=None) -> str:
    block = format_device_context(device_context)
    msg = (message or "").strip()
    if not block:
        return msg
    return f"{block}\n\n【用户本轮提问】\n{msg}"
