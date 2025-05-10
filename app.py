# app.py
import urllib.parse
import random
import io
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

# 2. クエリパラメータから初期seedを取得
params = st.experimental_get_query_params()
initial_seed = params.get("seed", [""])[0]

# 3. サイドバー：各種設定
with st.sidebar:
    st.header("Settings")
    seed_input = st.text_input(
        "Seed（使いたい文字列）",
        value=initial_seed,
        key="seed_input"
    )
    randomize = st.checkbox("🔀 ランダムシードにする", value=(seed_input == ""))
    outline = st.checkbox("輪郭を表示", value=False)
    transparent = st.checkbox("背景を透明に", value=False)
    bg_color = st.selectbox(
        "背景色",
        list(BG_OPTIONS.keys()),
        index=list(BG_OPTIONS.keys()).index(gotoh.PALETTE['bg'])
    )
    scale = st.selectbox(
        "拡大率",
        [1, 10, 15, 20],
        index=1
    )
    generate_button = st.button("▶️ 生成")

# 4. 生成処理
if generate_button:
    # 背景色反映
    gotoh.PALETTE['bg'] = BG_OPTIONS[bg_color]
    # シード決定
    if randomize or not seed_input:
        seed_input = "".join(random.choices(
            'abcdefghijklmnopqrstuvwxyz0123456789', k=6
        ))
    # クエリパラメータ更新
    st.experimental_set_query_params(seed=seed_input)
    # フレーム生成
    gen = GoatGenerator(seed_input)
    frames = gen.generate_animation(outline, transparent)
    # GIF 化
    big_frames = [
        f.resize((16 * scale, 16 * scale), Image.NEAREST) for f in frames
    ]
    buf = io.BytesIO()
    big_frames[0].save(
        buf,
        format='GIF',
        save_all=True,
        append_images=big_frames[1:],
        duration=150,
        loop=0,
        disposal=2,
        transparency=0
    )
    buf.seek(0)
    st.session_state.gif_bytes = buf.getvalue()
    st.session_state.last_seed = seed_input
    st.session_state.last_bg = bg_color

# 5. 結果表示
gif = st.session_state.get('gif_bytes', None)
if gif:
    st.subheader(
        f"Seed = `{st.session_state.last_seed}`  |  背景色 = {st.session_state.last_bg}"
    )
    st.image(gif, width=16 * scale)

# 6. 【ここにシェアリンクを挿入】
# シェアリンクは結果表示のすぐ下に配置します。
# ツイートに含めるseed値付きURLを生成し、X（旧Twitter）intentで開くようにします。
snippet = st.empty()  # プレースホルダー
if gif:
    base_url = "https://share.streamlit.io/trebuchet-souchi/gotoh-animator/main/app.py"
    current_seed = st.session_state.last_seed
    url_with_seed = f"{base_url}?seed={urllib.parse.quote(current_seed)}"
    tweet_text = f"後藤"
    intent_url = (
        "https://twitter.com/intent/tweet"
        f"?text={urllib.parse.quote(tweet_text)}"
        f"&url={urllib.parse.quote(url_with_seed)}"
    )
    snippet.markdown(
        f"[Xで後藤をシェア]({intent_url})",
        unsafe_allow_html=True
    )
