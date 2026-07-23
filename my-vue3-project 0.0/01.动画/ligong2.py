# -*- coding: utf-8 -*-
"""
鲤工助手 · 宣传动画（修订分镜）
依据：具体要求：.md + assets/ 实际素材
美术：延续前作黑底科技风（青蓝/紫霓虹、HUD、Glitch、矩阵雨）
"""
from manim import *
import numpy as np
import random
from manim.utils.rate_functions import (
    ease_out_sine, ease_out_back, there_and_back, linear, smooth, ease_in_out_sine
)

# ================= 科技风配色 =================
TECH_BLUE = "#00F0FF"
TECH_PURPLE = "#8A2BE2"
TECH_BG = "#0A0A12"
WARNING_RED = "#FF3366"
CYAN_GLITCH = "#00FFFF"
GLASS_WHITE = "#FFFFFF"
SOFT_GREEN = "#39FFB6"

FONT = "Microsoft YaHei"

# ================= 素材路径（与 assets 文件名对齐） =================
ASSETS = {
    "logo": "assets/logo.jpg",
    "art_half": "assets/04.半身图.jpg",
    "art_full": "assets/03.全身图.jpg",
    "art_sketch_half": "assets/01.手绘半身草图.jpg",
    "art_sketch_full": "assets/02.全身草图.jpg",
    "worried": "assets/苦恼.jpg",
    "home_before": "assets/签到前的首页.jpg",
    "home_after": "assets/签到后的首页.jpg",
    "agent": "assets/智能体页面.jpg",
    "agent_demo_0": "assets/Agent功能演示0.jpg",  # 选课跳转 + 今日课表问答
    "agent_demo_1": "assets/Agent功能演示1.jpg",  # 华工知识库（学习方法等）
    "timetable": "assets/课表页面.jpg",
    "import_tt": "assets/课表导入页面.jpg",
    "user": "assets/用户页面.jpg",
    "art_about": "assets/立绘鉴赏_关于立绘.jpg",
    "emoji_gate": "assets/emoji表情包入口页面.jpg",
    "emoji_view_00": "assets/表情包00鉴赏页面.jpg",
    "emoji_view_11": "assets/表情包11鉴赏页面.jpg",
    "emoji_view_13": "assets/表情包13鉴赏页面.jpg",
    "qr": "assets/下载APP二维码.png",
    # 配乐：由「星际.mp3」截取前 75 秒 → bgm_75s.mp3
    "bgm": "assets/bgm_75s.mp3",
    "emoji_00": "assets/00.emoji/00.jpg",
    "emoji_01": "assets/00.emoji/01.jpg",
    "emoji_02": "assets/00.emoji/02.jpg",
    "emoji_03": "assets/00.emoji/03.jpg",
    "emoji_04": "assets/00.emoji/04.jpg",
    "emoji_05": "assets/00.emoji/05.jpg",
    "emoji_06": "assets/00.emoji/06.jpg",
    "emoji_07": "assets/00.emoji/07.jpg",
    "emoji_08": "assets/00.emoji/08.jpg",
    "emoji_09": "assets/00.emoji/09.jpg",
    "emoji_10": "assets/00.emoji/10.jpg",
    "emoji_11": "assets/00.emoji/11.jpg",
    "emoji_12": "assets/00.emoji/12.jpg",
    "emoji_13": "assets/00.emoji/13.jpg",
    "emoji_14": "assets/00.emoji/14.jpg",
    "emoji_15": "assets/00.emoji/15.jpg",
}

EMOJI_CAPTION_00 = "爱心发射～先哄好你，再偷偷搞小恶作剧ฅ●ω●ฅ"


