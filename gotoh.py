# gotoh.py
"""Goat generation logic for use in the Streamlit app. This module does not depend on tkinter."""

import random
import hashlib
from PIL import Image, ImageDraw, ImageColor

# 背景色オプション
BG_OPTIONS = {
    'Purple': '#ff00b3',       # 紫
    'Sky':    '#20F6FF',       # 空
    'Green':  '#71E500',       # 緑
    'Deep Purple': '#4A215E',  # 深紫
    'Gray':   '#696969',       # 灰
}

# パレット定義
PALETTE = {
    'bg':       BG_OPTIONS['Purple'],  # デフォルト: 紫
    'body':     '#ffffff',
    'eye':      '#000000',
    'horn':     '#ffb300',
    'horn_alt': '#ff3300',
    'horn_blue':'#0080ff',
}

# フレームサイズと遅延
FRAME_SIZE     = (16, 16)
FRAME_DELAY_MS = 150


def get_line_points(x0, y0, x1, y1):
    """
    Bresenham のアルゴリズムで直線上の座標を列挙
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


class GoatGenerator:
    """
    山羊ピクセルアニメーションを生成するジェネレータ
    """
    def __init__(self, seed: str):
        self.seed_str = seed
        h = hashlib.sha256(seed.encode('utf-8')).digest()
        # random.Random に渡すため、整数値に変換
        self.rand = random.Random(int.from_bytes(h[:8], 'big'))

    def generate_frame(self, body_shape, eye_positions, leg_shapes, horns,
                       small_shape, small_eyes, small_horns,
                       small_flag, dy, outline: bool, transparent: bool):
        """
        単一フレームを描く。座標とパラメータに基づいて PIL.Image を返す
        """
        im = Image.new('RGBA' if transparent else 'RGB', FRAME_SIZE,
                       ImageColor.getcolor(PALETTE['bg'], 'RGB'))
        draw = ImageDraw.Draw(im)

        # 身体
        draw.ellipse(body_shape, fill=PALETTE['body'])
        if outline:
            for px, py in get_line_points(*body_shape[:2], *body_shape[2:]):
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

        # 小さい山羊パーツ（ミニチュア）
        if small_flag:
            draw.ellipse(small_shape, fill=PALETTE['body'])
            for ex, ey in small_eyes:
                draw.point((ex, ey + dy), fill=PALETTE['eye'])
            for hx, hy in small_horns:
                draw.point((hx, hy + dy), fill=PALETTE['horn_blue'])

        return im

    def generate_animation(self, outline: bool, transparent: bool):
        """
        全フレームを生成して PIL.Image のリストを返す
        """
        frames = []
        # フレームの基本パラメータを決定
        # body_shape, eye_positions, leg_shapes, horns など...
        # ここに生成ロジックを記述
        # 省略可
        # 最終的に frames.append(self.generate_frame(...)) が呼ばれる
        return frames
