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

# 세련된 UI CSS
st.markdown("""
<style>
    /* 전체 앱 스타일 초기화 */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* 사이드바 완전 숨김 */
    [data-testid="stSidebar"] {
        display: none !important;
    }
    
    /* 메인 컨테이너 */
    .main .block-container {
        max-width: 1400px;
        padding: 2rem;
        background: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        margin: 2rem auto;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(10px);
    }
    
    /* 헤더 스타일 */
    .main-header {
        text-align: center;
        margin-bottom: 3rem;
        padding: 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        color: white;
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        animation: shimmer 3s ease-in-out infinite;
    }
    
    @keyframes shimmer {
        0%, 100% { transform: translate(-50%, -50%) rotate(0deg); }
        50% { transform: translate(-50%, -50%) rotate(180deg); }
    }
    
    .main-header h1 {
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 1rem;
        text-shadow: 0 4px 15px rgba(0,0,0,0.3);
        position: relative;
        z-index: 1;
    }
    
    .main-header p {
        font-size: 1.3rem;
        opacity: 0.9;
        position: relative;
        z-index: 1;
    }
    
    /* 인증 카드 */
    .auth-card {
        background: white;
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        margin-bottom: 2rem;
        border: 1px solid rgba(102, 126, 234, 0.2);
    }
    
    /* 상태 표시 카드 */
    .status-card {
        background: linear-gradient(135deg, #e8f5e8 0%, #f0f8f0 100%);
        padding: 1.5rem 2rem;
        border-radius: 15px;
        border-left: 5px solid #28a745;
        margin-bottom: 2rem;
        box-shadow: 0 5px 15px rgba(40, 167, 69, 0.2);
    }
    
    .status-card.unlimited {
        background: linear-gradient(135deg, #fff3cd 0%, #fefefe 100%);
        border-left-color: #ffc107;
        box-shadow: 0 5px 15px rgba(255, 193, 7, 0.2);
    }
    
    .status-card.expired {
        background: linear-gradient(135deg, #f8d7da 0%, #fefefe 100%);
        border-left-color: #dc3545;
        box-shadow: 0 5px 15px rgba(220, 53, 69, 0.2);
    }
    
    /* 섹션 카드 */
    .section-card {
        background: white;
        padding: 2.5rem;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
        margin-bottom: 2rem;
        border: 1px solid rgba(0, 0, 0, 0.05);
    }
    
    .section-title {
        font-size: 1.5rem;
        font-weight: 600;
        margin-bottom: 1.5rem;
        color: #2c3e50;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* 옵션 그리드 */
    .option-grid {
        display: grid;
        gap: 1rem;
        margin-bottom: 2rem;
    }
    
    .size-grid {
        grid-template-columns: repeat(3, 1fr);
    }
    
    .style-category-grid {
        grid-template-columns: repeat(4, 1fr);
        margin-bottom: 1rem;
    }
    
    .style-grid {
        grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
    }
    
    .count-grid {
        grid-template-columns: repeat(4, 1fr);
        max-width: 400px;
    }
    
    /* 옵션 버튼 */
    .option-btn {
        background: #f8f9fa;
        border: 2px solid #e9ecef;
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s ease;
        font-weight: 500;
        color: #495057;
        position: relative;
        overflow: hidden;
    }
    
    .option-btn:hover {
        border-color: #667eea;
        background: #f8f9ff;
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.2);
    }
    
    .option-btn.selected {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-color: #667eea;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
    }
    
    .option-btn.selected::after {
        content: '✓';
        position: absolute;
        top: 8px;
        right: 8px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    
    /* 스타일 카드 특별 디자인 */
    .style-card {
        background: white;
        border: 2px solid #e9ecef;
        border-radius: 15px;
        padding: 1.2rem;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s ease;
        height: 80px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 500;
        color: #495057;
        position: relative;
        overflow: hidden;
    }
    
    .style-card:hover {
        border-color: #667eea;
        background: #f8f9ff;
        transform: translateY(-3px);
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.15);
    }
    
    .style-card.selected {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-color: #667eea;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
    }
    
    /* 버튼 스타일 */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.8rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
    }
    
    /* 입력 필드 스타일 */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        border-radius: 12px;
        border: 2px solid #e9ecef;
        padding: 1rem;
        font-size: 1rem;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* 프롬프트 표시 */
    .prompt-display {
        background: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 4px solid #667eea;
    }
    
    /* 이미지 갤러리 */
    .image-gallery {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 2rem;
        margin-top: 2rem;
    }
    
    .image-card {
        background: white;
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s ease;
    }
    
    .image-card:hover {
        transform: translateY(-5px);
    }
    
    /* 선택 상태 표시 */
    .selection-info {
        background: linear-gradient(135deg, #e3f2fd 0%, #f1f8ff 100%);
        padding: 1rem 1.5rem;
        border-radius: 10px;
        margin-top: 1rem;
        border-left: 4px solid #2196f3;
        font-weight: 500;
        color: #1565c0;
    }
    
    /* 반응형 디자인 */
    @media (max-width: 768px) {
        .main .block-container {
            padding: 1rem;
            margin: 1rem;
        }
        
        .main-header h1 {
            font-size: 2rem;
        }
        
        .size-grid,
        .style-category-grid {
            grid-template-columns: repeat(2, 1fr);
        }
        
        .count-grid {
            grid-template-columns: repeat(2, 1fr);
        }
    }
</style>
""", unsafe_allow_html=True)

