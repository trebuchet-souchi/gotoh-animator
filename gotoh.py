import tkinter as tk
from tkinter import ttk, filedialog
from tkinter.scrolledtext import ScrolledText
from tkinter import messagebox
import random
import hashlib
from PIL import Image, ImageDraw, ImageColor
import os
import platform

def get_line_points(x0, y0, x1, y1):
    """
    Bresenham のアルゴリズムで直線上の座標をリストで返す
    """
    points = []
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    while True:
        points.append((x0, y0))
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy
    return points

# 背景色オプション
BG_OPTIONS = {
    'Purple':       '#ff00b3',  # 紫
    'Sky':          '#20F6FF',  # 空
    'Green':        '#71E500',  # 緑
    'Deep Purple':  '#4A215E',  # 深紫
    'Gray':         '#696969',  # 灰
}

# 描画パレット
PALETTE = {
    'bg':        BG_OPTIONS['Purple'],
    'body':      '#ffffff',
    'eye':       '#000000',
    'horn':      '#ffb300',
    'horn_alt':  '#ff3300',
    'horn_blue': '#0080ff',
}

# フレームサイズとフレーム遅延
FRAME_SIZE     = (16, 16)
FRAME_DELAY_MS = 150

class GoatGenerator:
    """山羊ピクセルアニメーションを生成するクラス"""

    def __init__(self, seed: str, outline: bool = False, transparent: bool = False):
        self.seed_str = seed
        h = hashlib.sha256(seed.encode('utf-8')).digest()
        self.rand = random.Random(int.from_bytes(h[:8], 'big'))
        self.outline = outline
        self.transparent = transparent

        # 山羊構造の初期設定
        base = (3, 5, 13, 11)
        bw, bh = base[2] - base[0], base[3] - base[1]

        # 目の数、脚の数、角の数をランダムに決定
        self.eye_n = self.rand.randint(1, 3)
        self.leg_n = self.rand.randint(2, 4)
        self.horn_n = self.rand.randint(1, 2)

        # 目の位置を一意に決定
        self.eyes = []
        attempts = 0
        while len(self.eyes) < self.eye_n and attempts < 50:
            ex = self.rand.randint(base[0] + 2, base[2] - 2)
            ey = self.rand.randint(base[1] + 1, base[3] - 1)
            if all(abs(ex - ox) > 1 or abs(ey - oy) > 1 for ox, oy in self.eyes):
                self.eyes.append((ex, ey))
            attempts += 1

        # 脚の位置を決定
        self.legs = []
        for _ in range(self.leg_n):
            x0 = self.rand.randint(base[0] + 2, base[2] - 2)
            y0 = base[3]
            dy_leg = self.rand.randint(1, 2)
            xm = x0 + self.rand.choice([-1, 0, 1])
            ym = y0 + dy_leg
            self.legs.append((x0, y0, xm, ym))

        # 角の位置を決定
        self.horns = []
        for _ in range(self.horn_n):
            x = self.rand.randint(base[0] + 2, base[2] - 2)
            y = base[1]
            self.horns.append((x, y))

        # ミニ山羊パーツの有無
        self.small_flag = self.rand.random() < 0.05
        self.small_shape = (0, 0, 0, 0)
        self.small_eyes = []
        self.small_horns = []
        if self.small_flag:
            w = max(2, int(bw * 0.3))
            h = max(3, int(bh * 0.3))
            off = self.rand.randint(2, 3)
            sx0 = max(base[0], base[0] - off)
            sy0 = base[1] if self.rand.choice([True, False]) else base[3] - h
            self.small_shape = (sx0, sy0, sx0 + w, sy0 + h)
            # ミニ目
            cnt_eyes = self.rand.randint(1, 3)
            b = 0
            while len(self.small_eyes) < cnt_eyes and b < 20:
                ex = self.rand.randint(sx0 + 1, sx0 + w - 1)
                ey = self.rand.randint(sy0 + 1, sy0 + h - 1)
                if all(abs(ex - ox) > 1 or abs(ey - oy) > 1 for ox, oy in self.small_eyes):
                    self.small_eyes.append((ex, ey))
                b += 1
            # ミニ角
            cnt_horns = self.rand.randint(0, 3)
            min_eye_y = min(ey for _, ey in self.small_eyes)
            max_horn_y = min_eye_y - 2
            for _ in range(cnt_horns):
                hx = self.rand.randint(sx0 + 1, sx0 + w - 1)
                hy = self.rand.randint(sy0, max_horn_y if max_horn_y >= sy0 else sy0)
                self.small_horns.append((hx, hy))

    def generate_frame(self, body_shape, eye_positions, leg_shapes, horns,
                       small_shape, small_eyes, small_horns,
                       small_flag, dy, outline, transparent):
        mode = 'RGBA' if transparent else 'RGB'
        bg_color = ImageColor.getcolor(PALETTE['bg'], 'RGB')
        im = Image.new(mode, FRAME_SIZE, bg_color)
        draw = ImageDraw.Draw(im)
        # 身体
        draw.ellipse(body_shape, fill=PALETTE['body'])
        if outline:
            for px, py in get_line_points(
                    body_shape[0], body_shape[1],
                    body_shape[2], body_shape[3]):
                draw.point((px, py), fill=PALETTE['eye'])
        # 目
        for ex, ey in eye_positions:
            draw.point((ex, ey + dy), fill=PALETTE['eye'])
        # 脚
        for x0, y0, x1, y1 in leg_shapes:
            draw.line((x0, y0 + dy, x1, y1 + dy), fill=PALETTE['body'])
            if outline:
                for px, py in get_line_points(x0, y0, x1, y1):
                    draw.point((px - 1, py + dy), fill=PALETTE['eye'])
                    draw.point((px + 1, py + dy), fill=PALETTE['eye'])
        # 角
        for hx, hy in horns:
            draw.point((hx, hy + dy), fill=PALETTE['horn'])
        # ミニ山羊パーツ
        if small_flag:
            draw.ellipse(small_shape, fill=PALETTE['body'])
            for ex, ey in small_eyes:
                draw.point((ex, ey + dy), fill=PALETTE['eye'])
            for hx, hy in small_horns:
                draw.point((hx, hy + dy), fill=PALETTE['horn_blue'])
        return im

    def generate_animation(self, outline, transparent):
        frames = []
        for dy in [-1, 0, 1]:
            dx0 = self.rand.randint(-1, 1)
            dy0 = self.rand.randint(-1, 1)
            dx1 = self.rand.randint(-1, 1)
            dy1 = self.rand.randint(-1, 1)
            base = (3, 5, 13, 11)
            body_shape = (
                base[0] + dx0, base[1] + dy0,
                base[2] + dx1, base[3] + dy1
            )
            leg_shapes = []
            for x0, y0, xm, ym in self.legs:
                lx0 = x0 + self.rand.choice([-1, 0, 1])
                ly0 = y0
                lx1 = xm + self.rand.choice([-1, 0, 1])
                ly1 = ym
                leg_shapes.append((lx0, ly0, lx1, ly1))
            frames.append(self.generate_frame(
                body_shape, self.eyes,
                leg_shapes, self.horns,
                self.small_shape, self.small_eyes,
                self.small_horns, self.small_flag,
                dy, self.outline,
                self.transparent
            ))
        return frames
