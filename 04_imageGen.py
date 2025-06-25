import streamlit as st
from openai import OpenAI
import re
import requests
import time
import os
import json
import hashlib
import random
import string
from datetime import datetime, timedelta

# 페이지 설정
st.set_page_config(
    page_title="AI 이미지 생성기",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 참고 이미지와 동일한 깔끔한 UI
st.markdown("""
<style>
    /* 전체 앱 강제 라이트 모드 */
    .stApp {
        background-color: #f5f5f5 !important;
        color: #333333 !important;
    }
    
    /* 사이드바 숨김 */
    [data-testid="stSidebar"] {
        display: none !important;
    }
    
    /* 메인 컨테이너 - 참고 이미지와 동일 */
    .main .block-container {
        max-width: 800px !important;
        padding: 2rem 1.5rem !important;
        background: white !important;
        border-radius: 16px !important;
        margin: 2rem auto !important;
        box-shadow: 0 2px 10px rgba(0,0,0,0.08) !important;
        color: #333333 !important;
    }
    
    /* 헤더 - 참고 이미지와 동일한 그라데이션 */
    .main-header {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
        color: white !important;
        padding: 2.5rem 2rem !important;
        border-radius: 16px !important;
        text-align: center !important;
        margin-bottom: 2rem !important;
    }
    
    .main-header h1 {
        font-size: 2.2rem !important;
        font-weight: 600 !important;
        margin: 0 !important;
        color: white !important;
    }
    
    .main-header p {
        font-size: 1rem !important;
        margin: 0.5rem 0 0 0 !important;
        opacity: 0.9 !important;
        color: white !important;
    }
    
    /* 인증 섹션 */
    .auth-section {
        text-align: center;
        margin: 3rem 0;
        color: #333333 !important;
    }
    
    .auth-section h3 {
        font-size: 1.3rem !important;
        font-weight: 600 !important;
        margin-bottom: 0.5rem !important;
        color: #333333 !important;
    }
    
    .auth-section p {
        color: #6b7280 !important;
        margin-bottom: 2rem !important;
        font-size: 0.95rem !important;
    }
    
    /* 상태 배너 */
    .status-success {
        background: #f0fdf4 !important;
        border: 1px solid #bbf7d0 !important;
        color: #15803d !important;
        padding: 1rem 1.5rem !important;
        border-radius: 12px !important;
        margin-bottom: 2rem !important;
        font-weight: 500 !important;
    }
    
    .status-error {
        background: #fef2f2 !important;
        border: 1px solid #fecaca !important;
        color: #dc2626 !important;
        padding: 1rem 1.5rem !important;
        border-radius: 12px !important;
        margin-bottom: 2rem !important;
        font-weight: 500 !important;
    }
    
    /* 모든 텍스트 강제 색상 지정 */
    .stMarkdown, .stMarkdown p, .stMarkdown div, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4 {
        color: #333333 !important;
    }
    
    /* 섹션 헤더 */
    .section-title {
        font-size: 1.2rem !important;
        font-weight: 600 !important;
        margin: 2.5rem 0 1.5rem 0 !important;
        color: #333333 !important;
        display: flex !important;
        align-items: center !important;
        gap: 0.5rem !important;
    }
    
    /* 입력 필드 스타일 */
    .stTextInput > div > div > input {
        background: white !important;
        border: 1px solid #d1d5db !important;
        border-radius: 12px !important;
        padding: 0.75rem 1rem !important;
        font-size: 1rem !important;
        color: #333333 !important;
    }
    
    .stTextInput > div > div > input::placeholder {
        color: #9ca3af !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #6366f1 !important;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1) !important;
        outline: none !important;
    }
    
    .stTextArea > div > div > textarea {
        background: white !important;
        border: 1px solid #d1d5db !important;
        border-radius: 12px !important;
        padding: 1rem !important;
        font-size: 1rem !important;
        color: #333333 !important;
        resize: vertical !important;
    }
    
    .stTextArea > div > div > textarea::placeholder {
        color: #9ca3af !important;
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: #6366f1 !important;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1) !important;
        outline: none !important;
    }
    
    /* 버튼 스타일 - 참고 이미지와 동일 */
    .stButton > button {
        background: #6366f1 !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 500 !important;
        font-size: 1rem !important;
        transition: all 0.2s ease !important;
        width: 100% !important;
    }
    
    .stButton > button:hover {
        background: #5b51f5 !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3) !important;
    }
    
    /* 스타일 카드 그리드 */
    .style-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 0.75rem;
        margin-bottom: 2rem;
    }
    
    .style-card {
        background: white !important;
        border: 1.5px solid #e5e7eb !important;
        border-radius: 12px !important;
        padding: 1rem 0.5rem !important;
        text-align: center !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
        height: 70px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-size: 0.85rem !important;
        font-weight: 500 !important;
        color: #374151 !important;
    }
    
    .style-card:hover {
        border-color: #6366f1 !important;
        background: #f8faff !important;
        transform: translateY(-1px) !important;
    }
    
    .style-card.selected {
        border-color: #6366f1 !important;
        background: #6366f1 !important;
        color: white !important;
    }
    
    /* 슬라이더 스타일 */
    .stSlider > div > div > div > div {
        background: #6366f1 !important;
    }
    
    .stSlider > div > div > div {
        color: #333333 !important;
    }
    
    /* 이미지 수 선택 버튼 */
    .count-button {
        background: #f9fafb !important;
        border: 1.5px solid #e5e7eb !important;
        border-radius: 8px !important;
        padding: 0.5rem 1rem !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
        font-weight: 500 !important;
        color: #374151 !important;
        text-align: center !important;
    }
    
    .count-button:hover {
        border-color: #6366f1 !important;
        background: #f8faff !important;
    }
    
    .count-button.selected {
        background: #6366f1 !important;
        color: white !important;
        border-color: #6366f1 !important;
    }
    
    /* 고급 옵션 expander */
    .streamlit-expanderHeader {
        color: #6366f1 !important;
        font-weight: 500 !important;
    }
    
    /* 이미지 갤러리 */
    .image-container {
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        overflow: hidden;
        margin-bottom: 1rem;
        background: white;
    }
    
    /* 다운로드 버튼 */
    .stDownloadButton > button {
        background: #f3f4f6 !important;
        color: #374151 !important;
        border: 1px solid #d1d5db !important;
        border-radius: 8px !important;
        padding: 0.5rem 1rem !important;
        font-size: 0.9rem !important;
        width: 100% !important;
    }
    
    .stDownloadButton > button:hover {
        background: #e5e7eb !important;
    }
    
    /* 경고/성공 메시지 */
    .stSuccess, .stError, .stWarning, .stInfo {
        color: inherit !important;
    }
    
    /* 코드 블록 */
    .stCodeBlock {
        background: #f8f9fa !important;
        border: 1px solid #e9ecef !important;
        border-radius: 8px !important;
    }
    
    .stCodeBlock code {
        color: #333333 !important;
    }
    
    /* 반응형 */
    @media (max-width: 768px) {
        .main .block-container {
            margin: 1rem !important;
            padding: 1.5rem 1rem !important;
        }
        
        .style-grid {
            grid-template-columns: repeat(2, 1fr);
        }
        
        .main-header h1 {
            font-size: 1.8rem !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# API 클라이언트 초기화
@st.cache_resource
def init_openai_client():
    return OpenAI(api_key=st.secrets['openai']['API_KEY'])

client = init_openai_client()

# 보안 관련 함수들 (기존과 동일)
def get_secure_session_id():
    if 'secure_session_id' not in st.session_state:
        random_str = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        session_data = f"{random_str}_{time.time()}_{os.getpid()}"
        st.session_state.secure_session_id = hashlib.sha256(session_data.encode()).hexdigest()[:16]
    return st.session_state.secure_session_id

def get_fail_log_path():
    try:
        session_id = get_secure_session_id()
        today = datetime.now().strftime("%Y%m%d")
        return f".failcount_{session_id}_{today}.json"
    except Exception:
        today = datetime.now().strftime("%Y%m%d")
        fallback_id = hashlib.sha256(f"fallback_{time.time()}".encode()).hexdigest()[:8]
        return f".failcount_{fallback_id}_{today}.json"

def get_fail_info():
    try:
        path = get_fail_log_path()
        if os.path.exists(path):
            with open(path, "r") as f:
                data = json.load(f)
                return data.get("fail_count", 0), data.get("fail_time", 0)
    except Exception:
        pass
    return 0, 0

def set_fail_info(fail_count, fail_time):
    try:
        path = get_fail_log_path()
        with open(path, "w") as f:
            json.dump({"fail_count": fail_count, "fail_time": fail_time}, f)
    except Exception:
        pass

def check_user_access(user_code):
    if not user_code:
        return False, 0, "코드를 입력해주세요."
    
    fail_count, fail_time = get_fail_info()
    block_seconds = 30 * 60
    
    if fail_count >= 5:
        now = time.time()
        if now - fail_time < block_seconds:
            left_min = int((block_seconds - (now - fail_time)) // 60) + 1
            return False, 0, f"5회 이상 오류로 {left_min}분간 접근이 제한됩니다."
        else:
            set_fail_info(0, 0)
            fail_count = 0
    
    try:
        user_limits = st.secrets.get("user_codes", {})
        limit_value = user_limits.get(user_code, "0")
        limit = int(limit_value)
    except Exception as e:
        st.error(f"설정 파일 읽기 오류: {e}")
        return False, 0, "시스템 오류가 발생했습니다."
    
    if limit > 0 or limit == -1:
        set_fail_info(0, 0)
        return True, limit, ""
    else:
        fail_count += 1
        current_time = int(time.time()) if fail_count >= 5 else fail_time
        set_fail_info(fail_count, current_time)
        
        if fail_count >= 5:
            return False, 0, "5회 이상 오류로 30분간 접근이 제한됩니다."
        else:
            return False, 0, f"유효하지 않은 코드입니다. (실패 {fail_count}/5회)"

def generate_prompt(user_input, style):
    style_mapping = {
        "기본": "Auto, best fit",
        "없음": "no style",
        "사진 콜라주": "photo collage",
        "사진": "realistic photo",
        "사이버펑크": "cyberpunk style", 
        "사실적인": "photorealistic",
        "애니메이션": "anime style",
        "판타지 아트": "fantasy art",
        "만화": "comic book style",
        "사이버델릭": "psychedelic art",
        "아날로그": "analog photography",
        "픽토그램": "pictogram style",
        "미니멀리즘": "minimalist design",
        "아트포스터": "vintage art poster",
        "반 고흐": "Van Gogh style",
        "에드워드 호퍼": "Edward Hopper style",
        "앤디 워홀": "Andy Warhol pop art",
        "구스타프 클림트": "Gustav Klimt style",
        "무하": "Alphonse Mucha style",
        "헤이즐 블룸": "Hazel Bloom digital art"
    }
    
    full_style = style_mapping.get(style, style)
    
    gpt_prompt = f"""당신은 AI 이미지 프롬프트 엔지니어입니다.
아래는 사용자의 간단한 한글 설명입니다.
---
{user_input} {f'({full_style})' if style != '기본' else ''}
---
1. 이 내용을 바탕으로 색상, 질감, 배경, 분위기, 조명, 카메라 각도, 디테일, 동작, 감정 등 시각적 정보까지 추가해 풍성한 한글 프롬프트를 완성해줘.
2. 두 번째로, 이 한글 프롬프트를 AI가 잘 이해할 수 있는 영어 프롬프트로 자연스럽게 번역해줘. 
 - 영어 프롬프트에는 'edge-to-edge composition, no letterboxing' 같은 여백 제거 지시어를 반드시 포함해줘. 
3. 각각은 아래 양식으로, 반드시 영어 프롬프트는 코드블럭으로 출력해.
4. 그 뒤에 영어 프롬프트를 확인할 수 있도록 플레인 텍스트로 한국어 설명을 플레인텍스트로 자세히 설명해줘.
[English Prompt]
```
(여기에 풍성한 영어 프롬프트)
```
[프롬프트 설명]
1. 여기에 영문 프롬프트를 플레인 텍스트로 자세하게 설명.
2. 영문 프롬프트 한국어 전문 번역 후 프롬프트 의도 설명
"""
    
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": gpt_prompt}],
        temperature=0.6
    )
    
    ai_response = response.choices[0].message.content.strip()
    
    eng_match = re.search(r"\[English Prompt\]\s*```([\s\S]+?)```", ai_response)
    desc_match = re.search(r"\[프롬프트 설명\]\s*([\s\S]+)", ai_response)
    
    eng_prompt = eng_match.group(1).strip() if eng_match else ""
    kor_desc = desc_match.group(1).strip() if desc_match else ""
    
    summary_response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{
            "role": "user",
            "content": f"아래 한글 해설을 10자 이내로 요약해줘:\n{kor_desc}"
        }],
        temperature=0.2
    )
    summary = summary_response.choices[0].message.content.strip()
    
    return eng_prompt, kor_desc, summary

def generate_images(prompt, size, num_images):
    images = []
    for _ in range(num_images):
        try:
            response = client.images.generate(
                prompt=prompt,
                model="dall-e-3",
                n=1,
                size=size
            )
            images.append(response.data[0].url)
        except Exception as e:
            st.error(f"이미지 생성 중 오류: {e}")
            break
    return images

# 세션 상태 초기화
def init_session_state():
    defaults = {
        "all_images": [],
        "used_count": 0,
        "user_authenticated": False,
        "current_user_code": "",
        "selected_size": "1024x1024",
        "selected_style": "기본",
        "selected_num_images": 1,
        "aspect_ratio": 1.0
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

# 헤더
st.markdown("""
<div class="main-header">
    <h1>🎨 AI 이미지 생성기</h1>
    <p>텍스트를 이미지로</p>
</div>
""", unsafe_allow_html=True)

# 인증 상태 확인
if st.session_state.user_authenticated:
    is_valid, limit, error_msg = check_user_access(st.session_state.current_user_code)
    if not is_valid and "제한" not in error_msg:
        st.session_state.user_authenticated = False
        st.session_state.current_user_code = ""

if not st.session_state.user_authenticated:
    # 인증 섹션
    st.markdown("""
    <div class="auth-section">
        <h3>🔐 이용자 코드 입력</h3>
        <p>서비스 이용을 위해 코드를 입력해주세요</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        input_code = st.text_input(
            "이용자 코드",
            max_chars=16,
            type="password",
            placeholder="이용자 코드를 입력하세요",
            label_visibility="collapsed"
        )
        
        if st.button("코드 확인"):
            if input_code:
                is_valid, limit, error_msg = check_user_access(input_code)
                if is_valid:
                    st.session_state.user_authenticated = True
                    st.session_state.current_user_code = input_code
                    st.session_state.used_count = 0
                    st.experimental_rerun()
                else:
                    st.error(error_msg)
            else:
                st.warning("코드를 입력해주세요.")

else:
    # 인증된 상태
    is_valid, limit, error_msg = check_user_access(st.session_state.current_user_code)
    remaining = limit - st.session_state.used_count if limit > 0 else -1
    
    if remaining == 0 and limit > 0:
        st.markdown("""
        <div class="status-error">
            ⚠️ 사용 횟수 소진 - 새로운 코드를 입력해주세요
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("새 코드 입력"):
                st.session_state.user_authenticated = False
                st.session_state.current_user_code = ""
                st.experimental_rerun()
    else:
        # 상태 표시
        if limit == -1:
            status_text = "✅ 무제한 이용 가능"
        else:
            status_text = f"✅ 남은 횟수: {remaining}장"
            
        st.markdown(f"""
        <div class="status-success">
            {status_text}
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([4, 1, 4])
        with col2:
            if st.button("코드 변경"):
                st.session_state.user_authenticated = False
                st.session_state.current_user_code = ""
                st.experimental_rerun()

        # 메인 콘텐츠
        user_input = st.text_area(
            "원하는 이미지를 한글로 자세히 설명해주세요",
            height=100,
            placeholder="예: 석양이 지는 바다가에서 혼자 앉아있는 소녀, 따뜻한 분위기, 파스텔 톤"
        )
        
        # 스타일 선택
        st.markdown('<div class="section-title">🎨 스타일</div>', unsafe_allow_html=True)
        
        styles = [
            ["기본", "없음", "사진 콜라주", "사진"],
            ["사이버펑크", "사실적인", "애니메이션", "판타지 아트"], 
            ["만화", "사이버델릭", "아날로그", "픽토그램"],
            ["미니멀리즘", "아트포스터", "반 고흐", "에드워드 호퍼"],
            ["앤디 워홀", "구스타프 클림트", "무하", "헤이즐 블룸"]
        ]
        
        for row in styles:
            cols = st.columns(4)
            for i, (style, col) in enumerate(zip(row, cols)):
                if style:
                    if col.button(style, key=f"style_{style}"):
                        st.session_state.selected_style = style
        
        # 비율 선택
        st.markdown('<div class="section-title">📐 비율</div>', unsafe_allow_html=True)
        
        aspect_ratio = st.slider(
            "비율",
            min_value=0.5,
            max_value=2.0,
            value=1.0,
            step=0.1,
            label_visibility="collapsed"
        )
        
        if aspect_ratio < 0.8:
            selected_size = "1024x1792"
        elif aspect_ratio > 1.3:
            selected_size = "1792x1024"
        else:
            selected_size = "1024x1024"
        
        # 이미지 수 선택
        st.markdown('<div class="section-title">🔢 이미지 수</div>', unsafe_allow_html=True)
        
        col1, col2, col3, col4, col5 = st.columns([1,1,1,1,6])
        
        for i, num in enumerate([1, 2, 3, 4]):
            with [col1, col2, col3, col4][i]:
                if st.button(str(num), key=f"num_{num}"):
                    st.session_state.selected_num_images = num
        
        # 고급 옵션
        with st.expander("🔧 고급 컨트롤"):
            st.slider("지침 스케일", min_value=1, max_value=20, value=7)
            st.toggle("고정된 시드 사용")
        
        # 버튼들
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🚀 자동 전문적 프롬프트 생성"):
                if not user_input.strip():
                    st.warning("먼저 이미지 설명을 입력해주세요!")
                else:
                    with st.spinner("AI가 전문적인 프롬프트를 생성 중입니다..."):
                        eng_prompt, kor_desc, summary = generate_prompt(user_input, st.session_state.selected_style)
                        st.session_state.eng_prompt = eng_prompt
                        st.session_state.kor_desc = kor_desc
                        st.session_state.summary = summary
                        st.experimental_rerun()
        
        with col2:
            if st.button("⚡ 즉시 생성"):
                if not user_input.strip():
                    st.warning("먼저 이미지 설명을 입력해주세요!")
                elif 'eng_prompt' not in st.session_state:
                    st.warning("먼저 프롬프트를 생성해주세요!")
                elif limit > 0 and st.session_state.used_count >= limit:
                    st.error("사용 가능한 횟수를 모두 사용했습니다.")
                else:
                    with st.spinner("이미지를 생성 중입니다..."):
                        images = generate_images(st.session_state.eng_prompt, selected_size, st.session_state.selected_num_images)
                        for url in images:
                            st.session_state.all_images.append({
                                "url": url,
                                "caption": st.session_state.get("summary", "")
                            })
                        if limit > 0:
                            st.session_state.used_count += st.session_state.selected_num_images
                        st.success("✅ 이미지가 생성되었습니다!")

        # 프롬프트 표시
        if st.session_state.get('eng_prompt'):
            st.markdown('<div class="section-title">🤖 생성된 프롬프트</div>', unsafe_allow_html=True)
            
            with st.expander("📝 프롬프트 수정"):
                st.info(st.session_state.get('kor_desc', ''))
                
                kor_prompt_update = st.text_area(
                    "프롬프트 수정",
                    value=st.session_state.get('kor_desc', ''),
                    height=100
                )
                
                if st.button("🔄 프롬프트 재생성"):
                    with st.spinner("재생성 중..."):
                        gpt_re_prompt = f"""아래 한글 프롬프트를 영어로 번역해줘.
```
{kor_prompt_update}
```"""
                        
                        response = client.chat.completions.create(
                            model="gpt-4.1-mini",
                            messages=[{"role": "user", "content": gpt_re_prompt}],
                            temperature=0.6
                        )
                        
                        re_eng_match = re.search(r"```([\s\S]+?)```", response.choices[0].message.content)
                        if re_eng_match:
                            st.session_state.eng_prompt = re_eng_match.group(1).strip()
                        st.session_state.kor_desc = kor_prompt_update
                        st.experimental_rerun()

        # 생성된 이미지 갤러리
        if st.session_state.all_images:
            st.markdown('<div class="section-title">🖼️ 생성된 이미지</div>', unsafe_allow_html=True)
            
            images = st.session_state.all_images
            n_images = len(images)
            
            # 이미지 그리드
            cols_per_row = min(3, n_images)
            for i in range(0, n_images, cols_per_row):
                row_cols = st.columns(cols_per_row)
                
                for j, col in enumerate(row_cols):
                    idx = i + j
                    if idx < n_images:
                        img = images[idx]
                        
                        with col:
                            st.image(
                                img["url"],
                                caption=f"이미지 {idx+1}: {img['caption']}",
                                use_container_width=True
                            )
                            
                            try:
                                img_data = requests.get(img["url"]).content
                                st.download_button(
                                    label=f"📥 다운로드",
                                    data=img_data,
                                    file_name=f"ai_image_{idx+1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                                    mime="image/png",
                                    key=f"download_{idx}",
                                    use_container_width=True
                                )
                            except Exception as e:
                                st.error(f"다운로드 준비 중 오류: {e}")
            
            # 이미지 삭제 버튼
            st.markdown("---")
            col1, col2, col3 = st.columns([2, 1, 2])
            with col2:
                if st.button("🗑️ 모든 이미지 삭제", type="secondary"):
                    st.session_state.all_images = []
                    st.experimental_rerun()

# 푸터
st.markdown("---")
st.markdown("""
<div style='text-align: center; padding: 1rem; color: #6b7280; font-size: 0.9rem;'>
    © AI 이미지 생성기 by FAITH | Powered by OpenAI DALL-E 3
</div>
""", unsafe_allow_html=True)
