import streamlit as st
import random
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import os

# --- [1. 기본 설정] ---
st.set_page_config(page_title="숨은 글자 찾기 (여백조절)", page_icon="👀", layout="wide")

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

# --- [3. 추천 문제 세트] ---
PRESET_PAIRS = {
    "직접 입력": ("A", "B"),
    "98 vs 89 (숫자)": ("98", "89"),
    "5 vs 2 (숫자)": ("5", "2"),
    "6 vs 9 (숫자)": ("6", "9"),
    "3 vs 8 (숫자)": ("3", "8"),
    "1 vs 7 (숫자)": ("1", "7"),
    "O vs Q (영어)": ("O", "Q"),
    "F vs E (영어)": ("F", "E"),
    "R vs P (영어)": ("R", "P"),
    "나 vs 너 (한글)": ("나", "너"),
    "김 vs 금 (한글)": ("김", "금")
}

# --- [4. 이미지 생성 함수] ---
def get_font(size):
    if os.path.exists(FONT_FILE):
        return ImageFont.truetype(FONT_FILE, size)
    else:
        return ImageFont.load_default()

def create_puzzle_image(base_text, target_text, rows, cols, design, show_answer=False):
    # 캔버스 생성
    canvas = Image.new('RGB', (1080, 1920), design['bg_color'])
    draw = ImageDraw.Draw(canvas)
    
    # 폰트 로드
    font_main = get_font(design['font_size'])
    font_title = get_font(design['title_size'])
    font_bottom = get_font(design['bot_size'])
    
    # 1. 상단 제목 (헤더 바 포함)
    header_h = 250
    draw.rectangle([(0, 0), (1080, header_h)], fill=design['header_bg'])
    
    title_text = f"3초 안에 숫자 '{target_text}' 찾기"
    try:
        bbox = draw.textbbox((0, 0), title_text, font=font_title)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        draw.text(((1080 - text_w) / 2, (header_h - text_h) / 2 - 20), title_text, font=font_title, fill=design['header_text'])
    except: pass

    # 2. 그리드 배치
    start_x = design['grid_x']
    start_y = design['grid_y']
    spacing_x = design['spacing_x']
    spacing_y = design['spacing_y']
    
    # 정답 위치 랜덤 선정 (session_state에 없으면 새로 생성)
    if 'answer_pos' not in st.session_state:
        st.session_state.answer_pos = (random.randint(0, rows-1), random.randint(0, cols-1))
    
    ans_r, ans_c = st.session_state.answer_pos
    
    for r in range(rows):
        for c in range(cols):
            x = start_x + (c * spacing_x)
            y = start_y + (r * spacing_y)
            
            # 정답 위치면 타겟 텍스트, 아니면 베이스 텍스트
            is_target = (r == ans_r and c == ans_c)
            text = target_text if is_target else base_text
            color = design['text_color']
            
            # 텍스트 그리기
            draw.text((x, y), text, font=font_main, fill=color, anchor="mm")
            
            # 정답 공개 모드일 때 빨간 박스 표시
            if show_answer and is_target:
                # 박스 크기 계산 (글자 크기 기반)
                box_s = design['font_size'] * 0.8
                draw.rectangle([x - box_s, y - box_s, x + box_s, y + box_s], outline="#FF0000", width=10)

    # 3. 하단 문구 (위치 및 여백 조절 기능 적용)
    bot_y = design['bot_y'] # 사용자 지정 Y좌표
    bot_text = design['bottom_text']
    try:
        bbox_b = draw.textbbox((0, 0), bot_text, font=font_bottom)
        text_bw = bbox_b[2] - bbox_b[0]
        # 중앙 정렬하여 그리기
        draw.text(((1080 - text_bw) / 2, bot_y), bot_text, font=font_bottom, fill=design['bot_color'], align="center")
    except: pass

    return canvas

# --- [5. 유튜브 메타데이터 생성] ---
def generate_youtube_metadata(base, target):
    titles = [
        f"뇌지컬 테스트! 3초 안에 {target} 찾으면 천재? 🧠",
        f"99%가 틀리는 문제! {base} 사이에 숨은 {target} 찾기",
        f"눈 좋은 사람만 보입니다. {target} 찾기 도전! #shorts",
        f"치매 예방 퀴즈! {target} 찾으면 뇌 나이 20대",
        f"집중력 테스트 🧐 3초 안에 다른 글자를 찾아보세요!"
    ]
    title = random.choice(titles)
    
    desc = f"""집중력 최고수만 통과한다는 그 문제!
3초 안에 '{target}'을 찾아보세요! 👀

👇 정답을 찾으셨다면 댓글로 '찾았다' 라고 남겨주세요! 👇
(화면을 두 번 터치하면 눈이 맑아집니다 ✨)

#두뇌퀴즈 #시력테스트 #집중력 #치매예방 #틀린그림찾기 #{base} #{target}
"""
    tags = f"두뇌회전, 두뇌퀴즈, 시력테스트, 틀린그림찾기, 집중력향상, 치매예방, 숫자퀴즈, 뇌풀기, shorts, 쇼츠, {base}, {target}"
    
    return title, desc, tags

