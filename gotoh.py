import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageDraw, ImageTk, ImageColor
import random
import hashlib

# 背景色オプション
BG_OPTIONS = {
    'Purple': '#ff00b3',       # 紫
    'Sky': '#20F6FF',          # 空
    'Green': '#71E500',        # 緑
    'Deep Purple': '#4A215E',  # 深紫
    'Gray': '#696969',         # 灰
}

# パレット定義
PALETTE = {
    'bg': BG_OPTIONS['Purple'],  # デフォルト紫
    'body': '#ffffff',
    'eye': '#000000',
    'horn': '#ffb300',
    'horn_alt': '#ff3300',
    'horn_blue': '#0080ff',
}

FRAME_SIZE = (16, 16)
FRAME_DELAY_MS = 200  # 1フレームあたりの表示時間（ms）

# Bresenhamの線生成
def get_line_points(x0, y0, x1, y1):
    points = []
    dx, dy = abs(x1 - x0), abs(y1 - y0)
    x, y = x0, y0
    sx, sy = (1 if x1 > x0 else -1), (1 if y1 > y0 else -1)
    if dx > dy:
        err = dx // 2
        while x != x1:
            points.append((x, y)); err -= dy
            if err < 0: y += sy; err += dx
            x += sx
        points.append((x, y))
    else:
        err = dy // 2
        while y != y1:
            points.append((x, y)); err -= dx
            if err < 0: x += sx; err += dy
            y += sy
        points.append((x, y))
    return points

class GoatGenerator:
    def __init__(self, seed_str):
        # シードによる一貫乱数生成
        h = hashlib.sha256(seed_str.encode()).digest()
        self.rand = random.Random(int.from_bytes(h, 'big'))
        self.eye_weights = [(2, 50), (1, 20), (3, 15), (4, 10), (5, 5)]
        self.leg_weights = [(4, 40)] + [(i, 10) for i in range(1, 8) if i != 4]
        self.horn_weights = [(i, 1) for i in range(1, 6)]

    def weighted_choice(self, choices):
        total = sum(w for _, w in choices)
        r = self.rand.uniform(0, total)
        upto = 0
        for item, w in choices:
            if upto + w >= r:
                return item
            upto += w

    def generate_frame(self, body_shape, eye_positions, leg_shapes,
                       horns, small_shape, small_eyes, small_horns,
                       small_flag, dy, outline, transparent):
        # 背景生成
        if transparent:
            im = Image.new('RGBA', FRAME_SIZE, (0, 0, 0, 0))
        else:
            bg_rgb = ImageColor.getcolor(PALETTE['bg'], 'RGB')
            im = Image.new('RGBA', FRAME_SIZE, bg_rgb + (255,))
        draw = ImageDraw.Draw(im)

        bx0, by0, bx1, by1 = body_shape
        # 本体
        draw.ellipse((bx0, by0+dy, bx1, by1+dy), fill=PALETTE['body'])
        if outline:
            draw.ellipse((bx0, by0+dy, bx1, by1+dy), outline=PALETTE['eye'])
        # 目
        for ex, ey in eye_positions:
            draw.point((ex, ey+dy), fill=PALETTE['eye'])
        # 脚
        for x0, y0, x1, y1 in leg_shapes:
            draw.line((x0, y0+dy, x1, y1+dy), fill=PALETTE['body'])
            if outline:
                for px, py in get_line_points(x0, y0, x1, y1):
                    wx, wy = px-1, py
                    if 0 <= wx < 16 and 0 <= wy+dy < 16:
                        draw.point((wx, wy+dy), fill=PALETTE['eye'])
                    sx, sy = px, py+1
                    if 0 <= sx < 16 and 0 <= sy+dy < 16:
                        draw.point((sx, sy+dy), fill=PALETTE['eye'])
        # 角
        for x0, y0, x1, y1, col in horns:
            draw.line((x0, y0+dy, x1, y1+dy), fill=col)
        # 小ゴート
        if small_flag:
            sx0, sy0, sx1, sy1 = small_shape
            draw.ellipse((sx0, sy0+dy, sx1, sy1+dy), fill=PALETTE['body'])
            if outline:
                draw.ellipse((sx0, sy0+dy, sx1, sy1+dy), outline=PALETTE['eye'])
                ox0, ox1 = max(sx0, bx0), min(sx1, bx1)
                oy0, oy1 = max(sy0, by0), min(sy1, by1)
                for x in range(ox0, ox1):
                    for y in range(oy0+dy, oy1+dy):
                        if im.getpixel((x,y))[:3] == ImageColor.getcolor(PALETTE['eye'], 'RGB'):
                            im.putpixel((x,y), ImageColor.getcolor(PALETTE['body'], 'RGB') + (255,))
            for ex, ey in small_eyes:
                draw.point((ex, ey+dy), fill=PALETTE['eye'])
            for x0, y0, x1, y1, col in small_horns:
                draw.line((x0, y0+dy, x1, y1+dy), fill=col)
        # 隙間埋め
        if small_flag:
            gx0, gx1 = small_shape[2], body_shape[0]
            gy0, gy1 = max(small_shape[1], by0), min(small_shape[3], by1)
            for gx in range(gx0, gx1):
                for gy in range(gy0, gy1):
                    if im.getpixel((gx, gy+dy))[:3] == ImageColor.getcolor(PALETTE['bg'], 'RGB'):
                        im.putpixel((gx, gy+dy), ImageColor.getcolor(PALETTE['body'], 'RGB') + (255,))
        return im

    def generate_animation(self, outline, transparent):
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

