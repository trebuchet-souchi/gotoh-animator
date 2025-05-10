# gotoh.py
"""Goat generation logic for use in the Streamlit app. This module does not depend on tkinter."""

import random
import hashlib
from PIL import Image, ImageDraw, ImageColor

# 背景色オプション
BG_OPTIONS = {
    'Purple':      '#ff00b3',  # 紫
    'Sky':         '#20F6FF',  # 空
    'Green':       '#71E500',  # 緑
    'Deep Purple': '#4A215E',  # 深紫
    'Gray':        '#696969',  # 灰
}

# 描画パレット（bgは後でapp.pyから書き換える）
PALETTE = {
    'bg':        BG_OPTIONS['Purple'],
    'body':      '#ffffff',
    'eye':       '#000000',
    'horn':      '#ffb300',
    'horn_alt':  '#ff3300',
    'horn_blue': '#0080ff',
}

FRAME_SIZE     = (16, 16)
FRAME_DELAY_MS = 150


def get_line_points(x0, y0, x1, y1):
    """Bresenham のアルゴリズムで線上のピクセルを返す"""
    points = []
    dx = abs(x1 - x0); dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1; sy = 1 if y0 < y1 else -1
    err = dx + dy
    while True:
        points.append((x0, y0))
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy; x0 += sx
        if e2 <= dx:
            err += dx; y0 += sy
    return points


class GoatGenerator:
    """山羊ピクセルアニメーションを生成するクラス"""

    def __init__(self, seed: str):
        self.seed_str = seed
        # シード文字列からランダムオブジェクトを作成
        h = hashlib.sha256(seed.encode('utf-8')).digest()
        self.rand = random.Random(int.from_bytes(h[:8], 'big'))
        # 各パーツ生成の重み
        self.eye_weights = [1, 2, 3]
        self.leg_weights = [2, 3, 4]
        self.horn_weights = [1, 2]

    def weighted_choice(self, options):
        """重み付き選択（均等確率）"""
        return self.rand.choice(options)

    def generate_frame(self, body_shape, eye_positions, leg_shapes, horn_shapes,
                       small_shape, small_eyes, small_horns,
                       small_flag, dy, outline: bool, transparent: bool):
        mode = 'RGBA' if transparent else 'RGB'
        bg_color = ImageColor.getcolor(PALETTE['bg'], 'RGB')
        im = Image.new(mode, FRAME_SIZE, bg_color)
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
                    draw.point((px-1, py+dy), fill=PALETTE['eye'])
                    draw.point((px+1, py+dy), fill=PALETTE['eye'])

        # 角
        for x0, y0, x1, y1, col in horn_shapes:
            draw.line((x0, y0 + dy, x1, y1 + dy), fill=col)

        # ミニ山羊パーツ
        if small_flag:
            draw.ellipse(small_shape, fill=PALETTE['body'])
            for ex, ey in small_eyes:
                draw.point((ex, ey + dy), fill=PALETTE['eye'])
            for x0, y0, x1, y1, col in small_horns:
                draw.line((x0, y0 + dy, x1, y1 + dy), fill=col)

        return im

    def generate_animation(self, outline: bool, transparent: bool):
        """全フレームを生成して返す"""
        base = (3, 5, 13, 11)
        bw, bh = base[2]-base[0], base[3]-base[1]

        # 目・脚・角の数を決定
        eye_n = self.weighted_choice(self.eye_weights)
        leg_n = self.weighted_choice(self.leg_weights)
        horn_n = self.weighted_choice(self.horn_weights)

        # 目配置
        eyes = []
        attempts = 0
        while len(eyes) < eye_n and attempts < 50:
            ex, ey = self.rand.randint(8, 12), self.rand.randint(6, 9)
            if all(abs(ex-ox)>1 or abs(ey-oy)>1 for ox,oy in eyes):
                eyes.append((ex, ey))
            attempts += 1

        # 脚配置
        legs = []
        for _ in range(leg_n):
            x0, y0 = self.rand.randint(5, 10), 11
            ln = self.rand.randint(1, 3)
            angle = self.rand.choice([-1, 1])
            x1, y1 = x0 + angle*ln, y0 - self.rand.randint(0, 1)
            legs.append((x0, y0, x1, y1))

        # 角配置
        horns = []
        for _ in range(horn_n):
            x = self.rand.randint(6, 9)
            y = 5
            ln = self.rand.randint(2, 3)
            col_r = self.rand.random()
            if col_r < 0.10:
                col = PALETTE['horn_blue']
            elif col_r < 0.25:
                col = PALETTE['horn_alt']
            else:
                col = PALETTE['horn']
            # 2本枝分かれする場合も
            if self.rand.random() < 0.4:
                off = self.rand.choice([-1,1])
                bx, by = x+off, y - ln//2
                horns.append((x, y, bx, by, col))
                horns.append((bx, by, x, y-ln, col))
            else:
                horns.append((x, y, x, y-ln, col))

        # ミニ山羊生成フラグ
        small_flag = self.rand.random() < 0.05
        small_horns = []
        small_eyes = []
        small_shape = (0,0,0,0)
        if small_flag:
            w = max(2, int(bw*0.3))
            h = max(3, int(bh*0.3))
            off = self.rand.randint(2,3)
            sx = max(0, base[0] - off)
            sy = base[1] if self.rand.choice([True,False]) else base[3] - h
            small_shape = (sx, sy, sx+w, sy+h)
            # 小ゴートの目
            cnt_eyes = self.rand.randint(1,3)
            b=0
            while len(small_eyes)<cnt_eyes and b<20:
                ex = self.rand.randint(sx+1, sx+w-1)
                ey = self.rand.randint(sy+1, sy+h-1)
                if all(abs(ex-ox)>1 or abs(ey-oy)>1 for ox,oy in small_eyes):
                    small_eyes.append((ex, ey))
                b+=1
            # 小ゴートの角
            cnt_horns = self.rand.randint(0,3)
            min_eye_y = min(ey for _,ey in small_eyes)
            max_horn_y = min_eye_y - 2
            for _ in range(cnt_horns):
                xh = self.rand.randint(sx+1, sx+w-1)
                yh = self.rand.randint(sy, max_horn_y if max_horn_y>=sy else sy)
                ln2 = self.rand.randint(1,2)
                cr = self.rand.random()
                if cr<0.10:
                    ch = PALETTE['horn_blue']
                elif cr<0.25:
                    ch = PALETTE['horn_alt']
                else:
                    ch = PALETTE['horn']
                if self.rand.random()<0.4:
                    off2 = self.rand.choice([-1,1])
                    bx2,by2 = xh+off2, yh - ln2//2
                    small_horns.append((xh, yh, bx2, by2, ch))
                    small_horns.append((bx2, by2, xh, yh-ln2, ch))
                else:
                    small_horns.append((xh, yh, xh, yh-ln2, ch))

        # フレーム生成
        frames = []
        for dy in [-1, 0, 1]:
            dx0, dy0 = self.rand.randint(-1,1), self.rand.randint(-1,1)
            dx1, dy1 = self.rand.randint(-1,1), self.rand.randint(-1,1)
            body_shape = (
                base[0]+dx0, base[1]+dy0, base[2]+dx1, base[3]+dy1
            )
            leg_shapes = [(
                x0 + self.rand.choice([-1,0,1]), y0, x1 + self.rand.choice([-1,0,1]), y1
            ) for (x0,y0,x1,y1) in legs]
            frame = self.generate_frame(
                body_shape, eyes, leg_shapes, horns,
                small_shape, small_eyes, small_horns,
                small_flag, dy, outline, transparent
            )
            frames.append(frame)
        return frames
