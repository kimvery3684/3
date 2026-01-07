import streamlit as st
import random
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import os

# --- [1. 기본 설정] ---
st.set_page_config(page_title="숫자 퀴즈 생성기 (대본수정)", page_icon="🎯", layout="wide")

FONT_FILE = "NanumGothic-ExtraBold.ttf"

# --- [2. 비밀번호 보안] ---
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state.password_correct = False
    if st.session_state.password_correct:
        return True
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.warning("🔒 접속하려면 비밀번호가 필요합니다.")
        password_input = st.text_input("비밀번호", type="password")
        CORRECT_PASSWORD = st.secrets["APP_PASSWORD"] if "APP_PASSWORD" in st.secrets else "1234"
        if password_input:
            if password_input == CORRECT_PASSWORD:
                st.session_state.password_correct = True
                st.rerun()
            else:
                st.error("비밀번호가 틀렸습니다.")
    return False

if not check_password(): st.stop()

# --- [3. 폰트 로드 (안전장치)] ---
def get_font(size):
    if os.path.exists(FONT_FILE):
        return ImageFont.truetype(FONT_FILE, size)
    else:
        return ImageFont.load_default()

if not os.path.exists(FONT_FILE):
    st.error(f"🚨 폰트 파일({FONT_FILE})이 없습니다! 한글이 깨질 수 있습니다.")

# --- [4. 이미지 생성 엔진] ---
def create_puzzle_image(base, target, rows, cols, d, show_answer=False):
    canvas = Image.new('RGB', (1080, 1920), d['bg_color'])
    draw = ImageDraw.Draw(canvas)
    
    font_h1 = get_font(d['h1_size'])
    font_h2 = get_font(d['h2_size'])
    font_main = get_font(d['main_size'])
    font_bot = get_font(d['bot_size'])

    # [섹션 1: 상단 헤더]
    draw.rectangle([(0, 0), (1080, d['header_height'])], fill=d['header_bg'])
    
    h1_text = d['h1_text']
    try:
        bbox1 = draw.textbbox((0, 0), h1_text, font=font_h1)
        w1 = bbox1[2] - bbox1[0]
        draw.text(((1080 - w1) / 2, d['h1_y']), h1_text, font=font_h1, fill=d['h1_color'])
    except: pass

    h2_text = d['h2_text'].replace("{target}", target).replace("{base}", base)
    try:
        bbox2 = draw.textbbox((0, 0), h2_text, font=font_h2)
        w2 = bbox2[2] - bbox2[0]
        draw.text(((1080 - w2) / 2, d['h2_y']), h2_text, font=font_h2, fill=d['h2_color'])
    except: pass

    # [섹션 2: 중앙 숫자 그리드]
    if 'answer_pos' not in st.session_state:
        st.session_state.answer_pos = (random.randint(0, rows-1), random.randint(0, cols-1))
    ans_r, ans_c = st.session_state.answer_pos

    for r in range(rows):
        for c in range(cols):
            x = d['grid_start_x'] + (c * d['spacing_x'])
            y = d['grid_start_y'] + (r * d['spacing_y'])
            
            is_target = (r == ans_r and c == ans_c)
            text_content = target if is_target else base
            
            draw.text((x, y), text_content, font=font_main, fill=d['main_color'], anchor="mm")
            
            if show_answer and is_target:
                box_s = d['main_size'] * 0.75
                draw.rectangle([x - box_s, y - box_s, x + box_s, y + box_s], outline="#FF0000", width=10)

    # [섹션 3: 하단 문구]
    bot_text = d['bot_text']
    try:
        bbox_b = draw.textbbox((0, 0), bot_text, font=font_bot, spacing=d['bot_spacing'])
        wb = bbox_b[2] - bbox_b[0]
        draw.text(
            ((1080 - wb) / 2, d['bot_y']), 
            bot_text, 
            font=font_bot, 
            fill=d['bot_color'], 
            align="center", 
            spacing=d['bot_spacing']
        )
    except: pass

    return canvas

# --- [5. 유튜브 메타데이터 생성 (수정됨)] ---
def generate_metadata(base, target):
    title = f"3초 안에 숫자 '{target}' 찾기 도전! ⏱️ #shorts"
    
    # [요청하신 대본 내용으로 정확히 수정]
    desc = f"3초안에 숫자 [{target}]를 찾으면 정답을 톡톡 두번 터치해주세요\n\n#두뇌퀴즈 #시력테스트 #shorts"
    
    tags = f"두뇌퀴즈, 시력테스트, 집중력, 치매예방, 숫자퀴즈, {base}, {target}, 뇌훈련, shorts"
    return title, desc, tags

# --- [6. 메인 컨트롤 패널 (UI)] ---
st.title("🎯 숫자 퀴즈 생성기 (대본 수정완료)")