class GoatApp:
    def __init__(self, root):
        self.root = root
        root.title("Goat Pixel Animator")
        self.canvas = tk.Canvas(root, width=FRAME_SIZE[0]*8, height=FRAME_SIZE[1]*8)
        self.canvas.grid(row=0, column=0, columnspan=9, pady=10)
        self.seed_var = tk.StringVar()
        self.rand_var = tk.BooleanVar(value=True)
        self.outline_var = tk.BooleanVar(value=False)
        self.transp_var = tk.BooleanVar(value=False)
        self.bg_var = tk.StringVar(value='Purple')
        self.scale_var = tk.IntVar(value=1)
        ttk.Checkbutton(root, text="Randomize Seed", variable=self.rand_var).grid(row=1, column=0)
        ttk.Checkbutton(root, text="Outline", variable=self.outline_var).grid(row=1, column=1)
        ttk.Checkbutton(root, text="Transparent BG", variable=self.transp_var).grid(row=1, column=2)
        tk.Label(root, text="Seed:").grid(row=1, column=3, sticky="e")
        ttk.Entry(root, textvariable=self.seed_var, width=16).grid(row=1, column=4)
        tk.Label(root, text="BG Color:").grid(row=1, column=5, sticky="e")
        ttk.Combobox(root, textvariable=self.bg_var, values=list(BG_OPTIONS.keys()), width=12, state="readonly").grid(row=1,column=6)
        tk.Label(root, text="Scale:").grid(row=1, column=7, sticky="e")
        ttk.Combobox(root, textvariable=self.scale_var, values=[1,10,15,20], width=5, state="readonly").grid(row=1, column=8)
        ttk.Button(root, text="Generate", command=self.on_generate).grid(row=2, column=0)
        ttk.Button(root, text="Play", command=self.on_play).grid(row=2, column=1)
        ttk.Button(root, text="Stop", command=self.on_stop).grid(row=2, column=2)
        ttk.Button(root, text="Save GIF", command=self.on_save).grid(row=2, column=3)
        ttk.Button(root, text="Quit", command=root.quit).grid(row=2, column=4)
        self.frame_images = []
        self.pil_frames = []
        self.playing = False
        self.current_frame = 0

    def on_generate(self):
        # 背景色更新
        PALETTE['bg'] = BG_OPTIONS[self.bg_var.get()]
        seed = self.seed_var.get()
        if self.rand_var.get() or not seed:
            seed = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=6))
            self.seed_var.set(seed)
        gen = GoatGenerator(seed)
        # outline_var, transp_var を引数として渡す
        self.pil_frames = gen.generate_animation(self.outline_var.get(), self.transp_var.get())
        self.frame_images = [ImageTk.PhotoImage(f.resize((FRAME_SIZE[0]*8, FRAME_SIZE[1]*8), Image.NEAREST))
                             for f in self.pil_frames]
        if hasattr(self, 'canvas_image'):
            self.canvas.itemconfig(self.canvas_image, image=self.frame_images[0])
        else:
            self.canvas_image = self.canvas.create_image(0, 0, anchor='nw', image=self.frame_images[0])
        self.current_frame = 0

    def on_play(self):
        if not self.frame_images:
            return
        self.playing = True
        self.next_frame()

    def next_frame(self):
        if not self.playing:
            return
        self.current_frame = (self.current_frame + 1) % len(self.frame_images)
        self.canvas.itemconfig(self.canvas_image, image=self.frame_images[self.current_frame])
        self.root.after(FRAME_DELAY_MS, self.next_frame)

    def on_stop(self):
        self.playing = False

    def on_save(self):
        if not self.pil_frames:
            return
        filename = filedialog.asksaveasfilename(defaultextension='.gif', filetypes=[('GIF files', '*.gif')])
        if filename:
            scale = self.scale_var.get()
            scaled = [f.resize((FRAME_SIZE[0]*scale, FRAME_SIZE[1]*scale), Image.NEAREST) for f in self.pil_frames]
            scaled[0].save(
                filename,
                save_all=True,
                append_images=scaled[1:],
                duration=FRAME_DELAY_MS,
                loop=0,
                transparency=0,
                disposal=2
            )

if __name__ == '__main__':
    root = tk.Tk()
    app = GoatApp(root)
    root.mainloop()
