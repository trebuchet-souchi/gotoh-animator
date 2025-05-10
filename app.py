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
    seed_input = st.text_input(
        "Seed（使いたい文字列）",
        value=st.session_state.seed_input,
        key="seed_input"
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
    generate_button = st.button("▶️ 生成", key="generate_button")

# ─── 生成ロジック（ボタンを押したときだけ実行） ────────────────────
if generate_button:
    # 1) シードを最終決定して state に書き戻し
    if randomize or not seed_input:
        seed = "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=6))
    else:
        seed = seed_input
    st.session_state.seed_input = seed

    # 2) URL に反映（experimental API で統一）
    st.experimental_set_query_params(seed=seed)
    
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
# 1) あなたの公開アプリのベース URL
app_base_url = "https://share.streamlit.io/trebuchet-souchi/gotoh-animator/main/app.py"

# 2) 現在のシード
current_seed = st.session_state.seed_input

# 3) seed を付与した URL
url_with_seed = f"{app_base_url}?seed={urllib.parse.quote(current_seed)}"

# 4) 投稿テキスト
app_base_url = "https://share.streamlit.io/trebuchet-souchi/gotoh-animator/main/app.py"
# 現在のシードを state から取得
current_seed = st.session_state.seed_input
# seed 付き URL を組み立て
url_with_seed = f"{app_base_url}?seed={urllib.parse.quote(current_seed)}"
# ツイート文を作成
tweet_text = f"後藤「{current_seed}」"

# 5) X Web Intent URL を組み立て
intent_url = (
    "https://twitter.com/intent/tweet"
    f"?text={urllib.parse.quote(tweet_text)}"
    f"&url={urllib.parse.quote(url_with_seed)}"
)

# 6) Markdown でリンク表示
st.markdown(
    f"[Xで後藤をシェア]({intent_url})",
    unsafe_allow_html=True
)
