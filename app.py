import streamlit as st
import random
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import os

# --- [1. 기본 설정] ---
st.set_page_config(page_title="JJ 숫자 퀴즈 마스터", page_icon="🎨", layout="wide")

FONT_FILE = "NanumGothic-ExtraBold.ttf"

# --- [2. 폰트 로드] ---
def get_font(size):
    if os.path.exists(FONT_FILE):
        return ImageFont.truetype(FONT_FILE, size)
    else:
        return ImageFont.load_default()

if not os.path.exists(FONT_FILE):
    st.error(f"🚨 폰트 파일({FONT_FILE})이 없습니다! 한글이 깨질 수 있습니다.")

# --- [3. 이미지 생성 엔진] ---
def create_puzzle_image(base, target, rows, cols, d, show_answer=False):
    # 1. 캔버스 생성 (1080x1920)
    canvas = Image.new('RGB', (1080, 1920), d['bg_color'])
    draw = ImageDraw.Draw(canvas)
    
    # 폰트 로드
    font_top = get_font(d['top_fs'])
    font_bot = get_font(d['bot_fs'])
    font_main = get_font(d['main_size'])

    # === [A. 상단 바 영역 (Top Bar)] ===
    # HTML의 #top-bar { height: var(--top-h); background: var(--top-bg); } 구현
    draw.rectangle([(0, 0), (1080, d['top_h'])], fill=d['top_bg'])
    
    # 상단 텍스트 그리기 (정중앙 정렬)
    # 텍스트 내용 치환 ({target} -> 실제 숫자)
    top_content = d['top_text'].replace("{target}", target).replace("{base}", base)
    
    # 박스의 정중앙 좌표 계산
    top_center_x = 1080 / 2
    top_center_y = d['top_h'] / 2
    
    draw.text(
        (top_center_x, top_center_y), 
        top_content, 
        font=font_top, 
        fill=d['top_color'], 
        anchor="mm", 
        align="center",
        spacing=d['top_lh']
    )

    # === [B. 하단 바 영역 (Bottom Bar)] ===
    # HTML의 #bot-bar { height: var(--bot-h); background: var(--bottom-bg); } 구현
    # 하단 바는 캔버스 맨 아래에 위치해야 함 (1920 - 높이)
    bot_y_start = 1920 - d['bot_h']
    draw.rectangle([(0, bot_y_start), (1080, 1920)], fill=d['bot_bg'])
    
    # 하단 텍스트 그리기 (정중앙 정렬)
    bot_center_x = 1080 / 2
    bot_center_y = bot_y_start + (d['bot_h'] / 2)
    
    draw.text(
        (bot_center_x, bot_center_y), 
        d['bot_text'], 
        font=font_bot, 
        fill=d['bot_color'], 
        anchor="mm", 
        align="center",
        spacing=d['bot_lh']
    )

    # === [C. 중앙 숫자 그리드 (Grid)] ===
    # 정답 위치 랜덤 생성
    if 'answer_pos' not in st.session_state:
        st.session_state.answer_pos = (random.randint(0, rows-1), random.randint(0, cols-1))
    ans_r, ans_c = st.session_state.answer_pos

    for r in range(rows):
        for c in range(cols):
            x = d['grid_start_x'] + (c * d['spacing_x'])
            y = d['grid_start_y'] + (r * d['spacing_y'])
            
            is_target = (r == ans_r and c == ans_c)
            text_content = target if is_target else base
            
            # 숫자 그리기
            draw.text((x, y), text_content, font=font_main, fill=d['main_color'], anchor="mm")
            
            # 정답 박스 (정답 이미지용)
            if show_answer and is_target:
                box_s = d['main_size'] * 0.75
                draw.rectangle([x - box_s, y - box_s, x + box_s, y + box_s], outline="#FF0000", width=10)

    return canvas

# --- [4. 메인 컨트롤 패널] ---
st.title("🎨 JJ 숫자 퀴즈 마스터")

