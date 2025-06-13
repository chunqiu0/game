import pygame
import sys
import random
import json
import os

# 初始化pygame
pygame.init()
pygame.font.init()

# 游戏窗口设置
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("文字修仙游戏")

# 颜色定义
BACKGROUND = (10, 10, 10)
TEXT_COLOR = (220, 220, 220)
HIGHLIGHT = (255, 215, 0)
PROGRESS_BG = (40, 32, 56)
PROGRESS_FG = (86, 207, 225)
BUTTON_BG = (70, 50, 90)
BUTTON_HOVER = (100, 70, 120)
ENCOUNTER_BG = (30, 20, 40)

# 字体
title_font = pygame.font.SysFont('simhei', 48)
font_large = pygame.font.SysFont('simhei', 32)
font_medium = pygame.font.SysFont('simhei', 24)
font_small = pygame.font.SysFont('simhei', 18)

# 修仙境界体系
cultivation_levels = [
    {"name": "凡人", "exp_required": 0, "color": (180, 180, 180)},
    {"name": "炼气期", "exp_required": 100, "color": (100, 200, 100)},
    {"name": "筑基期", "exp_required": 500, "color": (100, 150, 255)},
    {"name": "金丹期", "exp_required": 2000, "color": (255, 200, 100)},
    {"name": "元婴期", "exp_required": 10000, "color": (255, 100, 200)},
    {"name": "化神期", "exp_required": 50000, "color": (200, 100, 255)},
    {"name": "返虚期", "exp_required": 100000, "color": (220, 150, 205)},
    {"name": "大乘期", "exp_required": 300000, "color": (255, 215, 0)},
    {"name": "渡劫期", "exp_required": 1000000, "color": (255, 69, 0)},
    {"name": "真仙", "exp_required": 10000000, "color": (255, 255, 255)}
]


