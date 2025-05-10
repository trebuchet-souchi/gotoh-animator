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
if "seed_input" not in st.session_state:
    st.session_state.seed_input = initial_seed

# 3. セッションステートの初期値設定
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
    st.text_input("Seed（使いたい文字列）", key="seed_input")
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
if initial_seed:
    # すでにgif_bytesがある場合は再生成を避ける
    if st.session_state.gif_bytes is None:
        generate_animation()

# 7. 結果表示
gif = st.session_state.gif_bytes
if gif:
    st.subheader(
        f"Seed = `{st.session_state.seed_input}` | 背景色 = {st.session_state.bg_color}"
    )
    st.image(
        gif,
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
