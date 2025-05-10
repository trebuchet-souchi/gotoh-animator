# app.py
import random
import io
from PIL import Image
import urllib.parse
import streamlit as st
import gotoh
from gotoh import GoatGenerator, BG_OPTIONS

# ─── ページ設定は必ず最初に ───────────────────────────────
st.set_page_config(page_title="後藤Animator", layout="wide")
st.title("後藤Animator")

# ─── 1) クエリから seed の初期値を読み込んで state にセット ──────────
params = st.experimental_get_query_params()
initial_seed = params.get("seed", [""])[0]
if "seed_input" not in st.session_state:
    st.session_state.seed_input = initial_seed

# ─── セッションステートの初期化 ────────────────────────────
st.session_state.setdefault("gif_bytes", None)
st.session_state.setdefault("bg_color", next(iter(BG_OPTIONS.keys())))
st.session_state.setdefault("scale", 10)

# ─── サイドバー：設定UIを常にトップレベルで定義 ─────────────────
with st.sidebar:
    st.header("Settings")

    # テキスト入力と各ウィジェット（ラベルを唯一に）
    seed_input = st.text_input("Seed（使いたい文字列）", key="seed_input")
    
    randomize = st.checkbox(
        "🔀 ランダムシードにする",
        value=(seed_input == "")
    )
    outline = st.checkbox(
        "後藤に輪郭をつける",
        value=False
    )
    transparent = st.checkbox(
        "背景を透明に",
        value=False
    )
    bg_color = st.selectbox(
        "背景色",
        options=list(BG_OPTIONS.keys()),
        index=list(BG_OPTIONS.keys()).index(st.session_state.bg_color),
        key="bg_color"
    )
    scale = st.selectbox(
        "拡大率",
        [1, 10, 15, 20],
        index=[1,10,15,20].index(st.session_state.scale),
        key="scale"
    )

    # 生成ボタン（サイドバーに常時表示）
    st.button("▶️ 生成", on_click=generate_animation, key="gen_btn")

# ─── 生成ロジック（ボタンを押したときだけ実行） ────────────────────
def generate_animation():
    # → この中でのみ st.session_state.seed_input を書き換える
    if randomize or not st.session_state.seed_input:
        new_seed = "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=6))
        st.session_state.seed_input = new_seed

    # URL に seed を反映
    st.experimental_set_query_params(seed=st.session_state.seed_input)

    # 背景色反映
    gotoh.PALETTE["bg"] = BG_OPTIONS[st.session_state.bg_color]

    # アニメ生成
    gen = GoatGenerator(st.session_state.seed_input)
    frames = gen.generate_animation(st.session_state.outline, st.session_state.transparent)

    # GIF 化
    big_frames = [
        f.resize((16 * st.session_state.scale, 16 * st.session_state.scale), Image.NEAREST)
        for f in frames
    ]
    buf = io.BytesIO()
    big_frames[0].save(
        buf, format="GIF", save_all=True, append_images=big_frames[1:],
        duration=150, loop=0, disposal=2
    )
    buf.seek(0)
    st.session_state.gif_bytes = buf.getvalue()

# ─── 結果表示 ───────────────────────────────────────────────
if st.session_state.gif_bytes:
    st.subheader(
        f"Seed = `{st.session_state.last_seed}`  |  背景色 = {st.session_state.last_bg}"
    )
    st.image(
        st.session_state.gif_bytes,
        width=16 * scale
    )
# ─── シェアリンクを作る ────────────────────
if st.session_state.gif_bytes:
    st.subheader(f"Seed = `{st.session_state.seed_input}`  |  背景色 = {st.session_state.bg_color}")
    st.image(st.session_state.gif_bytes, width=16 * st.session_state.scale)

    # シェアリンク
    app_base = "https://share.streamlit.io/trebuchet-souchi/gotoh-animator/main/app.py"
    seed = st.session_state.seed_input
    url_with_seed = f"{app_base}?seed={urllib.parse.quote(seed)}"
    text = f"後藤「{seed}」"
    intent = (
        "https://twitter.com/intent/tweet"
        f"?text={urllib.parse.quote(text)}"
        f"&url={urllib.parse.quote(url_with_seed)}"
    )
    st.markdown(f"[Xで後藤をシェア]({intent})", unsafe_allow_html=True)