# 玩家类
class Player:
    def __init__(self):
        self.name = "修真者"
        self.level = 0
        self.exp = 0
        self.start_time = pygame.time.get_ticks()  # 记录游戏开始时间
        self.game_year = 149  # 初始仙历年份
        self.events = []
        self.encounter_active = False
        self.current_encounter = None
        self.last_year = self.game_year
        self.cultivating = True  # 挂机状态，默认开启

    def add_exp(self, amount):
        self.exp += amount
        # 检查升级
        while self.level < len(cultivation_levels) - 1 and self.exp >= cultivation_levels[self.level + 1][
            "exp_required"]:
            self.level += 1
            self.add_event(f"恭喜！突破到{cultivation_levels[self.level]['name']}！")

    def update(self):
        # 更新游戏年份
        elapsed_seconds = (pygame.time.get_ticks() - self.start_time) // 1000  # 获取已过去的秒数
        elapsed_minutes = elapsed_seconds // 60  # 转换为分钟数
        # 每过一分钟增加一年
        self.game_year = 149 + elapsed_minutes
        # 检查年份是否变化，触发奇遇
        if self.game_year != self.last_year:
            self.trigger_encounter()
            self.last_year = self.game_year
        # 挂机升级!!!
        if self.cultivating:
            exp_gain = random.randint(1, 2**self.level) # 每秒获得的修为
            self.add_exp(exp_gain)
        # 随机事件
        if random.random() < 0.001:
            event_type = random.choice(["顿悟", "灵气充沛", "心魔干扰", "悟道"])
            if event_type == "顿悟":
                bonus = random.randint(100, 1000) * (self.level + 1)
                self.add_exp(bonus)
                self.add_event(f"灵光一闪，顿悟获得{bonus:.0f}经验")
            elif event_type == "灵气充沛":
                bonus = random.randint(10, 1000) * (self.level + 1)
                self.add_exp(bonus)
                self.add_event(f"周围灵气充沛，额外获得{bonus:.0f}经验")
            elif event_type == "心魔干扰":
                loss = random.randint(1, 5) ** (self.level + 1)
                self.exp = max(0, self.exp - loss)
                self.add_event(f"心魔干扰，损失{loss:.0f}经验")
            elif event_type == "悟道":
                bonus = random.randint(100, 10000) * (self.level + 1)
                self.add_exp(bonus)
                self.add_event(f"感悟天道，心境圆满，越发契合大道，获得{bonus:.0f}经验")

    def add_event(self, event):
        self.events.insert(0, event)
        if len(self.events) > 10:
            self.events.pop()

    def trigger_encounter(self):
        """触发一个随机奇遇"""
        encounters = [
            {"name": "神秘洞府", "description": "在深山中发现一处神秘洞府，里面似乎藏有宝物", "actions": [
                {"text": "谨慎探索", "effect": lambda: self.add_exp(random.randint(500, 2000))},
                {"text": "大胆进入",
                 "effect": lambda: (self.add_exp(random.randint(2000, 5000)*self.level), self.add_event("获得上古法宝！"))},
                {"text": "绕道而行", "effect": lambda: self.add_event("避开了可能的危险")}
            ]},
            {"name": "受伤的灵兽", "description": "发现一只受伤的稀有灵兽，它正痛苦地蜷缩在草丛中", "actions": [
                {"text": "救治灵兽", "effect": lambda: (self.add_exp(1000*self.level), self.add_event("灵兽康复后成为你的伙伴"))},
                {"text": "捕捉灵兽", "effect": lambda: (self.add_exp(500*self.level), self.add_event("捕获成功，但受了一点轻伤"))},
                {"text": "置之不理", "effect": lambda: self.add_event("继续前行")}
            ]},
            {"name": "上古遗迹", "description": "偶然发现一处上古遗迹，石壁上刻有神秘的符文", "actions": [
                {"text": "参悟符文", "effect": lambda: (self.add_exp(3000*self.level), self.add_event("领悟到一门神通！"))},
                {"text": "拓印符文", "effect": lambda: (self.add_exp(1000*self.level), self.add_event("拓印符文以备后续研究"))},
                {"text": "破坏符文",
                 "effect": lambda: (self.add_event("符文被破坏，什么也没得到"), self.add_event("你感到一阵心悸"))}
            ]},
            {"name": "神秘商人", "description": "遇到一个神秘商人，他出售各种奇珍异宝", "actions": [
                {"text": "购买灵药", "effect": lambda: (self.add_exp(1500*self.level), self.add_event("服用灵药修为大增"))},
                {"text": "交换法宝", "effect": lambda: self.add_event("用灵石换得一件法宝")},
                {"text": "无视商人", "effect": lambda: self.add_event("错过了交易机会")}
            ]},
            {"name": "灵气泉眼", "description": "发现一处灵气充沛的泉眼，周围生长着珍稀灵草", "actions": [
                {"text": "采集灵草", "effect": lambda: (self.add_exp(1000*self.level), self.add_event("采集到珍稀灵草"))},
                {"text": "泉边修炼", "effect": lambda: (self.add_exp(3000*self.level), self.add_event("在灵气泉边修炼事半功倍"))},
                {"text": "破坏泉眼", "effect": lambda: (self.add_event("泉眼被破坏，灵气消散"), self.add_exp(-500))}
            ]},
            {"name": "仙缘道侣", "description": "偶遇一位与你仙缘相合的道侣，她似乎对你有意", "actions": [
                {"text": "结为道侣", "effect": lambda: (self.add_exp(5000*self.level), self.add_event("与道侣双修，修为大增"))},
                {"text": "婉言谢绝", "effect": lambda: self.add_event("你选择独自修行")},
                {"text": "切磋论道", "effect": lambda: (self.add_exp(2000*self.level), self.add_event("论道切磋，互有收获"))}
            ]},
            {"name": "天材地宝", "description": "发现一株即将成熟的天地灵物，周围有妖兽守护", "actions": [
                {"text": "强行夺取", "effect": lambda: (self.add_exp(2000*self.level), self.add_event("击败妖兽夺得灵物"))},
                {"text": "等待成熟", "effect": lambda: (self.add_exp(4000*self.level), self.add_event("耐心等待后安全获得灵物"))},
                {"text": "放弃离开", "effect": lambda: self.add_event("不想冒险，悄然离去")}
            ]},
            {"name": "路遇妖魔", "description": "发现远处的城镇中存在不少妖魔，你会", "actions": [
                {"text": "替天行道",
                 "effect": lambda: (self.add_exp(4000 * self.level), self.add_event("击杀妖魔，战斗经验上涨"))},
                {"text": "暗中观察",
                 "effect": lambda: (self.add_exp(100 * self.level), self.add_event("妖魔作乱，生灵涂炭"))},
                {"text": "放弃离开", "effect": lambda: self.add_event("不愿冒险，悄然离去")}
            ]},
            {"name": "合欢魔女", "description": "偶遇合欢宗魔女，她妄图与你双修", "actions": [
                {"text": "阴阳交汇",
                 "effect": lambda: (self.add_exp(-200 * self.level), self.add_event("与魔女双修，修为少量下降"))},
                {"text": "采阴补阳",
                 "effect": lambda: (self.add_exp(-400 * self.level), self.add_event("你的技巧过于低端，反被魔女采阳补阴，修为下降"))},
                {"text": "迅速离开", "effect": lambda: self.add_event("实在危险，迅速离去")}
            ]},
            {"name": "天劫降世", "description": "你的天资引动了上天雷劫，做好准备吧！", "actions": [
                {"text": "挑衅雷劫",
                 "effect": lambda: (self.add_exp(-10000 * self.level), self.add_event("你引起天道震怒，修为大跌"))},
                {"text": "硬抗雷劫",
                 "effect": lambda: (self.add_exp(1000 * self.level), self.add_event("你以肉身硬抗雷劫，淬炼肉体，修为大增"))},
                {"text": "安然渡劫", "effect": lambda: self.add_event("你拿出法宝，有惊无险地度过雷劫")}
            ]}
        ]
        self.current_encounter = random.choice(encounters)
        self.encounter_active = True
        self.add_event(f"触发奇遇: {self.current_encounter['name']}")

    def to_dict(self):
        """将玩家数据转换为字典"""
        return {
            'name': self.name,
            'level': self.level,
            'exp': self.exp,
            'game_year': self.game_year,
            'events': self.events,
            'cultivating': self.cultivating,
            'start_time': pygame.time.get_ticks() - (self.game_year - 149) * 60 * 1000  # 计算新的开始时间
        }

    @classmethod
    def from_dict(cls, data):
        """从字典创建玩家实例"""
        player = cls()
        player.name = data['name']
        player.level = data['level']
        player.exp = data['exp']
        player.game_year = data['game_year']
        player.events = data['events']
        player.cultivating = data['cultivating']
        player.start_time = data['start_time']
        return player