# --- [6. 메인 UI] ---
st.title("👀 숨은 글자 찾기 생성기 (v2.0)")

# 사이드바 설정
with st.sidebar:
    st.header("🎨 디자인 설정")
    
    with st.expander("1. 색상 설정", expanded=False):
        bg_color = st.color_picker("배경색", "#FFFFFF")
        text_color = st.color_picker("본문 글자색", "#000000")
        header_bg = st.color_picker("헤더 배경", "#1E3A8A")
        header_text = st.color_picker("헤더 글자", "#FFFFFF")
        
    with st.expander("2. 그리드(본문) 배치", expanded=False):
        rows = st.slider("세로 줄 수 (Rows)", 5, 15, 10)
        cols = st.slider("가로 줄 수 (Cols)", 3, 10, 6)
        font_size = st.slider("본문 글자 크기", 30, 150, 80)
        spacing_x = st.slider("가로 간격", 50, 200, 140)
        spacing_y = st.slider("세로 간격", 50, 200, 120)
        grid_x = st.slider("시작 위치 X", 50, 500, 180)
        grid_y = st.slider("시작 위치 Y", 200, 800, 400)
    
    # [NEW] 하단 문구 및 여백 설정
    with st.expander("3. 하단 문구 & 여백 (New)", expanded=True):
        st.info("여기서 하단 글자의 위치와 크기를 조절하세요.")
        bottom_text = st.text_area("문구 내용", "정답은 댓글에서 확인하세요!\n구독과 좋아요는 사랑입니다 ❤️")
        bot_size = st.slider("하단 글자 크기", 30, 150, 60)
        bot_y = st.slider("하단 문구 위치 (Y좌표)", 1000, 1900, 1600, help="숫자가 클수록 아래로 내려갑니다.")
        bot_color = st.color_picker("하단 글자 색상", "#000000")
    
    title_size = 70

    design = {
        'bg_color': bg_color, 'text_color': text_color, 
        'header_bg': header_bg, 'header_text': header_text,
        'font_size': font_size, 'title_size': title_size, 
        'bot_size': bot_size, 'bot_y': bot_y, 'bot_color': bot_color, # New variables
        'rows': rows, 'cols': cols, 'spacing_x': spacing_x, 'spacing_y': spacing_y,
        'grid_x': grid_x, 'grid_y': grid_y, 'bottom_text': bottom_text
    }

# 메인 화면
c1, c2 = st.columns([1, 1.5])

with c1:
    st.subheader("1. 문제 설정")
    pair_key = st.selectbox("추천 문제 세트", list(PRESET_PAIRS.keys()))
    
    if pair_key == "직접 입력":
        col_inp1, col_inp2 = st.columns(2)
        base_text = col_inp1.text_input("바탕 글자 (많은 거)", "98")
        target_text = col_inp2.text_input("찾을 글자 (하나)", "89")
    else:
        base_text, target_text = PRESET_PAIRS[pair_key]
        st.info(f"선택: '{base_text}' 중에서 '{target_text}' 찾기")

    if st.button("🚀 퀴즈 이미지 생성", type="primary"):
        # 정답 위치 리셋 (새로운 랜덤 위치)
        st.session_state.answer_pos = (random.randint(0, rows-1), random.randint(0, cols-1))
        st.session_state.generated = True
        st.rerun()

with c2:
    if st.session_state.get('generated', False):
        st.subheader("2. 결과물 확인")
        
        tab_q, tab_a = st.tabs(["❓ 문제 이미지 (영상용)", "✅ 정답 이미지 (썸네일용)"])
        
        # 문제 이미지 생성
        img_q = create_puzzle_image(base_text, target_text, rows, cols, design, show_answer=False)
        # 정답 이미지 생성
        img_a = create_puzzle_image(base_text, target_text, rows, cols, design, show_answer=True)
        
        with tab_q:
            st.image(img_q, caption="문제 화면", use_container_width=True)
            buf_q = BytesIO()
            img_q.save(buf_q, format="JPEG", quality=100)
            st.download_button("💾 문제 이미지 다운로드", buf_q.getvalue(), "quiz_question.jpg", "image/jpeg", use_container_width=True)
            
        with tab_a:
            st.image(img_a, caption="정답 화면 (빨간 박스)", use_container_width=True)
            buf_a = BytesIO()
            img_a.save(buf_a, format="JPEG", quality=100)
            st.download_button("💾 정답 이미지 다운로드", buf_a.getvalue(), "quiz_answer.jpg", "image/jpeg", use_container_width=True)

        st.divider()
        st.markdown("### 🔥 유튜브 업로드 메타데이터")
        title, desc, tags = generate_youtube_metadata(base_text, target_text)
        
        st.text_input("📌 제목", value=title)
        st.text_area("📝 설명", value=desc, height=200)
        st.text_area("🏷️ 태그", value=tags, height=100)

    else:
        st.info("왼쪽에서 '퀴즈 이미지 생성' 버튼을 눌러주세요.")