# === [사이드바 컨트롤] ===
with st.sidebar:
    st.header("🎚️ 디자인 설정 패널")
    
    # 1. 상단 헤더
    with st.expander("1. 상단 제목 (2줄 설정)", expanded=True):
        st.markdown("### 🟦 헤더 박스")
        header_height = st.slider("헤더 높이", 100, 600, 350)
        header_bg = st.color_picker("헤더 배경색", "#112D4E")
        
        st.markdown("### 📝 첫 번째 줄 (큰 제목)")
        h1_text = st.text_input("내용 1", "숫자 찾기 도전")
        h1_size = st.slider("글자 크기 1", 40, 150, 90)
        h1_y = st.slider("위치 Y (1)", 10, 300, 50)
        h1_color = st.color_picker("글자 색 1", "#FFFFFF")
        
        st.markdown("### 📝 두 번째 줄 (노란색 강조)")
        h2_text = st.text_input("내용 2", "3초 안에 숫자 '{target}' 찾기")
        st.caption("'{target}'은 찾는 숫자로 자동 변환됩니다.")
        h2_size = st.slider("글자 크기 2", 40, 150, 80)
        h2_y = st.slider("위치 Y (2)", 50, 500, 180)
        h2_color = st.color_picker("글자 색 2", "#FFC300")

    # 2. 중앙 그리드
    with st.expander("2. 숫자판 배치 & 간격", expanded=True):
        col_r, col_c = st.columns(2)
        rows = col_r.number_input("세로 줄 수", 5, 20, 10)
        cols = col_c.number_input("가로 줄 수", 3, 15, 6)
        
        st.markdown("---")
        main_size = st.slider("숫자 크기", 30, 150, 80)
        main_color = st.color_picker("숫자 색상", "#000000")
        
        st.markdown("### 📏 간격 및 위치")
        spacing_x = st.slider("가로 간격 (↔️)", 50, 250, 140)
        spacing_y = st.slider("세로 간격 (↕️)", 50, 250, 120)
        grid_start_x = st.slider("시작점 X", 0, 500, 180)
        grid_start_y = st.slider("시작점 Y", 200, 1500, 450)

    # 3. 하단 문구
    with st.expander("3. 하단 문구 설정", expanded=True):
        bot_text = st.text_area("내용", "정답은 댓글에서 확인하세요!\n구독과 좋아요는 사랑입니다 ❤️")
        bot_size = st.slider("하단 글자 크기", 30, 100, 50)
        bot_color = st.color_picker("하단 글자 색", "#000000")
        bot_y = st.slider("위치 Y (아래쪽)", 1000, 1900, 1650)
        bot_spacing = st.slider("줄 간격 (넓히기)", 0, 100, 20)
        
    bg_color = st.color_picker("전체 배경색", "#FFFFFF")

    design = {
        'bg_color': bg_color, 'header_height': header_height, 'header_bg': header_bg,
        'h1_text': h1_text, 'h1_size': h1_size, 'h1_y': h1_y, 'h1_color': h1_color,
        'h2_text': h2_text, 'h2_size': h2_size, 'h2_y': h2_y, 'h2_color': h2_color,
        'main_size': main_size, 'main_color': main_color,
        'spacing_x': spacing_x, 'spacing_y': spacing_y,
        'grid_start_x': grid_start_x, 'grid_start_y': grid_start_y,
        'bot_text': bot_text, 'bot_size': bot_size, 'bot_color': bot_color,
        'bot_y': bot_y, 'bot_spacing': bot_spacing
    }

# === [메인 화면 구성] ===
c1, c2 = st.columns([1, 1.5])

with c1:
    st.subheader("📝 문제 입력")
    base_text = st.text_input("바탕 글자 (많은 거)", "98")
    target_text = st.text_input("찾을 글자 (정답)", "89")
    
    if st.button("🚀 퀴즈 이미지 생성", type="primary"):
        st.session_state.answer_pos = (random.randint(0, rows-1), random.randint(0, cols-1))
        st.session_state.generated = True
        st.rerun()

with c2:
    if st.session_state.get('generated', False):
        st.subheader("🖼️ 결과물 확인")
        tab1, tab2 = st.tabs(["문제용 이미지", "정답용 이미지"])
        
        img_q = create_puzzle_image(base_text, target_text, rows, cols, design, False)
        img_a = create_puzzle_image(base_text, target_text, rows, cols, design, True)
        
        with tab1:
            st.image(img_q)
            buf = BytesIO()
            img_q.save(buf, format="JPEG", quality=100)
            st.download_button("💾 문제 다운로드", buf.getvalue(), "quiz.jpg", "image/jpeg", use_container_width=True)
            
        with tab2:
            st.image(img_a)
            buf = BytesIO()
            img_a.save(buf, format="JPEG", quality=100)
            st.download_button("💾 정답 다운로드", buf.getvalue(), "answer.jpg", "image/jpeg", use_container_width=True)
            
        st.divider()
        # [수정됨] 변경된 메타데이터 생성 함수 호출
        t, d, tags = generate_metadata(base_text, target_text)
        st.text_input("유튜브 제목", t)
        st.text_area("설명란 (대본)", d, height=150) # 높이 조절
        st.text_area("태그", tags)