# 存档管理
def save_game(player):
    """保存游戏"""
    save_data = player.to_dict()
    try:
        with open('修仙游戏存档.json', 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False, indent=4)
        print("游戏已成功保存到'修仙游戏存档.json'")
    except Exception as e:
        print(f"保存游戏失败: {e}")


def load_game():
    """加载游戏"""
    try:
        with open('修仙游戏存档.json', 'r', encoding='utf-8') as f:
            save_data = json.load(f)
        return Player.from_dict(save_data)
    except FileNotFoundError:
        print("未找到存档文件，开始新游戏")
        return Player()
    except Exception as e:
        print(f"加载存档失败: {e}")
        return Player()


# 创建主菜单按钮
def create_menu_buttons():
    """创建主菜单按钮"""
    new_game_button = Button(WIDTH // 2 - 100, HEIGHT // 2 - 30, 200, 50, "新游戏", lambda: Player())
    load_game_button = Button(WIDTH // 2 - 100, HEIGHT // 2 + 50, 200, 50, "继续游戏", load_game)
    return new_game_button, load_game_button


# 按钮类
class Button:
    def __init__(self, x, y, width, height, text, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.hovered = False

    def draw(self, surface):
        color = BUTTON_HOVER if self.hovered else BUTTON_BG
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        pygame.draw.rect(surface, (120, 100, 140), self.rect, 2, border_radius=8)
        text_surf = font_medium.render(self.text, True, TEXT_COLOR)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def draw_encounter(self, surface):
        color = (100, 80, 120) if self.hovered else (80, 60, 100)
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        pygame.draw.rect(surface, (140, 120, 160), self.rect, 2, border_radius=8)
        text_surf = font_medium.render(self.text, True, TEXT_COLOR)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def check_hover(self, pos):
        self.hovered = self.rect.collidepoint(pos)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.hovered and self.action:
                return self.action()
        return None


# 主动修炼获得经验
def manual_cultivate():
    exp_gain = (player.level + 1) * random.randint(1, 10000)
    player.add_exp(exp_gain)
    player.add_event(f"主动修炼获得{exp_gain:.0f}经验")


# 切换挂机状态
def toggle_cultivation():
    player.cultivating = not player.cultivating
    player.add_event("开始挂机修炼" if player.cultivating else "停止挂机修炼")


# 创建主界面按钮
cultivate_button = Button(WIDTH - 180, HEIGHT - 100, 160, 50, "开始/停止挂机", toggle_cultivation)
manual_button = Button(WIDTH - 180, HEIGHT - 180, 160, 50, "主动修炼", manual_cultivate)
save_button = Button(WIDTH - 180, HEIGHT - 40, 160, 40, "保存游戏", lambda: save_game(player))


# 游戏主循环
def main():
    global player

    # 显示主菜单
    in_menu = True
    new_game_button, load_game_button = create_menu_buttons()

    clock = pygame.time.Clock()

    while True:
        # 事件处理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            mouse_pos = pygame.mouse.get_pos()

            if in_menu:
                # 主菜单事件处理
                new_game_button.check_hover(mouse_pos)
                load_game_button.check_hover(mouse_pos)

                if new_game_button.handle_event(event):
                    player = Player()
                    in_menu = False
                elif load_game_button.handle_event(event):
                    player = load_game()
                    in_menu = False
            else:
                # 游戏主界面事件处理
                if player.encounter_active:
                    # 奇遇界面的事件处理
                    for btn in encounter_buttons:
                        btn.check_hover(mouse_pos)
                        if btn.handle_event(event):
                            player.encounter_active = False
                            encounter_buttons.clear()
                else:
                    # 主界面的事件处理
                    cultivate_button.check_hover(mouse_pos)
                    manual_button.check_hover(mouse_pos)
                    save_button.check_hover(mouse_pos)

                    cultivate_button.handle_event(event)
                    manual_button.handle_event(event)
                    save_button.handle_event(event)

        # 更新玩家状态
        if not in_menu:
            player.update()

        # 绘制界面
        screen.fill(BACKGROUND)

        if in_menu:
            # 绘制主菜单
            title = title_font.render("仙尊养成器", True, HIGHLIGHT)
            screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 150))

            new_game_button.draw(screen)
            load_game_button.draw(screen)

            # 检查存档是否存在
            if not os.path.exists('修仙游戏存档.json'):
                load_game_button.text = "无存档"
                load_game_button.action = None
        else:
            # 绘制左上角时间信息
            time_text = font_medium.render(f"仙历: {player.game_year}纪", True, (150, 220, 255))
            screen.blit(time_text, (50, 50))

            # 绘制标题
            title = title_font.render("仙尊养成器", True, HIGHLIGHT)
            screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 20))

            # 绘制玩家信息
            level_info = cultivation_levels[player.level]
            level_text = font_large.render(f"境界: {level_info['name']}", True, level_info["color"])
            screen.blit(level_text, (50, 100))

            # 绘制经验进度条
            pygame.draw.rect(screen, PROGRESS_BG, (50, 150, 400, 25), border_radius=12)
            current_exp = player.exp
            next_level_exp = cultivation_levels[player.level + 1]["exp_required"] if player.level < len(
                cultivation_levels) - 1 else current_exp
            prev_level_exp = cultivation_levels[player.level]["exp_required"]
            progress_width = 0
            if next_level_exp > prev_level_exp:
                progress = (current_exp - prev_level_exp) / (next_level_exp - prev_level_exp)
                progress_width = int(400 * progress)
            pygame.draw.rect(screen, PROGRESS_FG, (50, 150, progress_width, 25), border_radius=12)
            exp_text = font_small.render(f"修为: {current_exp:.0f}/{next_level_exp:.0f}", True, TEXT_COLOR)
            screen.blit(exp_text, (460, 150))

            # 绘制事件日志
            pygame.draw.rect(screen, (60, 52, 86), (50, 250, 500, 250), 2, border_radius=10)
            event_title = font_medium.render("修真记事", True, HIGHLIGHT)
            screen.blit(event_title, (50, 240 - event_title.get_height()))
            for i, event in enumerate(player.events[:10]):
                event_surf = font_small.render(event, True, TEXT_COLOR)
                screen.blit(event_surf, (70, 270 + i * 22))

            # 绘制境界图谱
            pygame.draw.rect(screen, (60, 52, 86), (WIDTH - 125, 50, 125, 350), 2, border_radius=10)
            realm_title = font_medium.render("境界图谱", True, HIGHLIGHT)
            screen.blit(realm_title, (WIDTH - 180 + 115 - realm_title.get_width() // 2, 40 - realm_title.get_height()))
            for i, level in enumerate(cultivation_levels[:10]):
                y_pos = 60 + i * 35
                color = level["color"] if player.level >= i else (80, 80, 80)
                level_text = font_small.render(level["name"], True, color)
                screen.blit(level_text, (WIDTH - 85, y_pos))
                if player.level == i:
                    pygame.draw.circle(screen, color, (WIDTH - 100, y_pos + 10), 5)

            # 绘制按钮
            cultivate_button.draw(screen)
            manual_button.draw(screen)
            save_button.draw(screen)

            # 绘制奇遇界面
            encounter_buttons = []
            if player.encounter_active and player.current_encounter:
                # 绘制半透明背景
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 180))
                screen.blit(overlay, (0, 0))

                # 绘制奇遇窗口
                encounter_rect = pygame.Rect(WIDTH // 2 - 250, HEIGHT // 2 - 150, 500, 300)
                pygame.draw.rect(screen, ENCOUNTER_BG, encounter_rect, border_radius=15)
                pygame.draw.rect(screen, (140, 100, 180), encounter_rect, 3, border_radius=15)

                # 奇遇标题
                title = font_large.render(player.current_encounter["name"], True, HIGHLIGHT)
                screen.blit(title, (encounter_rect.centerx - title.get_width() // 2, encounter_rect.y + 20))

                # 奇遇描述
                desc_lines = []
                current_line = ""
                for word in player.current_encounter["description"]:
                    test_line = current_line + word
                    if font_medium.size(test_line)[0] < 450:
                        current_line = test_line
                    else:
                        desc_lines.append(current_line)
                        current_line = word
                desc_lines.append(current_line)

                for i, line in enumerate(desc_lines):
                    desc_surf = font_medium.render(line, True, (220, 200, 255))
                    screen.blit(desc_surf,
                                (encounter_rect.centerx - desc_surf.get_width() // 2, encounter_rect.y + 70 + i * 30))

                # 创建奇遇按钮
                for i, action in enumerate(player.current_encounter["actions"]):
                    btn = Button(encounter_rect.x + 50 + i * 150, encounter_rect.y + 200, 140, 40, action["text"],
                                 action["effect"])
                    encounter_buttons.append(btn)

                # 绘制奇遇按钮
                mouse_pos = pygame.mouse.get_pos()
                for btn in encounter_buttons:
                    btn.check_hover(mouse_pos)
                    btn.draw_encounter(screen)

            # 绘制底部装饰
            footer = font_small.render("修仙之路漫漫，唯有坚持方能证道长生", True, (0, 250, 0))
            screen.blit(footer, (WIDTH // 5 - footer.get_width() // 2, HEIGHT - 30))

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()