# app.py
import random
import io
from PIL import Image
import urllib.parse
import streamlit as st
import gotoh
from gotoh import GoatGenerator, BG_OPTIONS

# 1. ページ設定
st.set_page_config(
    page_title="後藤 Animator",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.title("後藤 Animator")

# 2. クエリパラメータから初期seedを取得
params = st.experimental_get_query_params()
initial_seed = params.get("seed", [""])[0]
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
    # URLにseedを反映
    st.experimental_set_query_params(seed=st.session_state.seed_input)
    # 背景色反映
    gotoh.PALETTE['bg'] = BG_OPTIONS[st.session_state.bg_color]
    # フレーム生成
    gen = GoatGenerator(st.session_state.seed_input)
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
    # save_all と disposal は常に指定
    save_kwargs = {
        'format': 'GIF',
        'save_all': True,
        'append_images': big[1:],
        'duration': 150,
        'loop': 0,
        'disposal': 2
    }
    # 透明背景時のみ transparency を指定
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
        "背景色",
        list(BG_OPTIONS.keys()),
        key="bg_color",
        index=list(BG_OPTIONS.keys()).index(st.session_state.bg_color)
    )
    st.selectbox(
        "拡大率",
        [1, 10, 15, 20],
        key="scale",
        index=[1,10,15,20].index(st.session_state.scale)
    )
    st.button("▶️ 生成", on_click=generate_animation, key="generate_button")

# 6. 結果表示
if st.session_state.gif_bytes:
    st.subheader(
        f"Seed = `{st.session_state.seed_input}` | 背景色 = {st.session_state.bg_color}"
    )
    st.image(
        st.session_state.gif_bytes,
        width=16*st.session_state.scale
    )
    # シェアリンク作成
    base = "https://share.streamlit.io/trebuchet-souchi/gotoh-animator/main/app.py"
    seed = urllib.parse.quote(st.session_state.seed_input)
    url = f"{base}?seed={seed}"
    text = urllib.parse.quote(f"後藤「{st.session_state.seed_input}」")
    intent_url = f"https://twitter.com/intent/tweet?text={text}&url={urllib.parse.quote(url)}"
    st.markdown(f"[Xで後藤をシェア]({intent_url})", unsafe_allow_html=True)
