import streamlit as st
import random
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import os

# --- [1. 기본 설정] ---
st.set_page_config(page_title="숨은 글자 찾기 (100만뷰 ver)", page_icon="🔥", layout="wide")

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
    "0 vs 8 (숫자)": ("0", "8"),
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
    canvas = Image.new('RGB', (1080, 1920), design['bg_color'])
    draw = ImageDraw.Draw(canvas)
    
    font_main = get_font(design['font_size'])
    font_title = get_font(design['title_size'])
    font_bottom = get_font(design['bot_size'])
    
    # 1. 상단 헤더
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
    
    if 'answer_pos' not in st.session_state:
        st.session_state.answer_pos = (random.randint(0, rows-1), random.randint(0, cols-1))
    
    ans_r, ans_c = st.session_state.answer_pos
    
    for r in range(rows):
        for c in range(cols):
            x = start_x + (c * spacing_x)
            y = start_y + (r * spacing_y)
            
            is_target = (r == ans_r and c == ans_c)
            text = target_text if is_target else base_text
            
            draw.text((x, y), text, font=font_main, fill=design['text_color'], anchor="mm")
            
            # 정답 박스
            if show_answer and is_target:
                box_s = design['font_size'] * 0.7
                # 박스를 조금 더 두껍고 잘 보이게
                draw.rectangle([x - box_s, y - box_s, x + box_s, y + box_s], outline="#FF0000", width=12)

    # 3. 하단 문구
    bot_y = design['bot_y']
    bot_text = design['bottom_text']
    try:
        bbox_b = draw.textbbox((0, 0), bot_text, font=font_bottom)
        text_bw = bbox_b[2] - bbox_b[0]
        draw.text(((1080 - text_bw) / 2, bot_y), bot_text, font=font_bottom, fill=design['bot_color'], align="center")
    except: pass

    return canvas

# --- [5. 트래픽 폭발용 메타데이터 생성 (알고리즘 최적화)] ---
def generate_youtube_metadata(base, target):
    # 클릭률(CTR) 극대화 제목
    titles = [
        f"전세계 상위 1%만 가능! 3초 안에 {target} 찾기 👁️",
        f"※치매예방 테스트※ {base} 사이에 숨은 {target} 찾으면 뇌나이 20대?",
        f"절대 못 찾음ㅋㅋㅋ 3초 컷 가능하신 분? ({target} 찾기)",
        f"눈 좋은 사람만 보입니다. 5초 안에 {target} 찾아보세요! #shorts",
        f"몽골인 시력 테스트 🦅 {base} 속 다른 글자 찾기 (난이도 최상)"
    ]
    title = random.choice(titles)
    
    # 체류 시간 & 댓글 유도 설명
    desc = f"""당신의 뇌는 안녕하십니까? 🧠
하루 1분 두뇌 트레이닝으로 치매를 예방하세요!

3초 안에 '{target}'을 찾으셨다면?
당신은 상위 1% 눈썰미의 소유자입니다! 🦅

👇 **정답을 찾으신 분은 댓글로 '성공'이라고 남겨주세요!** 👇
(화면을 두 번 터치하면 눈이 맑아집니다 ✨)

#두뇌퀴즈 #시력테스트 #집중력 #치매예방 #틀린그림찾기 #{base} #{target} #뇌훈련
"""
    # 검색량 높은 키워드 조합
    tags = f"두뇌회전, 두뇌퀴즈, 시력테스트, 틀린그림찾기, 집중력향상, 치매예방, 숫자퀴즈, 뇌풀기, shorts, 쇼츠, {base}, {target}, 뇌훈련, 아이큐테스트, 관찰력"
    
    return title, desc, tags

# --- [6. 메인 UI] ---
st.title("🔥 숨은 글자 찾기 생성기 (100만뷰 Ver)")

with st.sidebar:
    st.header("🎨 디자인 설정")
    
    with st.expander("1. 색상 설정", expanded=False):
        bg_color = st.color_picker("배경색", "#FFFFFF")
        text_color = st.color_picker("본문 글자색", "#000000")
        header_bg = st.color_picker("헤더 배경", "#111827") # 다크 네이비 (전문적인 느낌)
        header_text = st.color_picker("헤더 글자", "#F3F4F6")
        
    with st.expander("2. 그리드 배치 (기본 10줄)", expanded=True):
        st.info("💡 10x10 배치가 가장 인기 있습니다.")
        rows = st.slider("세로 줄 수 (Rows)", 5, 20, 10) # 10줄 기본
        cols = st.slider("가로 줄 수 (Cols)", 3, 15, 10) # 10줄 기본
        font_size = st.slider("본문 글자 크기", 30, 150, 65) # 글자 크기 약간 줄임
        spacing_x = st.slider("가로 간격", 50, 200, 95) # 간격 좁힘
        spacing_y = st.slider("세로 간격", 50, 200, 100) # 간격 좁힘
        grid_x = st.slider("시작 위치 X", 10, 500, 110)
        grid_y = st.slider("시작 위치 Y", 200, 800, 350)
    
    with st.expander("3. 하단 문구 & 여백", expanded=False):
        bottom_text = st.text_area("문구 내용", "정답을 찾으셨나요?\n댓글로 알려주세요! 👇")
        bot_size = st.slider("하단 글자 크기", 30, 150, 60)
        bot_y = st.slider("하단 문구 위치 (Y좌표)", 1000, 1900, 1650)
        bot_color = st.color_picker("하단 글자 색상", "#000000")
    
    title_size = 70

    design = {
        'bg_color': bg_color, 'text_color': text_color, 
        'header_bg': header_bg, 'header_text': header_text,
        'font_size': font_size, 'title_size': title_size, 
        'bot_size': bot_size, 'bot_y': bot_y, 'bot_color': bot_color,
        'rows': rows, 'cols': cols, 'spacing_x': spacing_x, 'spacing_y': spacing_y,
        'grid_x': grid_x, 'grid_y': grid_y, 'bottom_text': bottom_text
    }

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
        st.markdown("### 🔥 유튜브 업로드 메타데이터 (100만뷰 최적화)")
        title, desc, tags = generate_youtube_metadata(base_text, target_text)
        
        st.text_input("📌 제목", value=title)
        st.text_area("📝 설명", value=desc, height=250)
        st.text_area("🏷️ 태그", value=tags, height=100)

    else:
        st.info("왼쪽에서 '퀴즈 이미지 생성' 버튼을 눌러주세요.")