# API 클라이언트 초기화
@st.cache_resource
def init_openai_client():
    return OpenAI(api_key=st.secrets['openai']['API_KEY'])

client = init_openai_client()

# 보안 강화된 세션 관리
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
        "자동": "Auto, best fit",
        "사진": "Real photo",
        "디즈니": "Disney style cartoon",
        "픽사": "Pixar 3D animation",
        "드림웍스": "Dreamworks style",
        "일본애니": "Japanese anime",
        "수채화": "Watercolor painting",
        "유화": "Oil painting",
        "연필드로잉": "Pencil sketch",
        "픽토그램": "Flat pictogram icon",
        "미니멀": "Minimalist flat design",
        "반고흐": "Vincent van Gogh style",
        "호퍼": "Edward Hopper style",
        "워홀": "Andy Warhol pop art",
        "클림트": "Gustav Klimt style",
        "무하": "Alphonse Mucha Art Nouveau"
    }
    
    full_style = style_mapping.get(style, style)
    
    gpt_prompt = f"""당신은 AI 이미지 프롬프트 엔지니어입니다.
아래는 사용자의 간단한 한글 설명입니다.
---
{user_input} {f'({full_style})' if style != '자동' else ''}
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
    if "all_images" not in st.session_state:
        st.session_state.all_images = []
    if "used_count" not in st.session_state:
        st.session_state.used_count = 0
    if "user_authenticated" not in st.session_state:
        st.session_state.user_authenticated = False
    if "current_user_code" not in st.session_state:
        st.session_state.current_user_code = ""
    if "selected_size" not in st.session_state:
        st.session_state.selected_size = "1024x1024"
    if "selected_style_category" not in st.session_state:
        st.session_state.selected_style_category = "기본"
    if "selected_style" not in st.session_state:
        st.session_state.selected_style = "자동"
    if "selected_num_images" not in st.session_state:
        st.session_state.selected_num_images = 1

init_session_state()

# 헤더
st.markdown("""
<div class="main-header">
    <h1>🎨 AI 이미지 생성기</h1>
    <p>한글로 원하는 그림을 설명하면 AI가 전문적인 프롬프트를 만들고 아름다운 이미지를 생성합니다</p>
