import streamlit as st
import random
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import os

# --- [1. 기본 설정] ---
st.set_page_config(page_title="숫자 퀴즈 마스터", page_icon="🎛️", layout="wide")

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

# --- [3. 폰트 로드] ---
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

    # === [상단 헤더 영역] ===
    # 1. 배경 박스 (높이 조절 반영)
    draw.rectangle([(0, 0), (1080, d['header_height'])], fill=d['header_bg'])
    
    # 2. 제목 1 (큰 제목)
    h1_text = d['h1_text']
    try:
        bbox1 = draw.textbbox((0, 0), h1_text, font=font_h1, spacing=d['h1_spacing'])
        w1 = bbox1[2] - bbox1[0]
        # 중앙 정렬 + 줄간격(spacing) 적용
        draw.text(((1080 - w1) / 2, d['h1_y']), h1_text, font=font_h1, fill=d['h1_color'], align="center", spacing=d['h1_spacing'])
    except: pass

    # 3. 제목 2 (작은 제목 - 자동 치환)
    h2_text = d['h2_text'].replace("{target}", target).replace("{base}", base)
    try:
        bbox2 = draw.textbbox((0, 0), h2_text, font=font_h2, spacing=d['h2_spacing'])
        w2 = bbox2[2] - bbox2[0]
        draw.text(((1080 - w2) / 2, d['h2_y']), h2_text, font=font_h2, fill=d['h2_color'], align="center", spacing=d['h2_spacing'])
    except: pass

    # === [중앙 숫자 그리드] ===
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

    # === [하단 문구 영역] ===
    bot_text = d['bot_text']
    try:
        bbox_b = draw.textbbox((0, 0), bot_text, font=font_bot, spacing=d['bot_spacing'])
        wb = bbox_b[2] - bbox_b[0]
        
        # 하단 위치(bot_y)에 그려줌
        draw.text(
            ((1080 - wb) / 2, d['bot_y']), 
            bot_text, 
            font=font_bot, 
            fill=d['bot_color'], 
            align="center", 
            spacing=d['bot_spacing']  # 여기가 핵심 (줄간격)
        )
    except: pass

    return canvas

# --- [5. 헤더 미리보기 함수] ---
def create_header_preview(d):
    preview_h = 500
    canvas = Image.new('RGB', (1080, preview_h), "#EEEEEE")
    draw = ImageDraw.Draw(canvas)
    
    # 헤더 박스
    draw.rectangle([(0, 0), (1080, d['header_height'])], fill=d['header_bg'])
    
    font_h1 = get_font(d['h1_size'])
    font_h2 = get_font(d['h2_size'])
    
    try:
        bbox1 = draw.textbbox((0, 0), d['h1_text'], font=font_h1, spacing=d['h1_spacing'])
        w1 = bbox1[2] - bbox1[0]
        draw.text(((1080 - w1) / 2, d['h1_y']), d['h1_text'], font=font_h1, fill=d['h1_color'], align="center", spacing=d['h1_spacing'])
    except: pass

    try:
        bbox2 = draw.textbbox((0, 0), d['h2_text'], font=font_h2, spacing=d['h2_spacing'])
        w2 = bbox2[2] - bbox2[0]
        draw.text(((1080 - w2) / 2, d['h2_y']), d['h2_text'], font=font_h2, fill=d['h2_color'], align="center", spacing=d['h2_spacing'])
    except: pass
    
    return canvas

# --- [6. 메타데이터 생성] ---
def generate_metadata(base, target):
    title = f"3초 안에 숫자 '{target}' 찾기 도전! ⏱️ #shorts"
    desc = f"3초안에 숫자 [{target}]를 찾으면 정답을 톡톡 두번 터치해주세요\n\n#두뇌퀴즈 #시력테스트 #shorts"
    tags = f"두뇌퀴즈, 시력테스트, 집중력, 치매예방, 숫자퀴즈, {base}, {target}, 뇌훈련, shorts"
    return title, desc, tags

# --- [7. 메인 컨트롤 패널 (UI)] ---
st.title("🎛️ 숫자 퀴즈 마스터 (HTML 기능 이식판)")

