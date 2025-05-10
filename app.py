# app.py
import random
import io
from PIL import Image
import streamlit as st
import gotoh
from gotoh import GoatGenerator, BG_OPTIONS
import urllib.parse
import streamlit as st

# ─── ページ設定は必ず最初に ───────────────────────────────
st.set_page_config(page_title="後藤Animator", layout="wide")
st.title("後藤Animator")

# ─── セッションステートの初期化 ────────────────────────────
# gif_bytes, last_seed, last_bg だけ保持すればOK
st.session_state.setdefault("gif_bytes", None)
st.session_state.setdefault("last_seed", "")
st.session_state.setdefault("last_bg", next(iter(BG_OPTIONS.keys())))

# ② クエリパラメータから初期シードを取得してセッションにセット
params = st.experimental_get_query_params()
initial_seed = params.get("seed", [""])[0]
# seed_input キーがなければ初回にだけセット
if "seed_input" not in st.session_state:
    st.session_state.seed_input = initial_seed

# ─── サイドバー：設定UIを常にトップレベルで定義 ─────────────────
with st.sidebar:
    st.header("Settings")

    # テキスト入力と各ウィジェット（ラベルを唯一に）
    seed_input = st.text_input(
        "Seed（使いたい文字列）",
        value=st.session_state.last_seed
    )
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
        index=list(BG_OPTIONS.keys()).index(st.session_state.last_bg)
    )
    scale = st.selectbox(
        "拡大率",
        [1, 10, 15, 20],
        index=1
    )

    # 生成ボタン（サイドバーに常時表示）
    generate_button = st.button("▶️ 生成")

# ─── 生成ロジック（ボタンを押したときだけ実行） ────────────────────
if generate_button:
    # 背景色を即反映
    gotoh.PALETTE["bg"] = BG_OPTIONS[bg_color]

    # シード決定
    if randomize or not seed_input:
        seed = "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=6))
    else:
        seed = seed_input

    # 状態を保存
    st.session_state.last_seed = seed
    st.session_state.last_bg = bg_color

    # フレーム生成
    gen = GoatGenerator(seed)
    frames = gen.generate_animation(outline, transparent)

    # リサイズ＆GIF化
    big_frames = [
        f.resize((16 * scale, 16 * scale), Image.NEAREST)
        for f in frames
    ]
    buf = io.BytesIO()
    big_frames[0].save(
        buf,
        format="GIF",
        save_all=True,
        append_images=big_frames[1:],
        duration=150,
        loop=0,
        disposal=2
    )
    buf.seek(0)
    st.session_state.gif_bytes = buf.getvalue()
    # 生成後 URL バーを書き換え（正式 API）
    st.set_query_params(seed=st.session_state.seed_input)

# ─── 結果表示 ───────────────────────────────────────────────
if st.session_state.gif_bytes:
    st.subheader(
        f"Seed = `{st.session_state.last_seed}`  |  背景色 = {st.session_state.last_bg}"
    )
    st.image(
        st.session_state.gif_bytes,
        width=16 * scale
    )

current_seed = st.session_state.seed_input
base_url = "https://share.streamlit.io/trebuchet-souchi/gotoh-animator/main/app.py"
url_with_seed = f"{base_url}?seed={urllib.parse.quote(current_seed)}"
tweet_text = f"後藤「{current_seed}」です"
intent_url = (
    "https://twitter.com/intent/tweet"
    f"?text={urllib.parse.quote(tweet_text)}"
    f"&url={urllib.parse.quote(url_with_seed)}"
)
st.markdown(f"[ Xで後藤をシェア]({intent_url})", unsafe_allow_html=True)