</div>
""", unsafe_allow_html=True)

# 현재 인증 상태 확인
if st.session_state.user_authenticated:
    is_valid, limit, error_msg = check_user_access(st.session_state.current_user_code)
    if not is_valid and "제한" not in error_msg:
        st.session_state.user_authenticated = False
        st.session_state.current_user_code = ""

if not st.session_state.user_authenticated:
    # 인증 카드
    st.markdown("""
    <div class="auth-card">
        <div class="section-title">🔐 이용자 인증</div>
        <p style="margin-bottom: 2rem; color: #6c757d;">서비스 이용을 위해 제공받은 이용자 코드를 입력해주세요</p>
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
        
        if st.button("🔓 코드 확인", use_container_width=True):
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
        <div class="status-card expired">
            <h3>⚠️ 사용 횟수 소진</h3>
            <p>모든 이미지 생성 횟수를 사용하셨습니다. 새로운 코드를 입력해주세요.</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("🔄 새 코드 입력", use_container_width=True):
                st.session_state.user_authenticated = False
                st.session_state.current_user_code = ""
                st.experimental_rerun()
    else:
        # 상태 표시
        if limit == -1:
            st.markdown("""
            <div class="status-card unlimited">
                <h3>✨ 무제한 이용 가능</h3>
                <p>무제한 코드로 이미지를 자유롭게 생성하세요!</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="status-card">
                <h3>✅ 남은 이미지 생성 횟수: {remaining}장</h3>
                <p>현재 {st.session_state.used_count}장 사용 / 총 {limit}장 가능</p>
            </div>
            """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([4, 1, 4])
        with col2:
            if st.button("🔄 코드 변경", use_container_width=True):
                st.session_state.user_authenticated = False
                st.session_state.current_user_code = ""
                st.experimental_rerun()

        # 메인 콘텐츠
        st.markdown("""
        <div class="section-card">
            <div class="section-title">📝 이미지 설명 입력</div>
        </div>
        """, unsafe_allow_html=True)
        
        user_input = st.text_area(
            "원하는 이미지를 한글로 자세히 설명해주세요",
            height=120,
            placeholder="예: 석양이 지는 바다가에서 혼자 앉아있는 소녀, 따뜻한 분위기, 파스텔 톤"
        )
        
        # 생성 옵션
        st.markdown("""
        <div class="section-card">
            <div class="section-title">⚙️ 생성 옵션</div>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🖼️ 이미지 크기/비율")
            
            size_options = [
                ("1:1 정사각형", "1024x1024"),
                ("세로형", "1024x1792"),
                ("가로형", "1792x1024")
            ]
            
            size_cols = st.columns(3)
            for i, ((label, value), col) in enumerate(zip(size_options, size_cols)):
                if col.button(
                    label, 
                    key=f"size_{i}",
                    use_container_width=True
                ):
                    st.session_state.selected_size = value
            
            st.markdown(f"""
            <div class="selection-info">
                📐 선택됨: {[label for label, value in size_options if value == st.session_state.selected_size][0]}
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("#### 🎨 스타일/화풍")
            
            style_categories = {
                "기본": ["자동", "사진"],
                "애니메이션": ["디즈니", "픽사", "드림웍스", "일본애니"],
                "예술": ["수채화", "유화", "연필드로잉", "픽토그램", "미니멀"],
                "명화": ["반고흐", "호퍼", "워홀", "클림트", "무하"]
            }
            
            # 카테고리 선택
            cat_cols = st.columns(4)
            for i, (category, col) in enumerate(zip(style_categories.keys(), cat_cols)):
                if col.button(
                    category, 
                    key=f"cat_{i}",
                    use_container_width=True
                ):
                    st.session_state.selected_style_category = category
                    st.session_state.selected_style = style_categories[category][0]
            
            # 선택된 카테고리의 스타일들
            styles_in_category = style_categories[st.session_state.selected_style_category]
            
            if len(styles_in_category) <= 4:
                style_cols = st.columns(len(styles_in_category))
            else:
                style_cols = st.columns(4)
                # 두 번째 줄이 필요한 경우
                if len(styles_in_category) > 4:
                    style_cols2 = st.columns(len(styles_in_category) - 4)
            
            for i, style in enumerate(styles_in_category):
                if i < 4:
                    col = style_cols[i]
                else:
                    col = style_cols2[i-4]
                    
                if col.button(
                    style, 
                    key=f"style_{i}",
                    use_container_width=True
                ):
                    st.session_state.selected_style = style
            
            st.markdown(f"""
            <div class="selection-info">
                🎭 선택됨: {st.session_state.selected_style}
            </div>
            """, unsafe_allow_html=True)
        
        # 버튼 섹션
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🚀 자동 전문적 프롬프트 생성", use_container_width=True):
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
            if st.button("⚡ 즉시 생성 (1장)", use_container_width=True):
                if not user_input.strip():
                    st.warning("먼저 이미지 설명을 입력해주세요!")
                elif 'eng_prompt' not in st.session_state:
                    st.warning("먼저 프롬프트를 생성해주세요!")
                elif limit > 0 and st.session_state.used_count >= limit:
                    st.error("사용 가능한 횟수를 모두 사용했습니다.")
                else:
                    with st.spinner("이미지를 생성 중입니다..."):
                        images = generate_images(st.session_state.eng_prompt, st.session_state.selected_size, 1)
                        if images:
                            st.session_state.all_images.append({
                                "url": images[0],
                                "caption": st.session_state.get("summary", "")
                            })
                            if limit > 0:
                                st.session_state.used_count += 1
                            st.success("✅ 이미지가 생성되었습니다!")
        
        # 프롬프트 표시
        if st.session_state.get('eng_prompt'):
            st.markdown("""
            <div class="section-card">
                <div class="section-title">🤖 생성된 프롬프트</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("**🔤 영어 프롬프트:**")
            st.code(st.session_state.eng_prompt, language='text')
            
            with st.expander("📝 프롬프트 수정 및 설명", expanded=False):
                st.markdown("**📖 프롬프트 해석:**")
                st.info(st.session_state.get('kor_desc', ''))
                
                kor_prompt_update = st.text_area(
                    "프롬프트를 수정하거나 추가 요청사항을 입력하세요",
                    value=st.session_state.get('kor_desc', ''),
                    height=100,
                    key="prompt_update"
                )
                
                if st.button("🔄 프롬프트 재생성"):
                    with st.spinner("프롬프트를 재생성 중입니다..."):
                        gpt_re_prompt = f"""아래 한글 프롬프트를 더 디테일하게 보완해 AI가 잘 이해할 수 있는 영어 프롬프트로 자연스럽게 번역해줘.
색감, 분위기, 질감, 동작, 감정, 세부 연출 등 시각적 디테일을 추가하고,
선택한 스타일 레퍼런스도 자연스럽게 포함해줘.
반드시 코드블럭으로 출력해.
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
            
            # 이미지 생성 옵션
            st.markdown("""
            <div class="section-card">
                <div class="section-title">🎨 이미지 생성</div>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.markdown("#### 📊 생성할 이미지 수")
                
                num_cols = st.columns(4)
                for i, num in enumerate([1, 2, 3, 4]):
                    if num_cols[i].button(
                        f"{num}장", 
                        key=f"num_{i}",
                        use_container_width=True
                    ):
                        st.session_state.selected_num_images = num
                
                st.markdown(f"""
                <div class="selection-info">
                    🔢 선택됨: {st.session_state.selected_num_images}장
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("#### ")  # 빈 공간
                st.markdown("#### ")  # 빈 공간
                if st.button("🎨 이미지 생성 시작!", use_container_width=True):
                    current_limit = limit if limit > 0 else float('inf')
                    if st.session_state.used_count + st.session_state.selected_num_images > current_limit:
                        st.error(f"생성 가능 횟수를 초과합니다. (현재: {st.session_state.used_count}/{limit if limit > 0 else '무제한'})")
                    else:
                        with st.spinner(f"🎨 {st.session_state.selected_num_images}장의 이미지를 생성 중입니다..."):
                            images = generate_images(
                                st.session_state.eng_prompt, 
                                st.session_state.selected_size, 
                                st.session_state.selected_num_images
                            )
                            
                            for url in images:
                                st.session_state.all_images.append({
                                    "url": url,
                                    "caption": st.session_state.summary
                                })
                            
                            if limit > 0:
                                st.session_state.used_count += st.session_state.selected_num_images
                            
                            st.success(f"✅ {len(images)}장의 이미지가 생성되었습니다!")
                            
                            if limit > 0 and st.session_state.used_count >= limit:
                                st.info("ℹ️ 모든 이미지 생성 횟수를 사용하셨습니다.")
                                time.sleep(2)
                                st.experimental_rerun()

        # 생성된 이미지 갤러리
        if st.session_state.all_images:
            st.markdown("""
            <div class="section-card">
                <div class="section-title">🖼️ 생성된 이미지 갤러리</div>
            </div>
            """, unsafe_allow_html=True)
            
            images = st.session_state.all_images
            n_images = len(images)
            
            # 반응형 그리드 레이아웃
            if n_images == 1:
                cols = 1
            elif n_images <= 2:
                cols = 2
            elif n_images <= 4:
                cols = 2
            else:
                cols = 3
            
            # 이미지 표시
            for i in range(0, n_images, cols):
                row_cols = st.columns(cols)
                
                for j, col in enumerate(row_cols):
                    idx = i + j
                    if idx < n_images:
                        img = images[idx]
                        
                        with col:
                            # 이미지 카드
                            st.markdown(f"""
                            <div class="image-card">
                            """, unsafe_allow_html=True)
                            
                            st.image(
                                img["url"],
                                caption=f"🎨 이미지 {idx+1}: {img['caption']}",
                                use_container_width=True
                            )
                            
                            # 다운로드 버튼
                            try:
                                img_data = requests.get(img["url"]).content
                                st.download_button(
                                    label=f"📥 이미지 {idx+1} 다운로드",
                                    data=img_data,
                                    file_name=f"ai_image_{idx+1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                                    mime="image/png",
                                    key=f"download_{idx}",
                                    use_container_width=True
                                )
                            except Exception as e:
                                st.error(f"다운로드 준비 중 오류: {e}")
                            
                            st.markdown("</div>", unsafe_allow_html=True)
            
            # 갤러리 관리 버튼
            st.markdown("---")
            col1, col2, col3 = st.columns([2, 1, 2])
            with col2:
                if st.button("🗑️ 모든 이미지 삭제", type="secondary", use_container_width=True):
                    st.session_state.all_images = []
                    st.experimental_rerun()

# 푸터
st.markdown("---")
st.markdown("""
<div style='text-align: center; padding: 2rem; color: #6c757d; background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); border-radius: 15px; margin-top: 2rem;'>
    <h4 style='margin-bottom: 1rem; color: #495057;'>✨ AI 이미지 생성기 by FAITH ✨</h4>
    <p style='margin: 0; font-size: 0.9rem;'>Powered by OpenAI DALL-E 3 | 최고의 AI 이미지 생성 경험을 제공합니다</p>
</div>
""", unsafe_allow_html=True)