# === [왼쪽 사이드바: HTML 제어 패널 이식] ===
with st.sidebar:
    st.header("⚙️ 디자인 제어 패널")
    
    # 1. 상단 바 설정
    with st.expander("1. ⬆️ 상단바 (Top Bar)", expanded=True):
        top_text = st.text_input("상단 문구", "3초 안에 숫자 '{target}' 찾기")
        
        # HTML: --top-h, --top-fs
        top_h = st.slider("높이 (Height)", 50, 400, 250)
        top_fs = st.slider("글자 크기 (Font Size)", 20, 150, 90)
        top_lh = st.slider("줄간격 (Line Height)", 0, 100, 20)
        
        col_t1, col_t2 = st.columns(2)
        top_bg = col_t1.color_picker("배경색 (Top BG)", "#112D4E")
        top_color = col_t2.color_picker("글자색 (Top Color)", "#FFFFFF")

    # 2. 하단 바 설정
    with st.expander("2. ⬇️ 하단바 (Bottom Bar)", expanded=True):
        bot_text = st.text_area("하단 문구", "정답은 댓글에서 확인하세요!\n구독과 좋아요는 사랑입니다 ❤️")
        
        # HTML: --bot-h, --bot-fs
        bot_h = st.slider("높이 (Height)", 50, 400, 200)
        bot_fs = st.slider("글자 크기 (Font Size)", 20, 100, 50)
        bot_lh = st.slider("줄간격 (Line Height)", 0, 100, 30)
        
        col_b1, col_b2 = st.columns(2)
        bot_bg = col_b1.color_picker("배경색 (Bot BG)", "#000000")
        bot_color = col_b2.color_picker("글자색 (Bot Color)", "#FFFFFF")

    # 3. 중앙 그리드 설정
    with st.expander("3. 🔢 중앙 숫자판 (Grid)", expanded=False):
        col_r, col_c = st.columns(2)
        rows = col_r.number_input("세로 줄 수", 5, 20, 10)
        cols = col_c.number_input("가로 줄 수", 3, 15, 6)
        
        main_size = st.slider("숫자 크기", 30, 150, 80)
        main_color = st.color_picker("숫자 색상", "#000000")
        
        st.caption("간격/위치 미세조정")
        spacing_x = st.slider("가로 간격 (X Spacing)", 50, 250, 140)
        spacing_y = st.slider("세로 간격 (Y Spacing)", 50, 250, 120)
        grid_start_x = st.slider("시작점 X", 0, 500, 180)
        grid_start_y = st.slider("시작점 Y", 200, 1500, 400)
        
    bg_color = st.color_picker("전체 배경색 (Main BG)", "#FFFFFF")

    # 디자인 데이터 패킹
    design = {
        'bg_color': bg_color,
        'top_h': top_h, 'top_fs': top_fs, 'top_lh': top_lh, 'top_bg': top_bg, 'top_color': top_color, 'top_text': top_text,
        'bot_h': bot_h, 'bot_fs': bot_fs, 'bot_lh': bot_lh, 'bot_bg': bot_bg, 'bot_color': bot_color, 'bot_text': bot_text,
        'main_size': main_size, 'main_color': main_color,
        'spacing_x': spacing_x, 'spacing_y': spacing_y,
        'grid_start_x': grid_start_x, 'grid_start_y': grid_start_y
    }

# === [메인 화면] ===
c1, c2 = st.columns([1, 1.5])

with c1:
    st.subheader("📝 숫자 설정")
    base_text = st.text_input("바탕 숫자 (많은 거)", "98")
    target_text = st.text_input("정답 숫자 (하나)", "89")
    
    if st.button("🚀 이미지 생성", type="primary", use_container_width=True):
        st.session_state.answer_pos = (random.randint(0, rows-1), random.randint(0, cols-1))
        st.session_state.generated = True
        st.rerun()

with c2:
    if st.session_state.get('generated', False):
        st.subheader("🖼️ 미리보기")
        tab1, tab2 = st.tabs(["문제용", "정답용"])
        
        img_q = create_puzzle_image(base_text, target_text, rows, cols, design, False)
        img_a = create_puzzle_image(base_text, target_text, rows, cols, design, True)
        
        with tab1:
            st.image(img_q, use_container_width=True)
            buf = BytesIO()
            img_q.save(buf, format="JPEG", quality=100)
            st.download_button("💾 문제 이미지 다운로드", buf.getvalue(), "quiz.jpg", "image/jpeg", use_container_width=True)
            
        with tab2:
            st.image(img_a, use_container_width=True)
            buf = BytesIO()
            img_a.save(buf, format="JPEG", quality=100)
            st.download_button("💾 정답 이미지 다운로드", buf.getvalue(), "answer.jpg", "image/jpeg", use_container_width=True)