from manim import *
import numpy as np
import random

# ================= 全局科技风配色方案 =================
TECH_BLUE = "#00F0FF"
TECH_PURPLE = "#8A2BE2"
TECH_BG = "#0A0A12"
WARNING_RED = "#FF3366"
CYAN_GLITCH = "#00FFFF"
GLASS_WHITE = "#FFFFFF"

class LiGongAssistant(Scene):
    def construct(self):
        # 设置沉浸式深色背景
        self.camera.background_color = TECH_BG
        
        # 1. 开场 (0:00–0:12) 全息系统启动 & 终端加载
        self.intro()

        # 2. 问题引入 (0:12–0:28) 混乱与报错 (Glitch效果)
        self.problem()

        # 3. 解决方案 (0:28–0:45) 终端降临 & 扫描
        self.solution()

        # 4. 核心功能展示 (0:45–1:00) 悬浮卡片 & HUD边框
        self.features()

        # 5. 快速导航 (1:00–1:15) 拓扑重构 & 雷达波
        self.navigation()

        # 6. 科技优势 (1:15–1:35) 持续代码雨
        self.tech_advantages()

        # 7. 号召行动 (1:35–1:45) 瞄准锁定
        self.call_to_action()

        # 8. 结尾 (1:45–1:50) 品牌升华
        self.outro()

    # ================= 辅助函数区 =================
    def safe_image(self, path, width=3, height=6):
        """如果找不到图片文件，生成一个炫酷的科技全息占位符"""
        try:
            img = ImageMobject(path)
            img.scale_to_fit_height(height)
            return img
        except Exception:
            placeholder = RoundedRectangle(corner_radius=0.2, width=width, height=height, 
                                         color=TECH_BLUE, fill_opacity=0.1)
            cross = VGroup(
                Line(placeholder.get_corner(UL), placeholder.get_corner(DR), color=TECH_BLUE, stroke_opacity=0.3),
                Line(placeholder.get_corner(UR), placeholder.get_corner(DL), color=TECH_BLUE, stroke_opacity=0.3)
            )
            text = Text("ASSET MISSING", font="Courier", font_size=16, color=TECH_BLUE).move_to(placeholder.get_center())
            return Group(placeholder, cross, text) # 兼容混搭

    def create_hud_corners(self, mobject, padding=0.2, length=0.4, stroke_width=3):
        """为物体生成极客风格的四个瞄准边角"""
        ul = mobject.get_corner(UL) + np.array([-padding, padding, 0])
        ur = mobject.get_corner(UR) + np.array([padding, padding, 0])
        dl = mobject.get_corner(DL) + np.array([-padding, -padding, 0])
        dr = mobject.get_corner(DR) + np.array([padding, -padding, 0])

        corners = VGroup(
            VGroup(Line(ul, ul + RIGHT*length), Line(ul, ul + DOWN*length)),
            VGroup(Line(ur, ur + LEFT*length), Line(ur, ur + DOWN*length)),
            VGroup(Line(dl, dl + RIGHT*length), Line(dl, dl + UP*length)),
            VGroup(Line(dr, dr + LEFT*length), Line(dr, dr + UP*length)),
        )
        corners.set_stroke(color=TECH_BLUE, width=stroke_width)
        return corners

    # ================= 1. 开场 =================
    def intro(self):
        # 极客元素：左上角命令行滚动加载
        cmd_lines = VGroup(*[Text(f"> {txt}", font="Courier", font_size=14, color=TECH_BLUE) for txt in [
            "INITIALIZING KERNEL...", "MOUNTING VIRTUAL DOM...", "BYPASSING FIREWALL...", "SYSTEM ONLINE."
        ]]).arrange(DOWN, aligned_edge=LEFT).to_corner(UL)
        
        self.play(LaggedStart(*[AddTextLetterByLetter(line) for line in cmd_lines], lag_ratio=0.5), run_time=1.5)

        # 雷达网格底纹
        grid = NumberPlane(background_line_style={"stroke_color": TECH_BLUE, "stroke_opacity": 0.1}, 
                           faded_line_style={"stroke_color": TECH_BLUE, "stroke_opacity": 0.05})
        self.play(Create(grid), run_time=1.5, rate_func=smooth)

        # 核心全息环
        rings = VGroup(*[Circle(radius=r, color=TECH_BLUE, stroke_opacity=1-r/5).set_style(stroke_width=2) for r in np.arange(0.5, 6, 0.8)])
        self.play(LaggedStart(*[Create(ring) for ring in rings], lag_ratio=0.1), run_time=1, rate_func=exponential_decay)
        self.play(Rotate(rings, PI/2), run_time=1.5, rate_func=linear)

        # Logo 与光晕
        logo = self.safe_image("assets/logo.png", width=2, height=2)
        logo.scale(0.8)
        glow = Circle(radius=1.5, color=TECH_PURPLE, fill_opacity=0.2, stroke_width=0).add_updater(
            lambda m, dt: m.scale(1 + 0.05 * np.sin(self.time * 5)) 
        )
        
        self.play(FadeIn(glow), FadeIn(logo, scale=0.1), run_time=1.2, rate_func=smooth)

        title = Text("鲤工助手", font="Microsoft YaHei", weight=BOLD).scale(1.5)
        title.set_color(color=[TECH_BLUE, TECH_PURPLE])
        title.next_to(logo, DOWN, buff=0.5)
        
        self.play(AddTextLetterByLetter(title), run_time=0.8)
        self.play(Flash(title, color=TECH_BLUE, line_length=0.4, num_lines=20), run_time=0.5)
        self.wait(0.5)

        # 退出动画，清理updater
        glow.clear_updaters()
        self.play(
            LaggedStart(
                FadeOut(grid), FadeOut(cmd_lines), FadeOut(rings, scale=1.5), 
                FadeOut(glow), FadeOut(logo, shift=UP), FadeOut(title, shift=DOWN),
                lag_ratio=0.1
            ), run_time=1
        )

    # ================= 2. 问题引入 =================
    def problem(self):
        # 屏幕红光警报器
        warning_bg = Rectangle(width=15, height=9, color=WARNING_RED, fill_opacity=0.1, stroke_width=0)
        warning_bg.add_updater(lambda m, dt: m.set_opacity(0.1 + 0.05 * np.sin(self.time * 10)))
        self.add(warning_bg)

        # 生成报错代码块
        chaos_group = VGroup()
        for _ in range(15):
            frag = RoundedRectangle(corner_radius=0.1, width=random.uniform(0.5, 2.0), height=random.uniform(0.3, 0.8))
            frag.set_style(stroke_color=WARNING_RED, stroke_opacity=0.8, fill_color=TECH_BG, fill_opacity=0.9)
            # 随机加点十六进制乱码
            hex_txt = Text(hex(random.randint(4096, 65535)), font="Courier", font_size=12, color=WARNING_RED).move_to(frag)
            chaos_group.add(VGroup(frag, hex_txt).move_to([random.uniform(-6, 6), random.uniform(-3, 3), 0]))

        self.play(LaggedStart(*[FadeIn(f, scale=0.5) for f in chaos_group], lag_ratio=0.02), run_time=1)
        
        text1 = Text("信息碎片化，网站杂乱无章？", font="Microsoft YaHei", font_size=36, color=GLASS_WHITE)
        text2 = Text("找不到课表，办事效率低下？", font="Microsoft YaHei", font_size=36, color=WARNING_RED)
        text_group = VGroup(text1, text2).arrange(DOWN, buff=0.4).move_to(ORIGIN)

        bg_rect = Rectangle(width=10, height=3, color=TECH_BG, fill_opacity=0.9, stroke_width=2, stroke_color=WARNING_RED)
        
        # RGB 色差层 (Glitch)
        glitch_cyan = text_group.copy().set_color(CYAN_GLITCH).shift(LEFT*0.05 + UP*0.05)
        glitch_red = text_group.copy().set_color(WARNING_RED).shift(RIGHT*0.05 + DOWN*0.05)

        self.play(FadeIn(bg_rect), FadeIn(glitch_cyan), FadeIn(glitch_red), Write(text_group), run_time=0.5)
        
        # 剧烈震动与闪烁
        for _ in range(3):
            self.play(
                text_group.animate.shift(RIGHT*0.2).set_opacity(0.8),
                glitch_cyan.animate.shift(LEFT*0.3).set_opacity(1),
                glitch_red.animate.shift(RIGHT*0.3).set_opacity(1),
                run_time=0.05
            )
            self.play(
                text_group.animate.shift(LEFT*0.2).set_opacity(1),
                glitch_cyan.animate.shift(RIGHT*0.3).set_opacity(0.3),
                glitch_red.animate.shift(LEFT*0.3).set_opacity(0.3),
                run_time=0.05
            )

        self.wait(0.5)
        warning_bg.clear_updaters()
        self.play(*[FadeOut(mob) for mob in [warning_bg, chaos_group, bg_rect, text_group, glitch_cyan, glitch_red]], run_time=0.6)

    # ================= 3. 解决方案 =================
    def solution(self):
        # 终端骨架生成
        phone_border = RoundedRectangle(corner_radius=0.4, width=3.2, height=6.5, color=TECH_BLUE, stroke_width=2)
        phone_glow = phone_border.copy().set_stroke(TECH_BLUE, width=10, opacity=0.3)
        notch = RoundedRectangle(corner_radius=0.1, width=1.0, height=0.2, color=TECH_BLUE).move_to(phone_border.get_top() + DOWN*0.15)
        phone = VGroup(phone_glow, phone_border, notch)

        self.play(Create(phone_border), FadeIn(phone_glow), FadeIn(notch), run_time=1, rate_func=smooth)
        self.play(phone.animate.set_fill(TECH_BG, opacity=1), run_time=0.5)

        left_screen = self.safe_image("assets/首页.jpg", width=2.8, height=5.6)
        right_screen = self.safe_image("assets/课表.jpg", width=2.8, height=5.6)
        
        left_screen.move_to(phone.get_center())
        right_screen.move_to(phone.get_center() + RIGHT * 4)

        # 扫描光线效
        scan_line = Line(phone.get_corner(UL), phone.get_corner(UR), color=TECH_BLUE, stroke_width=3)
        self.add(scan_line)
        self.play(
            FadeIn(left_screen, scale=0.9),
            scan_line.animate.move_to(phone.get_bottom()), 
            run_time=1, rate_func=smooth
        )
        self.remove(scan_line)
        
        slogan = Text("鲤工助手 · 一切井然有序", font="Microsoft YaHei", font_size=32, color=TECH_BLUE)
        slogan.to_edge(DOWN, buff=0.8)
        self.play(Write(slogan))
        self.wait(0.5)

        # 平滑滑屏
        self.play(
            left_screen.animate.shift(LEFT * 4),
            right_screen.animate.move_to(phone.get_center()),
            run_time=0.8, rate_func=smooth
        )
        self.wait(0.5)
        self.play(FadeOut(phone), FadeOut(left_screen), FadeOut(right_screen), FadeOut(slogan))

    # ================= 4. 核心功能展示 =================
    def features(self):
        features_data = [
            ("每日签到", "assets/首页.jpg"),
            ("聚合导航", "assets/用户.jpg"),
            ("定制课表", "assets/课表.jpg")
        ]
        
        cards = Group()
        huds = VGroup()
        for name, img_path in features_data:
            card_bg = RoundedRectangle(corner_radius=0.2, width=3.5, height=5, color=TECH_BLUE, stroke_opacity=0.3, fill_color=TECH_BG, fill_opacity=0.9)
            img = self.safe_image(img_path, width=3.2, height=4)
            img.next_to(card_bg.get_top(), DOWN, buff=0.15)
            title = Text(name, font="Microsoft YaHei", font_size=24, color=GLASS_WHITE).next_to(img, DOWN, buff=0.2)
            
            card = Group(card_bg, img, title)
            cards.add(card)

        cards.arrange(RIGHT, buff=0.8).move_to(ORIGIN)

        # 为每个卡片生成HUD边框
        for card in cards:
            huds.add(self.create_hud_corners(card[0]))

        self.play(
            LaggedStart(*[FadeIn(card, shift=UP) for card in cards], lag_ratio=0.2), 
            LaggedStart(*[Create(hud) for hud in huds], lag_ratio=0.2),
            run_time=1.5, rate_func=smooth
        )

        # 锁定中间卡片高亮
        self.play(
            cards[1].animate.scale(1.1),
            huds[1].animate.scale(1.1).set_stroke(TECH_PURPLE, width=5),
            run_time=0.5
        )
        self.play(
            cards[1].animate.scale(1/1.1),
            huds[1].animate.scale(1/1.1).set_stroke(TECH_BLUE, width=3),
            run_time=0.5
        )

        self.wait(0.5)
        self.play(FadeOut(cards, shift=DOWN), FadeOut(huds, scale=1.5))

    # ================= 5. 快速导航 =================
    def navigation(self):
        # 中心枢纽节点
        center_node = Dot(radius=0.3, color=TECH_PURPLE)
        center_glow = Circle(radius=0.6, color=TECH_BLUE, fill_opacity=0.3, stroke_width=0)
        # 旋转的虚线环
        dashed_ring = DashedVMobject(Circle(radius=1.2, color=TECH_BLUE), num_dashes=15)
        dashed_ring.add_updater(lambda m, dt: m.rotate(dt * 2))
        
        center_group = Group(center_glow, center_node, dashed_ring).move_to(RIGHT*3)
        
        nodes = VGroup(*[Dot(radius=0.15, color=GLASS_WHITE).move_to([random.uniform(-6, 0), random.uniform(-3, 3), 0]) for _ in range(8)])
        self.play(FadeIn(nodes), run_time=0.5)

        lines = VGroup()
        animations = []
        for i, node in enumerate(nodes):
            angle = PI/2 + (i/7) * PI
            target_pos = center_node.get_center() + np.array([np.cos(angle)*3, np.sin(angle)*3, 0])
            line = Line(center_node.get_center(), target_pos, color=TECH_BLUE, stroke_opacity=0.4)
            lines.add(line)
            animations.append(node.animate.move_to(target_pos).set_color(TECH_BLUE))
            
        self.play(FadeIn(center_group), *animations, run_time=1.5, rate_func=smooth)
        self.play(Create(lines), run_time=1)

        # 高速数据流光点
        pulses = VGroup(*[Dot(radius=0.08, color=GLASS_WHITE).move_to(node.get_center()) for node in nodes])
        self.play(FadeIn(pulses), run_time=0.2)
        self.play(*[MoveAlongPath(pulse, Line(node.get_center(), center_node.get_center())) for pulse, node in zip(pulses, nodes)], run_time=0.8)
        
        text = Text("一键直达，万物互联", font="Microsoft YaHei", font_size=36, color=TECH_BLUE).to_edge(DOWN, buff=1)
        self.play(FadeOut(pulses), Flash(center_node, color=TECH_PURPLE, line_length=1.5, num_lines=12), Write(text))
        
        self.wait(1)
        dashed_ring.clear_updaters()
        self.play(*[FadeOut(mob) for mob in [nodes, lines, center_group, text]])

    # ================= 6. 科技优势 =================
    def tech_advantages(self):
        # 真正的无尽代码雨
        data_group = VGroup()
        for i in range(15):
            binary_str = "".join([random.choice(["0", "1", "X", "$", "%"]) for _ in range(20)])
            code = Text(binary_str, font="Courier", font_size=14, color=TECH_BLUE, fill_opacity=random.uniform(0.2, 0.6))
            code.rotate(PI/2).move_to([random.uniform(-7, 7), random.uniform(2, 6), 0])
            
            # 让每一列独立往下掉，掉到底部重置
            code.speed = random.uniform(1.5, 3.5)
            code.add_updater(lambda m, dt: m.shift(DOWN * dt * m.speed))
            def wrap_around(m, dt):
                if m.get_top()[1] < -4:
                    m.move_to([m.get_center()[0], 6, 0])
            code.add_updater(wrap_around)
            
            data_group.add(code)
        
        self.add(data_group)
        self.play(FadeIn(data_group), run_time=1)
        
        panel = RoundedRectangle(corner_radius=0.3, width=10, height=4.5, color=TECH_BLUE, stroke_opacity=0.8, fill_color=TECH_BG, fill_opacity=0.85)
        # 面板四角装饰
        panel_hud = self.create_hud_corners(panel, padding=0.1, length=0.8, stroke_width=4)
        
        title = Text("尖端科技 · 驱动智慧校园", font="Microsoft YaHei", font_size=36, color=TECH_BLUE).move_to(panel.get_top() + DOWN*0.6)
        
        items = VGroup(
            Text("▶ 专属华工生态：贴吧 / 二手 / 评课", font="Microsoft YaHei", font_size=28, color=GLASS_WHITE),
            Text("▶ AI Agent：全天候对话即服务", font="Microsoft YaHei", font_size=28, color=GLASS_WHITE),
            Text("▶ 极客体验：仿 OpenClaw / 千文点外卖", font="Microsoft YaHei", font_size=28, color=GLASS_WHITE)
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.4).next_to(title, DOWN, buff=0.6).shift(RIGHT*0.5)

        self.play(FadeIn(panel, scale=0.9), Create(panel_hud), Write(title), run_time=1)
        self.play(LaggedStart(*[FadeIn(item, shift=RIGHT*0.5) for item in items], lag_ratio=0.3), run_time=1.5)

        self.wait(1.5)
        
        for code in data_group:
            code.clear_updaters()
            
        self.play(FadeOut(data_group), FadeOut(panel), FadeOut(panel_hud), FadeOut(title), FadeOut(items), shift=UP)
    
    # ================= 7. 号召行动 =================
    def call_to_action(self):
        qr_box = RoundedRectangle(corner_radius=0.2, width=3, height=3, color=TECH_BLUE, stroke_width=2)
        qr_img = self.safe_image("assets/二维码.png", width=2.8, height=2.8).move_to(qr_box.get_center())
        qr_group = Group(qr_box, qr_img)
        
        # 二维码锁定器
        lock_hud = self.create_hud_corners(qr_box, padding=0.3, length=0.6)
        
        self.play(FadeIn(qr_group, scale=0.8), Create(lock_hud), run_time=1)

        # 扫描效果
        scan_line = Line(lock_hud.get_left(), lock_hud.get_right(), color=TECH_PURPLE, stroke_width=4)
        scan_glow = scan_line.copy().set_stroke(TECH_PURPLE, width=12, opacity=0.4)
        scan = VGroup(scan_glow, scan_line).move_to(lock_hud.get_top())
        
        self.add(scan)
        self.play(scan.animate.move_to(lock_hud.get_bottom()), run_time=1.5, rate_func=there_and_back)
        self.remove(scan)

        download = Text("立即下载 · 开启高效之旅", font="Microsoft YaHei", font_size=32, color=GLASS_WHITE)
        platforms = Text("App Store  |  Google Play  |  Android", font="Microsoft YaHei", font_size=20, color=TECH_PURPLE)
        info = VGroup(download, platforms).arrange(DOWN, buff=0.3).next_to(lock_hud, DOWN, buff=0.8)

        self.play(Write(download), FadeIn(platforms, shift=UP*0.2), run_time=1)
        self.wait(1.5)
        self.play(FadeOut(qr_group), FadeOut(lock_hud), FadeOut(info))

    # ================= 8. 结尾 =================
    def outro(self):
        logo = self.safe_image("assets/logo.png", width=3, height=3).move_to(ORIGIN)
        slogan = Text("连接你的世界", font="Microsoft YaHei", font_size=40, weight=BOLD)
        slogan.set_color(color=[TECH_BLUE, TECH_PURPLE]).next_to(logo, DOWN, buff=0.8)
        
        particles = VGroup(*[Dot(radius=random.uniform(0.01, 0.04), color=TECH_BLUE).move_to([random.uniform(-7, 7), random.uniform(-4, 4), 0]) for _ in range(120)])
        
        # 背景波纹扩散
        wave = Circle(radius=0.1, color=TECH_PURPLE, stroke_width=8)
        self.play(FadeIn(logo, scale=0.5), run_time=1.2)
        
        self.play(
            wave.animate.scale(80).set_opacity(0), 
            Write(slogan), 
            FadeIn(particles), 
            run_time=1.5
        )
        
        final_ui = Group(logo, slogan, particles)
        
        # 最后的镜头推近效果
        self.play(final_ui.animate.scale(1.1).shift(UP*0.2), run_time=3, rate_func=linear)
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=1)
        self.wait(0.5)