# === [사이드바 컨트롤: HTML 구조 반영] ===
with st.sidebar:
    st.header("⚙️ 디자인 제어 패널")
    
    # [1] 상단바 디자인 (HTML의 '상단 높이/글자/줄간격' 반영)
    with st.expander("1. ⬆️ 상단바 디자인", expanded=True):
        st.caption("HTML 코드의 '상단 높이 / 글자크기 / 줄간격' 기능입니다.")
        
        # 높이 조절
        header_height = st.slider("상단 높이 (Box Height)", 50, 600, 200)
        
        st.markdown("---")
        # 제목 1 (큰 글씨)
        h1_text = st.text_input("제목 1 내용", "숫자 찾기 도전")
        col1_1, col1_2 = st.columns(2)
        h1_size = col1_1.slider("글자크기 1", 30, 150, 70)
        h1_spacing = col1_2.slider("줄간격 1", 0, 100, 20)
        h1_y = st.slider("위치 Y (1)", 0, 400, 40)
        
        st.markdown("---")
        # 제목 2 (작은 글씨)
        h2_text = st.text_input("제목 2 내용", "3초 안에 숫자 '{target}' 찾기")
        col2_1, col2_2 = st.columns(2)
        h2_size = col2_1.slider("글자크기 2", 30, 150, 80)
        h2_spacing = col2_2.slider("줄간격 2", 0, 100, 20)
        h2_y = st.slider("위치 Y (2)", 0, 500, 130)
        
        st.markdown("---")
        # 색상
        col_c1, col_c2, col_c3 = st.columns(3)
        header_bg = col_c1.color_picker("배경색", "#112D4E")
        h1_color = col_c2.color_picker("제목1 색", "#FFFFFF")
        h2_color = col_c3.color_picker("제목2 색", "#FFC300")
        
        # 미리보기
        preview_design = {
            'header_height': header_height, 'header_bg': header_bg,
            'h1_text': h1_text, 'h1_size': h1_size, 'h1_spacing': h1_spacing, 'h1_y': h1_y, 'h1_color': h1_color,
            'h2_text': h2_text, 'h2_size': h2_size, 'h2_spacing': h2_spacing, 'h2_y': h2_y, 'h2_color': h2_color,
        }
        st.image(create_header_preview(preview_design), caption="상단바 실시간 미리보기", use_container_width=True)

    # [2] 하단바 디자인 (HTML의 '하단 높이/글자/줄간격' 반영)
    with st.expander("2. ⬇️ 하단바 디자인", expanded=True):
        st.caption("HTML 코드의 '하단 높이 / 글자크기 / 줄간격' 기능입니다.")
        
        bot_text = st.text_area("하단 문구 입력", "정답은 댓글에서 확인하세요!\n구독과 좋아요는 사랑입니다 ❤️")
        
        # 높이 조절 개념은 '위치 Y'로 구현됨 (파이썬에서는 캔버스 좌표계이므로)
        bot_y = st.slider("하단 위치 Y (높이 조절)", 1200, 1850, 1650, help="숫자가 클수록 아래로 내려갑니다.")
        
        col_b1, col_b2 = st.columns(2)
        bot_size = col_b1.slider("하단 글자크기", 20, 100, 50)
        bot_spacing = col_b2.slider("하단 줄간격", 0, 100, 30, help="HTML의 line-height 역할")
        
        bot_color = st.color_picker("하단 글자색", "#000000")

    # [3] 중앙 숫자판 (기존 기능 유지)
    with st.expander("3. 중앙 숫자판 설정", expanded=False):
        col_r, col_c = st.columns(2)
        rows = col_r.number_input("세로 줄 수", 5, 20, 10)
        cols = col_c.number_input("가로 줄 수", 3, 15, 6)
        
        main_size = st.slider("숫자 크기", 30, 150, 80)
        main_color = st.color_picker("숫자 색상", "#000000")
        
        st.caption("간격/위치 미세조정")
        spacing_x = st.slider("가로 간격", 50, 250, 140)
        spacing_y = st.slider("세로 간격", 50, 250, 120)
        grid_start_x = st.slider("시작점 X", 0, 500, 180)
        grid_start_y = st.slider("시작점 Y", 200, 1500, 400)
        
    bg_color = st.color_picker("전체 배경색", "#FFFFFF")

    # 디자인 딕셔너리 패킹
    design = {
        'bg_color': bg_color, 'header_height': header_height, 'header_bg': header_bg,
        'h1_text': h1_text, 'h1_size': h1_size, 'h1_spacing': h1_spacing, 'h1_y': h1_y, 'h1_color': h1_color,
        'h2_text': h2_text, 'h2_size': h2_size, 'h2_spacing': h2_spacing, 'h2_y': h2_y, 'h2_color': h2_color,
        'main_size': main_size, 'main_color': main_color,
        'spacing_x': spacing_x, 'spacing_y': spacing_y,
        'grid_start_x': grid_start_x, 'grid_start_y': grid_start_y,
        'bot_text': bot_text, 'bot_size': bot_size, 'bot_spacing': bot_spacing, 'bot_y': bot_y, 'bot_color': bot_color
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
        t, d, tags = generate_metadata(base_text, target_text)
        st.text_input("유튜브 제목", t)
        st.text_area("설명란 (대본)", d, height=150)
        st.text_area("태그", tags)