class LiGongAssistant(Scene):
    def construct(self):
        self.camera.background_color = TECH_BG
        if ASSETS.get("bgm"):
            self.add_sound(ASSETS["bgm"])

        self.intro()
        self.problem()
        self.solution()
        self.features()
        self.agent_showcase()
        self.art_gallery()
        self.call_to_action()
        self.outro()
        self.credits()

    # ================= 特效工具 =================
    def safe_image(self, path, height=6, width=None):
        try:
            img = ImageMobject(path)
            if width is not None:
                img.scale_to_fit_width(width)
            else:
                img.scale_to_fit_height(height)
            return img
        except Exception:
            w = width if width is not None else height * 0.55
            h = height
            placeholder = RoundedRectangle(
                corner_radius=0.2, width=w, height=h,
                color=TECH_BLUE, fill_opacity=0.05, stroke_width=2
            )
            lines = VGroup(*[
                Line(placeholder.get_left(), placeholder.get_right(),
                     stroke_width=0.5, stroke_opacity=0.2)
                for _ in range(16)
            ]).arrange(DOWN, buff=h / 16).move_to(placeholder)
            cross = VGroup(
                Line(placeholder.get_corner(UL), placeholder.get_corner(DR),
                     color=TECH_BLUE, stroke_opacity=0.5),
                Line(placeholder.get_corner(UR), placeholder.get_corner(DL),
                     color=TECH_BLUE, stroke_opacity=0.5),
            )
            text = Text("ASSET MISSING", font="Courier", font_size=14,
                        weight=BOLD, color=TECH_BLUE).move_to(placeholder)
            return Group(placeholder, lines, cross, text)

    def create_neon_glow(self, mobject, color=TECH_BLUE, max_width=15, layers=4):
        glow = VGroup()
        for i in range(layers):
            layer = mobject.copy()
            layer.set_stroke(
                color=color,
                width=max_width * (1 - i / layers),
                opacity=0.15 * (i / layers + 0.2),
            )
            layer.set_fill(opacity=0)
            glow.add(layer)
        return glow

    def create_hud_corners(self, mobject, padding=0.2, length=0.4, stroke_width=3, color=TECH_BLUE):
        ul = mobject.get_corner(UL) + np.array([-padding, padding, 0])
        ur = mobject.get_corner(UR) + np.array([padding, padding, 0])
        dl = mobject.get_corner(DL) + np.array([-padding, -padding, 0])
        dr = mobject.get_corner(DR) + np.array([padding, -padding, 0])
        corners = VGroup(
            VGroup(Line(ul, ul + RIGHT * length), Line(ul, ul + DOWN * length)),
            VGroup(Line(ur, ur + LEFT * length), Line(ur, ur + DOWN * length)),
            VGroup(Line(dl, dl + RIGHT * length), Line(dl, dl + UP * length)),
            VGroup(Line(dr, dr + LEFT * length), Line(dr, dr + UP * length)),
        )
        corners.set_stroke(color=color, width=stroke_width)
        return corners

    def phone_frame(self, w=3.0, h=6.2):
        border = RoundedRectangle(
            corner_radius=0.35, width=w, height=h,
            color=TECH_BLUE, stroke_width=3, fill_color=TECH_BG, fill_opacity=0.95
        )
        notch = RoundedRectangle(
            corner_radius=0.08, width=0.9, height=0.16,
            color=TECH_BLUE, fill_opacity=1
        ).move_to(border.get_top() + DOWN * 0.14)
        glow = self.create_neon_glow(border, color=TECH_BLUE, max_width=18)
        return border, notch, glow

    def gradient_title(self, text, font_size=40, weight=BOLD):
        t = Text(text, font=FONT, weight=weight, font_size=font_size)
        t.set_color_by_gradient(TECH_BLUE, TECH_PURPLE)
        return t

    def chat_bubble(self, text, side="user", max_width=5.5, font_size=22):
        """side: user=右青, agent=左紫"""
        body = Text(text, font=FONT, font_size=font_size, color=GLASS_WHITE)
        if body.width > max_width - 0.5:
            body = Text(text, font=FONT, font_size=font_size - 4, color=GLASS_WHITE)
            if body.width > max_width - 0.5:
                # 手动换行
                chars = list(text)
                mid = len(chars) // 2
                text = "".join(chars[:mid]) + "\n" + "".join(chars[mid:])
                body = Text(text, font=FONT, font_size=font_size - 2, color=GLASS_WHITE)

        pad_x, pad_y = 0.28, 0.18
        bg = RoundedRectangle(
            corner_radius=0.18,
            width=body.width + pad_x * 2,
            height=body.height + pad_y * 2,
            stroke_width=1.5,
            fill_opacity=0.92,
        )
        if side == "user":
            bg.set_stroke(TECH_BLUE, 1.5)
            bg.set_fill("#12304A", 0.92)
        else:
            bg.set_stroke(TECH_PURPLE, 1.5)
            bg.set_fill("#1A1230", 0.92)
        body.move_to(bg.get_center())
        return Group(bg, body)

    def clear_updaters_in(self, *mobs):
        for m in mobs:
            if m is None:
                continue
            try:
                m.clear_updaters()
            except Exception:
                pass
            if hasattr(m, "submobjects"):
                for s in m.submobjects:
                    try:
                        s.clear_updaters()
                    except Exception:
                        pass

    # ================= 1. 开场 =================
    def intro(self):
        cmd_lines = VGroup(*[
            Text(f"> {txt}", font="Courier", font_size=15, weight=BOLD, color=TECH_BLUE)
            for txt in [
                "INITIALIZING KERNEL...",
                "MOUNTING VIRTUAL DOM...",
                "LOADING SCUT AGENT...",
                "SYSTEM ONLINE_ ",
            ]
        ]).arrange(DOWN, aligned_edge=LEFT, buff=0.18).to_corner(UL, buff=0.4)
        self.play(LaggedStart(*[Write(line) for line in cmd_lines], lag_ratio=0.28), run_time=1.8)

        grid = NumberPlane(
            background_line_style={"stroke_color": TECH_BLUE, "stroke_opacity": 0.15},
            faded_line_style={"stroke_color": TECH_PURPLE, "stroke_opacity": 0.05},
        )
        grid.set_opacity(0)
        self.play(grid.animate.set_opacity(1), run_time=1.2, rate_func=smooth)

        # 粒子汇聚
        particles = VGroup()
        for _ in range(48):
            ang = random.uniform(0, TAU)
            r = random.uniform(3.5, 7.5)
            p = Dot(
                point=[r * np.cos(ang), r * np.sin(ang), 0],
                radius=random.uniform(0.02, 0.05),
                color=random.choice([TECH_BLUE, TECH_PURPLE, GLASS_WHITE]),
            )
            particles.add(p)
        self.play(LaggedStart(*[FadeIn(p, scale=0.2) for p in particles], lag_ratio=0.01), run_time=0.6)

        rings = VGroup()
        for i, r in enumerate(np.arange(0.5, 5.5, 0.85)):
            ring = DashedVMobject(
                Circle(radius=r, color=TECH_BLUE),
                num_dashes=28 + i * 8, dashed_ratio=0.55
            )
            ring.set_stroke(opacity=max(0.15, 1 - r / 6.5), width=1.5 + r / 3)
            ring.add_updater(
                lambda m, dt, idx=i: m.rotate(dt * (0.45 if idx % 2 == 0 else -0.28) / (idx + 1))
            )
            rings.add(ring)
        self.play(
            LaggedStart(*[Create(ring) for ring in rings], lag_ratio=0.04),
            *[p.animate.move_to(ORIGIN * 0 + np.array([
                random.uniform(-0.3, 0.3), random.uniform(-0.3, 0.3), 0
            ])) for p in particles],
            run_time=1.4, rate_func=ease_out_sine
        )

        logo = self.safe_image(ASSETS["logo"], height=2.4)
        glow = self.create_neon_glow(Circle(radius=1.35), color=TECH_PURPLE, max_width=42)
        glow.add_updater(lambda m, dt: m.scale(1 + 0.012 * np.sin(self.time * 4)))

        self.play(
            FadeOut(particles, scale=0.2),
            FadeIn(glow),
            FadeIn(logo, scale=0.15),
            run_time=1.1, rate_func=ease_out_back
        )
        title = self.gradient_title("鲤工助手", font_size=56)
        title.next_to(logo, DOWN, buff=0.5)
        # 开场只聚焦 Logo + 标题，不放半身像
        self.play(Write(title), run_time=1.0)
        self.play(Flash(title, color=TECH_BLUE, line_length=0.55, num_lines=28, flash_radius=2.2), run_time=0.7)
        self.wait(0.35)

        self.clear_updaters_in(glow, *rings)
        self.play(
            LaggedStart(
                FadeOut(grid), FadeOut(cmd_lines), FadeOut(rings, scale=1.8),
                FadeOut(glow), FadeOut(logo, shift=UP * 0.4),
                FadeOut(title, shift=DOWN * 0.3),
                lag_ratio=0.08
            ),
            run_time=0.9
        )

    # ================= 2. 问题引入 =================
    def problem(self):
        warning_bg = Rectangle(width=16, height=9, color=WARNING_RED, fill_opacity=0.05, stroke_width=0)
        warning_bg.add_updater(lambda m, dt: m.set_opacity(0.04 + 0.07 * np.sin(self.time * 14)))
        self.add(warning_bg)

        chaos_group = VGroup()
        labels = ["教务", "VPN", "选课", "查分", "收藏夹", "链接", "通知", "表格"]
        for i in range(22):
            frag = RoundedRectangle(
                corner_radius=0.1,
                width=random.uniform(0.7, 2.2),
                height=random.uniform(0.35, 0.7),
            )
            frag.set_style(
                stroke_color=WARNING_RED, stroke_width=1.2, stroke_opacity=0.7,
                fill_color=TECH_BG, fill_opacity=0.92
            )
            label = Text(
                random.choice(labels) if random.random() > 0.45 else hex(random.randint(0x1000, 0xFFFF)),
                font="Courier" if random.random() > 0.5 else FONT,
                font_size=14, color=WARNING_RED
            ).move_to(frag)
            item = VGroup(frag, label).move_to([
                random.uniform(-6.8, 6.8), random.uniform(-3.6, 3.6), 0
            ])
            chaos_group.add(item)

        self.play(
            LaggedStart(*[FadeIn(f, scale=1.4) for f in chaos_group], lag_ratio=0.012),
            run_time=1.3
        )

        worried = self.safe_image(ASSETS["worried"], height=3.0)
        worried_glow = SurroundingRectangle(worried, color=WARNING_RED, buff=0.08, stroke_width=2)
        qmarks = VGroup(*[
            Text("?", font=FONT, font_size=42, color=TECH_BLUE, weight=BOLD)
            .move_to(worried.get_center() + np.array([dx, dy, 0]))
            for dx, dy in [(-2.0, 1.2), (2.1, 1.0), (0.2, 2.0)]
        ])
        for q in qmarks:
            q.add_updater(lambda m, dt: m.set_opacity(0.35 + 0.65 * abs(np.sin(self.time * 5 + hash(id(m)) % 7))))

        self.play(
            FadeIn(worried, scale=0.85), Create(worried_glow),
            LaggedStart(*[FadeIn(q, scale=1.5) for q in qmarks], lag_ratio=0.15),
            run_time=0.9
        )

        lines = [
            "华工网站太散，入口找不到？",
            "课表导入麻烦，今天有什么课只能自己翻？",
            "问通用 AI——答非所问，不懂华工？",
        ]
        text_group = VGroup(*[
            Text(s, font=FONT, weight=BOLD, font_size=30,
                  color=GLASS_WHITE if i < 2 else WARNING_RED)
            for i, s in enumerate(lines)
        ]).arrange(DOWN, buff=0.35).to_edge(DOWN, buff=0.55)

        bg_rect = RoundedRectangle(
            corner_radius=0.2, width=12.2, height=2.6,
            color=TECH_BG, fill_opacity=0.94, stroke_width=2, stroke_color=WARNING_RED
        ).move_to(text_group.get_center())

        glitch_cyan = text_group.copy().set_color(CYAN_GLITCH)
        glitch_red = text_group.copy().set_color(WARNING_RED)
        self.play(FadeIn(bg_rect), Write(text_group), run_time=1.0)
        self.add(glitch_cyan, glitch_red, text_group)

        for _ in range(7):
            self.play(
                glitch_cyan.animate.move_to(
                    text_group.get_center() + np.array([random.uniform(-0.14, 0.14), random.uniform(-0.05, 0.05), 0])
                ).set_opacity(random.uniform(0.35, 1)),
                glitch_red.animate.move_to(
                    text_group.get_center() + np.array([random.uniform(-0.14, 0.14), random.uniform(-0.05, 0.05), 0])
                ).set_opacity(random.uniform(0.35, 1)),
                run_time=0.055
            )
        self.play(
            glitch_cyan.animate.move_to(text_group).set_opacity(0),
            glitch_red.animate.move_to(text_group).set_opacity(0),
            run_time=0.1
        )
        self.wait(0.45)

        self.clear_updaters_in(warning_bg, *qmarks)
        self.play(
            FadeOut(Group(
                warning_bg, chaos_group, worried, worried_glow, qmarks,
                bg_rect, text_group, glitch_cyan, glitch_red
            ), scale=0.92),
            run_time=0.65
        )

    # ================= 3. 解决方案 =================
    def solution(self):
        # 圆环生长为手机（整体上移，给底部文案留空）
        seed_ring = Circle(radius=0.35, color=TECH_BLUE, stroke_width=4).shift(UP * 0.55)
        seed_glow = self.create_neon_glow(seed_ring, color=TECH_PURPLE, max_width=25)
        self.play(Create(seed_ring), FadeIn(seed_glow), run_time=0.5)
        self.play(
            seed_ring.animate.scale(4.2).set_opacity(0.25),
            FadeOut(seed_glow),
            run_time=0.7, rate_func=ease_out_sine
        )

        border, notch, phone_glow = self.phone_frame(w=2.75, h=5.55)
        phone_shift = UP * 0.55
        border.shift(phone_shift)
        notch.shift(phone_shift)
        phone_glow.shift(phone_shift)

        companion = self.safe_image(ASSETS["art_half"], height=2.15)
        companion.next_to(border, LEFT, buff=0.3).shift(UP * 0.15)
        companion.set_opacity(0)

        self.play(
            ReplacementTransform(seed_ring, border),
            FadeIn(notch), FadeIn(phone_glow),
            companion.animate.set_opacity(0.9),
            run_time=1.1, rate_func=ease_in_out_sine
        )

        left_screen = self.safe_image(ASSETS["home_before"], height=5.15)
        right_screen = self.safe_image(ASSETS["timetable"], height=5.15)
        left_screen.move_to(border.get_center())
        right_screen.move_to(border.get_center() + RIGHT * 5.0)

        scan_line = Line(border.get_corner(UL) + DOWN * 0.22 + RIGHT * 0.1,
                         border.get_corner(UR) + DOWN * 0.22 + LEFT * 0.1,
                         color=GLASS_WHITE, stroke_width=3.5)
        scan_glow = self.create_neon_glow(scan_line, color=TECH_BLUE, layers=3, max_width=12)
        scan = VGroup(scan_glow, scan_line)
        self.add(scan)
        self.play(
            FadeIn(left_screen, scale=0.92),
            scan.animate.move_to(border.get_bottom() + UP * 0.22),
            run_time=1.35, rate_func=smooth
        )
        self.remove(scan)

        slogan1 = self.gradient_title("现在，有鲤工助手。", font_size=34)
        slogan2 = Text(
            "导航 · 课表 · 智能体 · 立绘——收进同一部手机。",
            font=FONT, font_size=22, color=GLASS_WHITE
        )
        slogans = VGroup(slogan1, slogan2).arrange(DOWN, buff=0.18).to_edge(DOWN, buff=0.28)
        self.play(Write(slogan1), FadeIn(slogan2, shift=UP * 0.12), run_time=1.0)
        self.wait(0.35)

        self.play(
            left_screen.animate.shift(LEFT * 5.0).set_opacity(0),
            right_screen.animate.move_to(border.get_center()),
            run_time=0.85, rate_func=ease_out_back
        )
        self.wait(0.55)
        self.play(
            FadeOut(Group(phone_glow, border, notch, left_screen, right_screen, companion, slogans)),
            shift=DOWN * 0.2, run_time=0.7
        )

    # ================= 4. 日常能力蒙太奇 =================
    def features(self):
        # ---- A. 每日签到（画面整体上移，避免与底部配语重叠） ----
        title_a = self.gradient_title("每日签到", font_size=32).to_edge(UP, buff=0.28)
        self.play(Write(title_a), run_time=0.45)

        before = self.safe_image(ASSETS["home_before"], height=4.35)
        after = self.safe_image(ASSETS["home_after"], height=4.35)
        emoji = self.safe_image(ASSETS["emoji_00"], height=1.85)
        before.move_to(LEFT * 2.35 + UP * 0.35)
        after.move_to(RIGHT * 2.2 + UP * 0.35)
        after.set_opacity(0)
        emoji.next_to(after, RIGHT, buff=0.2).shift(UP * 0.1).set_opacity(0)

        hud_b = self.create_hud_corners(
            SurroundingRectangle(before, buff=0.06, stroke_width=0)
        )
        self.play(FadeIn(before, shift=UP * 0.15), Create(hud_b), run_time=0.7)

        loading = Text("签到中…", font=FONT, font_size=24, color=TECH_BLUE)
        loading.next_to(before, DOWN, buff=0.18)
        ring = DashedVMobject(Circle(radius=0.24, color=TECH_PURPLE), num_dashes=12)
        ring.next_to(loading, LEFT, buff=0.12)
        ring.add_updater(lambda m, dt: m.rotate(dt * 4))
        self.play(FadeIn(loading), FadeIn(ring), run_time=0.35)
        self.wait(0.45)
        self.clear_updaters_in(ring)

        caption = Text(EMOJI_CAPTION_00, font=FONT, font_size=18, color=GLASS_WHITE)
        caption_tag = Text("我的华工 · 签到的总是最好的", font=FONT, font_size=16, color=TECH_BLUE)
        cap_group = VGroup(caption, caption_tag).arrange(DOWN, buff=0.1).to_edge(DOWN, buff=0.22)

        self.play(
            FadeOut(loading), FadeOut(ring), FadeOut(hud_b),
            before.animate.scale(0.88).shift(LEFT * 0.55).set_opacity(0.35),
            after.animate.set_opacity(1).move_to(RIGHT * 1.35 + UP * 0.35),
            FadeIn(emoji, scale=0.75),
            FadeIn(cap_group),
            run_time=0.9, rate_func=ease_out_back
        )
        self.wait(0.7)
        self.play(FadeOut(Group(title_a, before, after, emoji, cap_group)), run_time=0.45)

        # ---- B. 校园导航（拓扑收束） ----
        title_b = self.gradient_title("常用服务，少绕弯路。", font_size=30).to_edge(UP, buff=0.3)
        self.play(Write(title_b), run_time=0.4)

        center_node = Dot(radius=0.32, color=GLASS_WHITE)
        center_glow = self.create_neon_glow(center_node, color=TECH_PURPLE, max_width=40)
        center_glow.add_updater(lambda m, dt: m.set_opacity(0.55 + 0.4 * np.sin(self.time * 5)))
        ring1 = DashedVMobject(Circle(radius=1.3, color=TECH_BLUE), num_dashes=18)
        ring1.add_updater(lambda m, dt: m.rotate(dt * 1.1))
        ring2 = DashedVMobject(Circle(radius=1.9, color=TECH_PURPLE), num_dashes=12)
        ring2.add_updater(lambda m, dt: m.rotate(-dt * 0.75))
        phone_mini = self.safe_image(ASSETS["home_after"], height=3.15)
        center_group = Group(center_glow, center_node, ring1, ring2).move_to(RIGHT * 3.2 + UP * 0.25)
        phone_mini.move_to(center_group.get_center())

        nodes = VGroup(*[
            Dot(radius=0.12, color=GLASS_WHITE).move_to([
                random.uniform(-6.5, -0.5), random.uniform(-2.6, 2.6), 0
            ]) for _ in range(10)
        ])
        labels_nav = ["查分", "选课", "VPN", "一卡通", "教务", "知网", "地图", "资料", "GPA", "雨课"]
        node_labels = VGroup(*[
            Text(labels_nav[i], font=FONT, font_size=14, color=TECH_BLUE)
            .next_to(nodes[i], UP, buff=0.08)
            for i in range(len(nodes))
        ])
        self.play(
            LaggedStart(*[FadeIn(n, scale=0) for n in nodes], lag_ratio=0.04),
            FadeIn(node_labels),
            run_time=0.7
        )
        lines = VGroup(*[
            Line(n.get_center(), center_node.get_center(),
                 color=TECH_BLUE, stroke_opacity=0.28, stroke_width=1.8)
            for n in nodes
        ])
        self.play(
            FadeIn(center_group, scale=0.5), FadeIn(phone_mini, scale=0.85),
            Create(lines), run_time=1.1, rate_func=smooth
        )
        packets = VGroup(*[Dot(radius=0.07, color=GLASS_WHITE).move_to(n.get_center()) for n in nodes])
        self.add(packets)
        self.play(
            *[MoveAlongPath(packets[i], Line(nodes[i].get_center(), center_node.get_center()))
              for i in range(len(nodes))],
            run_time=1.0, rate_func=ease_in_out_sine
        )
        self.play(Flash(center_node, color=TECH_PURPLE, line_length=1.6, num_lines=16), run_time=0.45)
        self.wait(0.35)
        self.clear_updaters_in(center_glow, ring1, ring2)
        self.play(FadeOut(Group(title_b, nodes, node_labels, lines, center_group, phone_mini, packets)), run_time=0.45)

        # ---- C. 课表双屏（上移，标题与卡片不挤） ----
        title_c = self.gradient_title("课表在手机里，不在收藏夹迷宫里。", font_size=26).to_edge(UP, buff=0.28)
        left = self.safe_image(ASSETS["timetable"], height=4.55)
        right = self.safe_image(ASSETS["import_tt"], height=4.55)
        cards = Group(left, right).arrange(RIGHT, buff=0.55).shift(UP * 0.2)
        huds = VGroup(*[self.create_hud_corners(
            SurroundingRectangle(c, buff=0.05, stroke_width=0)
        ) for c in cards])
        self.play(
            Write(title_c),
            LaggedStart(*[GrowFromCenter(c) for c in cards], lag_ratio=0.18),
            LaggedStart(*[Create(h) for h in huds], lag_ratio=0.18),
            run_time=1.2, rate_func=ease_out_back
        )
        self.wait(0.85)
        self.play(FadeOut(Group(title_c, cards, huds)), run_time=0.5)

    # ================= 5. Agent 高光三连击 =================
    def _phone_shot(self, path, height=5.5):
        """截图 + 霓虹手机框 + HUD 角，便于真机演示图登场。"""
        img = self.safe_image(path, height=height)
        border = RoundedRectangle(
            corner_radius=0.28, width=img.width + 0.18, height=img.height + 0.18,
            color=TECH_BLUE, stroke_width=2.5, fill_opacity=0
        ).move_to(img)
        glow = self.create_neon_glow(border, color=TECH_BLUE, max_width=16)
        hud = self.create_hud_corners(border, padding=0.12, length=0.4, stroke_width=2.5)
        return Group(glow, border, hud, img)

    def agent_showcase(self):
        """真机演示图驱动：演示0=跳转+读表，演示1=华工知识库。"""
        rain = VGroup()
        for _ in range(16):
            length = random.randint(6, 12)
            col = VGroup(*[
                Text(
                    random.choice(["0", "1", "A", "X", "$"]),
                    font="Courier", font_size=14, weight=BOLD,
                    color=GLASS_WHITE if j == 0 else TECH_BLUE
                ).set_opacity(max(0.12, 1 - j / length * 1.4))
                for j in range(length)
            ]).arrange(DOWN, buff=0.08)
            col.move_to([random.uniform(-7, 7), random.uniform(2.5, 7), 0])
            col.speed = random.uniform(2.0, 4.2)
            col.add_updater(lambda m, dt: m.shift(DOWN * dt * m.speed))
            def _wrap(m, dt):
                if m.get_top()[1] < -5:
                    m.shift(UP * random.uniform(10, 13))
            col.add_updater(_wrap)
            rain.add(col)
        self.add(rain)
        self.play(FadeIn(rain), run_time=0.45)

        section = self.gradient_title("华工智能体 · 能聊天，更能办事", font_size=34)
        section.to_edge(UP, buff=0.28)
        self.play(Write(section), run_time=0.5)

        # 欢迎页
        welcome = self._phone_shot(ASSETS["agent"], height=5.2)
        welcome.shift(DOWN * 0.15)
        tip0 = Text("可以说「打开课表」「今天有什么课」「我要选课」…",
                    font=FONT, font_size=20, color=TECH_BLUE)
        tip0.to_edge(DOWN, buff=0.32)
        self.play(FadeIn(welcome, scale=0.92), FadeIn(tip0), run_time=0.75)
        self.wait(0.45)

        # ----- Beat ①②：Agent功能演示0（选课跳转 + 今日课表） -----
        demo0 = self._phone_shot(ASSETS["agent_demo_0"], height=5.2)
        demo0.shift(DOWN * 0.15)
        cap1 = self.gradient_title("对话即跳转：我要选课 → 打开页面", font_size=26)
        cap1.to_edge(DOWN, buff=0.32)
        tag1 = Text("action: open_campus_web", font="Courier", font_size=14,
                   color=TECH_PURPLE).set_opacity(0.75)
        tag1.next_to(section, DOWN, buff=0.12)

        self.play(
            FadeOut(welcome), FadeOut(tip0),
            FadeIn(demo0, scale=0.94), FadeIn(cap1), FadeIn(tag1),
            run_time=0.7, rate_func=ease_out_back
        )
        self.play(Flash(demo0[-1], color=TECH_BLUE, line_length=0.4, flash_radius=2.4), run_time=0.4)
        self.wait(0.85)

        # 课表 Tab 补充「也能打开课表」
        tt = self._phone_shot(ASSETS["timetable"], height=5.0)
        tt.shift(DOWN * 0.1)
        jump = Text("→ 也能一键打开课表 Tab", font=FONT, font_size=24,
                   color=SOFT_GREEN, weight=BOLD).to_edge(DOWN, buff=0.32)
        self.play(
            FadeOut(demo0), FadeOut(cap1), FadeOut(tag1),
            FadeIn(tt, shift=RIGHT * 0.2), FadeIn(jump),
            run_time=0.65
        )
        self.wait(0.55)

        # 回到演示0，强调读表
        demo0b = self._phone_shot(ASSETS["agent_demo_0"], height=5.2)
        demo0b.shift(DOWN * 0.15)
        cap2 = Text("读懂你的课表：我今天什么课？", font=FONT, weight=BOLD,
                    font_size=26, color=GLASS_WHITE)
        tip2 = Text("课表在你手机里——Agent 按你的数据答，不编造。",
                    font=FONT, font_size=18, color=TECH_BLUE)
        caps2 = VGroup(cap2, tip2).arrange(DOWN, buff=0.12).to_edge(DOWN, buff=0.28)

        nonsense = Text("根据一般大学生作息……", font=FONT, font_size=22, color=WARNING_RED)
        nonsense.move_to(UP * 2.4)
        cross = VGroup(
            Line(LEFT * 1.5, RIGHT * 1.5, color=WARNING_RED, stroke_width=3),
            Line(LEFT * 1.5, RIGHT * 1.5, color=WARNING_RED, stroke_width=3).rotate(PI / 2),
        ).move_to(nonsense).scale(0.5)

        self.play(FadeOut(tt), FadeOut(jump), FadeIn(demo0b), FadeIn(caps2), run_time=0.6)
        self.play(FadeIn(nonsense), run_time=0.25)
        self.play(Create(cross), nonsense.animate.set_opacity(0.35), run_time=0.3)
        self.play(FadeOut(nonsense), FadeOut(cross), run_time=0.25)
        self.wait(0.9)

        # ----- Beat ③：Agent功能演示1（华工知识库） -----
        demo1 = self._phone_shot(ASSETS["agent_demo_1"], height=5.2)
        demo1.shift(DOWN * 0.15)
        cap3 = self.gradient_title("华工知识库，拒绝空心客服", font_size=28)
        cap3.to_edge(DOWN, buff=0.45)
        bad = Text("请咨询贵校教务处。", font=FONT, font_size=20, color=WARNING_RED)
        bad_box = SurroundingRectangle(bad, color=WARNING_RED, buff=0.12, stroke_width=1.5)
        bad_g = Group(bad_box, bad).next_to(section, DOWN, buff=0.15)
        gold = Text("懂华工的智能体，不是万能复读机。", font=FONT, weight=BOLD,
                    font_size=22, color=SOFT_GREEN)
        gold.next_to(cap3, UP, buff=0.12)

        self.play(
            FadeOut(demo0b), FadeOut(caps2),
            FadeIn(demo1, scale=0.94), FadeIn(cap3), FadeIn(bad_g),
            run_time=0.7
        )
        self.play(bad_g.animate.set_opacity(0.2), FadeIn(gold), run_time=0.55)
        self.wait(1.0)

        close = self.gradient_title("跳转 · 读表 · 知识库——能聊天，更能办事。", font_size=26)
        close.move_to(ORIGIN)
        self.clear_updaters_in(*rain)
        self.play(
            FadeOut(Group(section, rain, demo1, cap3, bad_g, gold)),
            FadeIn(close, scale=0.92),
            run_time=0.7
        )
        self.wait(0.65)
        self.play(FadeOut(close), run_time=0.35)

    # ================= 6. 立绘与表情包 =================
    def art_gallery(self):
        title = self.gradient_title("她有一张脸，也有十六种心情。", font_size=32)
        sub = Text("立绘鉴赏 · Emoji 表情包——华工日常的情绪备份。",
                   font=FONT, font_size=20, color=GLASS_WHITE)
        head = VGroup(title, sub).arrange(DOWN, buff=0.2).to_edge(UP, buff=0.3)
        self.play(Write(title), FadeIn(sub), run_time=0.7)

        # 关于立绘理念
        about = self.safe_image(ASSETS["art_about"], height=4.6)
        about.shift(DOWN * 0.15)
        quotes = VGroup(*[
            Text(t, font=FONT, font_size=20, color=TECH_BLUE)
            for t in [
                "不迎合千篇一律的网红脸。",
                "更中国人的鹅蛋脸骨架 · 清新校园穿搭。",
                "真实、慵懒、舒适——希望你喜欢这种风格。",
            ]
        ]).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        quotes.next_to(about, RIGHT, buff=0.45)
        self.play(FadeIn(about, shift=RIGHT * 0.2), LaggedStart(*[
            FadeIn(q, shift=RIGHT * 0.25) for q in quotes
        ], lag_ratio=0.25), run_time=1.2)
        self.wait(0.7)
        self.play(FadeOut(about), FadeOut(quotes), run_time=0.4)

        # Emoji 4×4 全套 00～15（统一缩略尺寸，整体居中）
        gate = self.safe_image(ASSETS["emoji_gate"], height=4.6)
        emoji_keys = [f"emoji_{i:02d}" for i in range(16)]
        emoji_cells = [
            self.safe_image(ASSETS[k], height=1.28) for k in emoji_keys
        ]
        rows = []
        for r in range(4):
            row = Group(*emoji_cells[r * 4:(r + 1) * 4]).arrange(RIGHT, buff=0.14)
            rows.append(row)
        emojis = Group(*rows).arrange(DOWN, buff=0.14).shift(DOWN * 0.15)
        # 略缩放保证四边留白
        if emojis.width > 12.5:
            emojis.scale_to_fit_width(12.5)
        if emojis.height > 5.6:
            emojis.scale_to_fit_height(5.6)

        self.play(FadeIn(gate, scale=0.95), run_time=0.5)
        self.wait(0.3)
        self.play(FadeOut(gate), FadeIn(emojis, shift=UP * 0.1), run_time=0.6)
        self.play(emojis.animate.scale(1.03), run_time=0.45, rate_func=there_and_back)
        self.wait(0.45)
        self.play(FadeOut(emojis), run_time=0.35)

        # 草图 → 半身 → 全身
        sketch = self.safe_image(ASSETS["art_sketch_half"], height=4.8)
        half = self.safe_image(ASSETS["art_half"], height=4.8)
        full = self.safe_image(ASSETS["art_full"], height=5.2)
        for img in (sketch, half, full):
            img.shift(DOWN * 0.2)

        # 不同分辨率立绘不能用 ReplacementTransform（像素数组形状必须一致）
        label_s = Text("手绘草图", font=FONT, font_size=22, color=TECH_PURPLE).next_to(sketch, DOWN, buff=0.15)
        self.play(FadeIn(sketch), FadeIn(label_s), run_time=0.55)
        self.wait(0.4)
        label_h = Text("半身立绘", font=FONT, font_size=22, color=TECH_BLUE).next_to(half, DOWN, buff=0.15)
        self.play(
            FadeOut(sketch), FadeOut(label_s),
            FadeIn(half), FadeIn(label_h),
            run_time=0.7
        )
        self.wait(0.45)
        label_f = Text("全身立绘", font=FONT, font_size=22, color=SOFT_GREEN).next_to(full, DOWN, buff=0.1)
        self.play(
            FadeOut(half), FadeOut(label_h),
            FadeIn(full),
            run_time=0.75
        )
        glow_f = self.create_neon_glow(
            SurroundingRectangle(full, buff=0.08, color=TECH_PURPLE, stroke_width=2),
            color=TECH_PURPLE, max_width=20
        )
        self.play(FadeIn(label_f), FadeIn(glow_f), run_time=0.45)
        self.wait(0.7)
        self.play(FadeOut(Group(head, full, label_f, glow_f)), run_time=0.55)

    # ================= 7. CTA =================
    def call_to_action(self):
        qr_box = RoundedRectangle(
            corner_radius=0.2, width=3.3, height=3.3,
            color=TECH_BLUE, stroke_width=2, fill_color=TECH_BG, fill_opacity=0.85
        )
        qr = self.safe_image(ASSETS["qr"], height=2.85).move_to(qr_box)
        qr_glow = self.create_neon_glow(qr_box, color=TECH_BLUE, max_width=22)
        lock = self.create_hud_corners(qr_box, padding=0.28, length=0.55, stroke_width=4)
        group = Group(qr_glow, qr_box, qr)
        self.play(FadeIn(group, scale=0.55), Create(lock), run_time=0.9, rate_func=ease_out_back)

        scan_line = Line(lock.get_left() + LEFT * 0.4, lock.get_right() + RIGHT * 0.4,
                         color=TECH_PURPLE, stroke_width=3)
        scan_g = self.create_neon_glow(scan_line, color=TECH_PURPLE, layers=4, max_width=14)
        scan = VGroup(scan_g, scan_line).move_to(lock.get_top())
        self.add(scan)
        self.play(scan.animate.move_to(lock.get_bottom()), run_time=1.35, rate_func=there_and_back)
        self.remove(scan)

        download = Text("立即下载，让华工日常少一点折腾。", font=FONT, weight=BOLD,
                        font_size=30, color=GLASS_WHITE)
        download.next_to(lock, DOWN, buff=0.7)
        self.play(Write(download), run_time=0.9)
        self.wait(1.0)
        self.play(FadeOut(group), FadeOut(lock), FadeOut(download), scale=0.85, run_time=0.55)

    # ================= 8. 结尾 =================
    def outro(self):
        # 左侧半身立绘（不用 Logo icon）+ 右侧全身点缀可选：按需求仅半身居中偏左
        half = self.safe_image(ASSETS["art_half"], height=4.8)
        half.shift(LEFT * 2.4 + UP * 0.25)
        slogan = self.gradient_title("连接你的世界", font_size=44)
        slogan.move_to(RIGHT * 2.0 + UP * 0.55)
        tiny = Text("华南理工大学学生校园助手", font=FONT, font_size=18, color=TECH_BLUE)
        tiny.next_to(slogan, DOWN, buff=0.28)

        particles = VGroup()
        for _ in range(120):
            r = random.uniform(0.012, 0.045)
            dot = Dot(radius=r, color=TECH_BLUE).move_to([
                random.uniform(-7.5, 7.5), random.uniform(-4.2, 4.2), 0
            ])
            dot.set_opacity(min(1, r * 18))
            speed = r
            dot.add_updater(lambda m, dt, s=speed: m.shift(RIGHT * dt * s * 45 + UP * dt * s * 18))
            def wrap(m, dt):
                c = m.get_center()
                if c[0] > 8 or c[1] > 5:
                    m.move_to([random.uniform(-8, 8), -4.5, 0])
            dot.add_updater(wrap)
            particles.add(dot)

        wave = Circle(radius=0.12, color=TECH_PURPLE, stroke_width=9)
        self.play(FadeIn(half, scale=0.9), FadeIn(particles), run_time=1.2)
        self.play(
            wave.animate.scale(90).set_stroke(width=0).set_opacity(0),
            Write(slogan), FadeIn(tiny),
            run_time=1.6, rate_func=ease_out_sine
        )
        final = Group(half, slogan, tiny)
        self.play(final.animate.scale(1.05).shift(UP * 0.1), run_time=2.2, rate_func=linear)
        self.clear_updaters_in(*particles)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=1.1)
        self.wait(0.25)

    # ================= 9. 致谢 =================
    def credits(self):
        bg = Rectangle(width=16, height=9, color=BLACK, fill_opacity=0.82, stroke_width=0)
        self.play(FadeIn(bg), run_time=0.55)
        developer = Text("本软件由 moon_explorer 开发", font=FONT, font_size=36,
                         weight=BOLD, color=GLASS_WHITE)
        association = Text("属于华工嵌入式协会", font=FONT, font_size=30, color=TECH_BLUE)
        group = VGroup(developer, association).arrange(DOWN, buff=0.45)
        glow = self.create_neon_glow(
            SurroundingRectangle(group, buff=0.35, color=TECH_PURPLE, stroke_width=1.5),
            color=TECH_PURPLE, max_width=18, layers=3
        )
        self.play(FadeIn(glow), Write(developer), Write(association), run_time=1.6)
        self.wait(1.6)
        self.play(FadeOut(glow), FadeOut(group), FadeOut(bg), run_time=1.1)
