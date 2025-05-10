import random
import hashlib
from PIL import Image, ImageDraw, ImageColor

# 背景色オプション

BG\_OPTIONS = {
'Purple':     '#ff00b3',  # 紫
'Sky':        '#20F6FF',  # 空
'Green':      '#71E500',  # 緑
'Deep Purple':'#4A215E',  # 深紫
'Gray':       '#696969',  # 灰
}

# 描画パレット（bgは後でapp.pyから書き換える）

PALETTE = {
'bg':       BG\_OPTIONS\['Purple'],
'body':     '#ffffff',
'eye':      '#000000',
'horn':     '#ffb300',
'horn\_alt': '#ff3300',
'horn\_blue':'#0080ff',
}

FRAME\_SIZE     = (16, 16)
FRAME\_DELAY\_MS = 150

def get\_line\_points(x0, y0, x1, y1):
"""Bresenham のアルゴリズムで線上のピクセルを返す"""
points = \[]
dx = abs(x1 - x0); dy = -abs(y1 - y0)
sx = 1 if x0 < x1 else -1; sy = 1 if y0 < y1 else -1
err = dx + dy
while True:
points.append((x0, y0))
if x0 == x1 and y0 == y1:
break
e2 = 2 \* err
if e2 >= dy:
err += dy; x0 += sx
if e2 <= dx:
err += dx; y0 += sy
return points

class GoatGenerator:
"""山羊ピクセルアニメーションを生成するクラス"""

```
def __init__(self, seed: str):
    self.seed_str = seed
    h = hashlib.sha256(seed.encode('utf-8')).digest()
    self.rand = random.Random(int.from_bytes(h[:8], 'big'))

def generate_frame(self, body_shape, eye_positions, leg_shapes, horns,
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

def generate_animation(self, outline: bool, transparent: bool):
    base = (3,5,13,11)
    bw, bh = base[2]-base[0], base[3]-base[1]
    eye_n = self.weighted_choice(self.eye_weights)
    leg_n = self.weighted_choice(self.leg_weights)
    horn_n = self.weighted_choice(self.horn_weights)
    # 目配置
    eyes = []
    a = 0
    while len(eyes) < eye_n and a < 50:
        ex, ey = self.rand.randint(8,12), self.rand.randint(6,9)
        if all(abs(ex-ox)>1 or abs(ey-oy)>1 for ox,oy in eyes):
            eyes.append((ex,ey))
        a += 1
    # 脚配置
    legs = []
    for _ in range(leg_n):
        x0, y0 = self.rand.randint(5,10), 11
        dy_leg = self.rand.randint(1,2)
        xm, ym = x0 + self.rand.choice([-1,0,1]), y0 + dy_leg
        legs.append((x0, y0, xm, ym))
    # 角配置
    horns = []
    for _ in range(horn_n):
        r = self.rand.random()
        if r < 0.10: col = PALETTE['horn_blue']
        elif r < 0.25: col = PALETTE['horn_alt']
        else: col = PALETTE['horn']
        x, y = self.rand.randint(6,9), 5
        ln = self.rand.randint(2,3)
        if self.rand.random() < 0.4:
            d = self.rand.choice([-1,1])
            by = y - (ln//2)
            bx = x + d
            horns.extend([(x,y,bx,by,col), (bx,by,x,y-ln,col)])
        else:
            horns.append((x,y,x,y-ln,col))
    # 小ゴート生成
    small_flag = self.rand.random() < 0.05
    small_shape = (0,0,0,0)
    small_eyes = []
    small_horns = []
    if small_flag:
        w = max(2, int(bw*0.3))
        h = max(3, int(bh*0.3))
        off = self.rand.randint(2,3)
        sx0 = max(0, base[0] - off)
        sy0 = base[1] if self.rand.choice([True,False]) else base[3] - h
        small_shape = (sx0, sy0, sx0+w, sy0+h)
        cnt_eyes = self.rand.randint(1,3)
        b = 0
        while len(small_eyes) < cnt_eyes and b < 20:
            ex, ey = self.rand.randint(sx0+1, sx0+w-1), self.rand.randint(sy0+1, sy0+h-1)
            if all(abs(ex-ox)>1 or abs(ey-oy)>1 for ox,oy in small_eyes): small_eyes.append((ex,ey))
            b += 1
        cnt_horns = self.rand.randint(0,3)
        min_eye_y = min(ey for _,ey in small_eyes)
        max_horn_y = min_eye_y - 2
        for _ in range(cnt_horns):
            r = self.rand.random()
            if r < 0.10: col = PALETTE['horn_blue']
            elif r < 0.25: col = PALETTE['horn_alt']
            else: col = PALETTE['horn']
            hx = self.rand.randint(sx0+1, sx0+w-1)
            hy = self.rand.randint(sy0, max_horn_y if max_horn_y >= sy0 else sy0)
            ln = self.rand.randint(1,2)
            if self.rand.random() < 0.4:
                d = self.rand.choice([-1,1])
                by = hy - (ln//2)
                bx = hx + d
                small_horns.extend([(hx,hy,bx,by,col), (bx,by,hx,hy-ln,col)])
            else:
                small_horns.append((hx,hy,hx,hy-ln,col))
    # フレーム生成
    frames = []
    for dy in [-1,0,1]:
        dx0, dy0 = self.rand.randint(-1,1), self.rand.randint(-1,1)
        dx1, dy1 = self.rand.randint(-1,1), self.rand.randint(-1,1)
        body_shape = (base[0]+dx0, base[1]+dy0, base[2]+dx1, base[3]+dy1)
        legs_f = [(x0 + self.rand.choice([-1,0,1]), y0, x1 + self.rand.choice([-1,0,1]), y1)
                  for x0,y0,x1,y1 in legs]
        # outlineとtransparentを引数から渡すように修正
        frames.append(self.generate_frame(
            body_shape, eyes, legs_f, horns,
            small_shape, small_eyes, small_horns,
            small_flag, dy, outline, transparent
        ))
    return frames
