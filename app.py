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
    page_title="🐐 Goat Pixel Animator",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🐐 Goat Pixel Animator")

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

# 4. サイドバーで設定
with st.sidebar:
    st.header("Settings")
    # シード入力
    seed_input = st.text_input(
        "Seed（使いたい文字列）",
        value=st.session_state.seed_input,
        key="seed_input"
    )
    # オプション
    st.checkbox("🔀 ランダムシードにする", key="randomize")
    st.checkbox("輪郭を表示", key="outline")
    st.checkbox("背景を透明に", key="transparent")
    # 背景色プルダウン（セッションから初期値取得）
    bg_color = st.selectbox(
        "背景色",
        list(BG_OPTIONS.keys()),
        key="bg_color",
        index=list(BG_OPTIONS.keys()).index(st.session_state.bg_color)
    )
    # 拡大率プルダウン
    scale = st.selectbox(
        "拡大率",
        [1, 10, 15, 20],
        key="scale",
        index=[1, 10, 15, 20].index(st.session_state.scale)
    )
    # 生成ボタン
    st.button("▶️ 生成", on_click=None, key="generate_button")

# 5. 生成処理（ボタンはコールバックで直接呼び出す場合に on_click指定可）
if st.session_state.get("generate_button_clicks", 0) > 0:
    # 背景色を反映
    gotoh.PALETTE['bg'] = BG_OPTIONS[st.session_state.bg_color]
    # シードを決定
    if st.session_state.randomize or not seed_input:
        st.session_state.seed_input = "".join(
            random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=6)
        )
    seed = st.session_state.seed_input
    # URLにseedを書く
    st.experimental_set_query_params(seed=seed)
    # アニメ生成
    gen = GoatGenerator(seed)
    frames = gen.generate_animation(
        st.session_state.outline,
        st.session_state.transparent
    )
    # GIF化
    buf = io.BytesIO()
    big_frames = [f.resize((16*st.session_state.scale,16*st.session_state.scale),Image.NEAREST) for f in frames]
    big_frames[0].save(
        buf, format='GIF', save_all=True, append_images=big_frames[1:],
        duration=150, loop=0, disposal=2, transparency=0
    )
    buf.seek(0)
    st.session_state.gif_bytes = buf.getvalue()

# 6. 結果表示
gif = st.session_state.gif_bytes
if gif:
    st.subheader(f"Seed = `{st.session_state.seed_input}` | 背景色 = {st.session_state.bg_color}")
    st.image(gif, width=16*st.session_state.scale)
    # シェアリンク作成
    base_url = "https://share.streamlit.io/trebuchet-souchi/gotoh-animator/main/app.py"
    url_with_seed = f"{base_url}?seed={urllib.parse.quote(st.session_state.seed_input)}"
    tweet_text = f"後藤「{st.session_state.seed_input}」"
    intent_url = (
        "https://twitter.com/intent/tweet"
        f"?text={urllib.parse.quote(tweet_text)}"
        f"&url={urllib.parse.quote(url_with_seed)}"
    )
    st.markdown(f"[Xで後藤をシェア]({intent_url})", unsafe_allow_html=True)
