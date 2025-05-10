# app.py
import random
import io
from PIL import Image
import urllib.parse
import streamlit as st
# Alias for Query API: fallback to experimental if official API is unavailable
if not hasattr(st, 'query_params'):
    st.query_params = st.experimental_get_query_params()
if not hasattr(st, 'set_query_params'):
    st.set_query_params = st.experimental_set_query_params
import gotoh
from gotoh import GoatGenerator, BG_OPTIONS

# 1. ページ設定
st.set_page_config(
    page_title="🐐 Goat Pixel Animator",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.title("🐐 Goat Pixel Animator")

# 2. クエリパラメータから初期seedを取得（正式 API）
initial_seed = st.query_params.get("seed", [""])[0]
if "seed_input" not in st.session_state:
    st.session_state.seed_input = initial_seed

# 3. セッションステートの初期化
st.session_state.setdefault("gif_bytes", None)
st.session_state.setdefault("bg_color", list(BG_OPTIONS.keys())[0])
st.session_state.setdefault("scale", 10)
st.session_state.setdefault("randomize", False)
st.session_state.setdefault("outline", False)
st.session_state.setdefault("transparent", False)

# 4. アニメ生成関数
def generate_animation():
    # シード決定
    if st.session_state.randomize or not st.session_state.seed_input:
        st.session_state.seed_input = "".join(
            random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=6)
        )
    seed = st.session_state.seed_input
        # URLにseedを反映
    if hasattr(st, "set_query_params"):  # 正式 API が利用可能なら
        st.set_query_params(seed=seed)
    else:  # なければ experimental API をフォールバックで使用
        st.experimental_set_query_params(seed=seed)
    # 背景色を反映
    gotoh.PALETTE['bg']['bg'] = BG_OPTIONS[st.session_state.bg_color]
    # フレーム生成
    gen = GoatGenerator(seed)
    frames = gen.generate_animation(
        st.session_state.outline,
        st.session_state.transparent
    )
    # GIF化
    buf = io.BytesIO()
    big = [
        f.resize((16*st.session_state.scale, 16*st.session_state.scale), Image.NEAREST)
        for f in frames
    ]
    save_kwargs = {
        'format': 'GIF',
        'save_all': True,
        'append_images': big[1:],
        'duration': 150,
        'loop': 0,
        'disposal': 2
    }
    if st.session_state.transparent:
        save_kwargs['transparency'] = 0
    big[0].save(buf, **save_kwargs)
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
        "背景色", list(BG_OPTIONS.keys()),
        key="bg_color",
        index=list(BG_OPTIONS.keys()).index(st.session_state.bg_color)
    )
    st.selectbox(
        "拡大率", [1, 10, 15, 20],
        key="scale",
        index=[1, 10, 15, 20].index(st.session_state.scale)
    )
    st.button("▶️ 生成", on_click=generate_animation, key="generate_button")

# 6. 結果表示
gif = st.session_state.gif_bytes
if gif:
    st.subheader(
        f"Seed = `{st.session_state.seed_input}` | 背景色 = {st.session_state.bg_color}"
    )
    st.image(gif, width=16*st.session_state.scale)
    # シェアリンク作成
    base = "https://share.streamlit.io/trebuchet-souchi/gotoh-animator/main/app.py"
    seed = urllib.parse.quote(st.session_state.seed_input)
    url = f"{base}?seed={seed}"
    text = urllib.parse.quote(f"後藤「{st.session_state.seed_input}」")
    intent_url = (
        f"https://twitter.com/intent/tweet?text={text}&url={urllib.parse.quote(url)}"
    )
    st.markdown(f"[Xで後藤をシェア]({intent_url})", unsafe_allow_html=True)
