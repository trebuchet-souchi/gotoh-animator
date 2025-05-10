# app.py
import random
import io
import urllib.parse
from PIL import Image
import streamlit as st
import gotoh
from gotoh import GoatGenerator, BG_OPTIONS

# 1. ページ設定
st.set_page_config(
    page_title="🐐 Goat Pixel Animator",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.title("🐐 Goat Pixel Animator")

# 2. URL クエリパラメータから初期シードを取得
initial_seed = st.query_params.get("seed", [""])[0]

# 3. サイドバーUI（seed_input は state を使わず、常に initial_seed をデフォルトに表示）
with st.sidebar:
    st.header("Settings")
    seed_input = st.text_input(
        "Seed（使いたい文字列）",
        value=initial_seed,
        help="ここを編集すると手動でseedを指定できます。",
    )
    randomize   = st.checkbox("🔀 ランダムシードにする", value=False)
    outline     = st.checkbox("輪郭を表示", value=False)
    transparent = st.checkbox("背景を透明に", value=False)
    bg_color    = st.selectbox(
        "背景色", list(BG_OPTIONS.keys()),
        index=list(BG_OPTIONS.keys()).index(defaults['bg_color'])
    )
    scale       = st.selectbox(
        "拡大率", [1, 10, 15, 20],
        index=[1,10,15,20].index(defaults['scale'])
    )
    gen_btn     = st.button("▶️ 生成")

# 4. アニメ生成関数は不要。以下で直接制御します
if gen_btn or (initial_seed and st.session_state['gif_bytes'] is None):
    # シード決定
    if randomize or not seed_input:
        seed = "".join(random.choices(
            "abcdefghijklmnopqrstuvwxyz0123456789", k=6
        ))
    else:
        seed = seed_input
    
    # 背景色反映
    gotoh.PALETTE['bg'] = BG_OPTIONS[bg_color]

    # フレーム生成
    gen = GoatGenerator(seed)
    frames = gen.generate_animation(outline, transparent)

    # GIF 化
    buf = io.BytesIO()
    big_frames = [
        f.resize((16*scale, 16*scale), Image.NEAREST)
        for f in frames
    ]
    save_kwargs = {'format':'GIF','save_all':True,
                   'append_images':big_frames[1:],
                   'duration':150,'loop':0,'disposal':2}
    if transparent:
        save_kwargs['transparency'] = 0
    big_frames[0].save(buf, **save_kwargs)
    buf.seek(0)
    st.session_state['gif_bytes'] = buf.getvalue()

# 5. 結果表示
if st.session_state['gif_bytes']:
    st.subheader(f"Seed = `{seed}` | 背景色 = {bg_color}")
    st.image(st.session_state['gif_bytes'], width=16*scale)

    # シェアリンク作成
    base_url = ("https://share.streamlit.io/trebuchet-souchi/gotoh-animator/main/app.py")
    url_with_seed = f"{base_url}?seed={urllib.parse.quote(seed)}"
    text_quoted = urllib.parse.quote(f"後藤「{seed}」")
    intent_url = f"https://twitter.com/intent/tweet?text={text_quoted}&url={urllib.parse.quote(url_with_seed)}"
    st.markdown(f"[Xで後藤をシェア]({intent_url})", unsafe_allow_html=True) セッションステートの初期値設定
defaults = {
    "gif_bytes": None,
    "bg_color": list(BG_OPTIONS.keys())[0],
    "scale": 10,
    "randomize": False,
    "outline": False,
    "transparent": False,
}
for key, val in defaults.items():
    st.session_state.setdefault(key, val)

# 4. アニメ生成関数
def generate_animation():
    # シード決定
    if st.session_state.randomize or not st.session_state.seed_input:
        st.session_state.seed_input = "".join(
            random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=6)
        )
    seed = st.session_state.seed_input

    # 背景色反映
    gotoh.PALETTE['bg'] = BG_OPTIONS[st.session_state.bg_color]

    # フレーム生成
    gen = GoatGenerator(seed)
    frames = gen.generate_animation(
        st.session_state.outline,
        st.session_state.transparent
    )

    # GIF 化
    buf = io.BytesIO()
    big_frames = [
        f.resize((16 * st.session_state.scale, 16 * st.session_state.scale), Image.NEAREST)
        for f in frames
    ]
    save_kwargs = {
        'format': 'GIF',
        'save_all': True,
        'append_images': big_frames[1:],
        'duration': 150,
        'loop': 0,
        'disposal': 2,
    }
    if st.session_state.transparent:
        save_kwargs['transparency'] = 0
    big_frames[0].save(buf, **save_kwargs)
    buf.seek(0)
    st.session_state.gif_bytes = buf.getvalue()

# 5. サイドバーUI
with st.sidebar:
    st.header("Settings")
    # シード入力（セッションステートと同期）
        # シード入力（セッションステートと同期）
    seed_input = st.text_input(
        "Seed（使いたい文字列）",
        value=st.session_state.seed_input,
        key="seed_input"
    )
    st.checkbox("🔀 ランダムシードにする", key="randomize")
    st.checkbox("輪郭を表示", key="outline")
    st.checkbox("背景を透明に", key="transparent")
    st.selectbox(
        "背景色",
        list(BG_OPTIONS.keys()),
        key="bg_color",
        index=list(BG_OPTIONS.keys()).index(st.session_state.bg_color)
    )
    st.selectbox(
        "拡大率",
        [1, 10, 15, 20],
        key="scale",
        index=[1, 10, 15, 20].index(st.session_state.scale)
    )
    st.button("▶️ 生成", on_click=generate_animation, key="generate_button")

# 6. 初回ロード時の自動生成
if initial_seed and st.session_state.gif_bytes is None:
    generate_animation()

# 7. 結果表示
if st.session_state.gif_bytes:
    st.subheader(
        f"Seed = `{st.session_state.seed_input}` | 背景色 = {st.session_state.bg_color}"
    )
    st.image(
        st.session_state.gif_bytes,
        width=16 * st.session_state.scale
    )

    # 8. シェアリンク作成
    base_url = (
        "https://share.streamlit.io/"
        "trebuchet-souchi/gotoh-animator/main/app.py"
    )
    seed_quoted = urllib.parse.quote(st.session_state.seed_input)
    url_with_seed = f"{base_url}?seed={seed_quoted}"
    text_quoted = urllib.parse.quote(f"後藤「{st.session_state.seed_input}」")
    intent_url = (
        f"https://twitter.com/intent/tweet?text={text_quoted}"
        f"&url={urllib.parse.quote(url_with_seed)}"
    )
    st.markdown(
        f"[Xで後藤をシェア]({intent_url})",
        unsafe_allow_html=True
    )
