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

# UI 스타일 - 참고 이미지와 동일하게
st.markdown("""
<style>
    /* 전체 앱 스타일 */
    .stApp {
        background: #f5f5f5;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    
    /* 사이드바 숨김 */
    [data-testid="stSidebar"] {
        display: none !important;
    }
    
    /* 메인 컨테이너 */
    .main .block-container {
        max-width: 900px;
        padding: 2rem 1rem;
        background: white;
        border-radius: 12px;
        margin: 2rem auto;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }
    
    /* 헤더 */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .main-header h1 {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
    }
    
    .main-header p {
        font-size: 1.1rem;
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
    }
    
    /* 상태 표시 */
    .status-banner {
        background: #e8f5e8;
        border: 1px solid #c3e6c3;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 2rem;
        color: #2d5a2d;
        font-weight: 500;
    }
    
    .auth-input {
        background: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 8px;
        padding: 1.5rem;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    /* 섹션 스타일 */
    .section-header {
        font-size: 1.3rem;
        font-weight: 600;
        margin: 2rem 0 1rem 0;
        color: #333;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* 스타일 그리드 */
    .style-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 0.8rem;
        margin-bottom: 2rem;
    }
    
    .style-card {
        background: white;
        border: 2px solid #e9ecef;
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
        cursor: pointer;
        transition: all 0.2s ease;
        height: 80px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.9rem;
        font-weight: 500;
        color: #555;
    }
    
    .style-card:hover {
        border-color: #667eea;
        background: #f8f9ff;
    }
    
    .style-card.selected {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-color: #667eea;
    }
    
    /* 비율 선택 */
    .ratio-selector {
        display: flex;
        gap: 0.5rem;
        margin-bottom: 1rem;
    }
    
    .ratio-btn {
        flex: 1;
        background: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 0.8rem;
        text-align: center;
        cursor: pointer;
        transition: all 0.2s ease;
        font-size: 0.9rem;
        font-weight: 500;
    }
    
    .ratio-btn:hover {
        background: #e9ecef;
    }
    
    .ratio-btn.selected {
        background: #667eea;
        color: white;
        border-color: #667eea;
    }
    
    /* 슬라이더 스타일 */
    .aspect-slider {
        margin: 1rem 0;
    }
    
    .stSlider > div > div > div > div {
        background: #667eea;
    }
    
    /* 이미지 수 선택 */
    .count-pills {
        display: flex;
        gap: 0.5rem;
        margin-bottom: 2rem;
    }
    
    .count-pill {
        background: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 20px;
        padding: 0.5rem 1rem;
        cursor: pointer;
        transition: all 0.2s ease;
        font-weight: 500;
        min-width: 50px;
        text-align: center;
    }
    
    .count-pill.selected {
        background: #667eea;
        color: white;
        border-color: #667eea;
    }
    
    /* 버튼 스타일 */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.8rem 2rem;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    
    /* 텍스트 입력 */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        border-radius: 8px;
        border: 1px solid #dee2e6;
        padding: 0.8rem;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
    }
    
    /* 고급 옵션 토글 */
    .advanced-toggle {
        color: #667eea;
        cursor: pointer;
        font-weight: 500;
        margin: 1rem 0;
    }
    
    /* 이미지 갤러리 */
    .image-gallery {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 1.5rem;
        margin-top: 2rem;
    }
    
    .image-item {
        background: white;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        transition: transform 0.2s ease;
    }
    
    .image-item:hover {
        transform: translateY(-2px);
    }
</style>
""", unsafe_allow_html=True)

# API 클라이언트 초기화
@st.cache_resource
def init_openai_client():
    return OpenAI(api_key=st.secrets['openai']['API_KEY'])

client = init_openai_client()

# 보안 강화된 세션 관리 (기존과 동일)
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
    if "selected_style" not in st.session_state:
        st.session_state.selected_style = "기본"
    if "selected_num_images" not in st.session_state:
        st.session_state.selected_num_images = 1
    if "aspect_ratio" not in st.session_state:
        st.session_state.aspect_ratio = 1.0

init_session_state()

# 헤더
st.markdown("""
<div class="main-header">
    <h1>🎨 AI 이미지 생성기</h1>
    <p>텍스트를 이미지로</p>
</div>
""", unsafe_allow_html=True)

# 현재 인증 상태 확인
if st.session_state.user_authenticated:
    is_valid, limit, error_msg = check_user_access(st.session_state.current_user_code)
    if not is_valid and "제한" not in error_msg:
        st.session_state.user_authenticated = False
        st.session_state.current_user_code = ""

if not st.session_state.user_authenticated:
    # 인증 입력
    st.markdown("""
    <div class="auth-input">
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
        
        if st.button("코드 확인", use_container_width=True):
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
        <div class="status-banner" style="background: #f8d7da; border-color: #f5c6cb; color: #721c24;">
            ⚠️ 사용 횟수 소진 - 새로운 코드를 입력해주세요
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("새 코드 입력", use_container_width=True):
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
        <div class="status-banner">
            {status_text}
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([4, 1, 4])
        with col2:
            if st.button("코드 변경", use_container_width=True):
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
        st.markdown('<div class="section-header">🎨 스타일</div>', unsafe_allow_html=True)
        
        # 스타일 그리드 (참고 이미지와 동일하게)
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
                if style:  # 빈 셀이 아닌 경우만
                    if col.button(style, key=f"style_{style}", use_container_width=True):
                        st.session_state.selected_style = style
        
        # 비율 선택
        st.markdown('<div class="section-header">📐 비율</div>', unsafe_allow_html=True)
        
        # 비율 슬라이더 (참고 이미지와 동일)
        aspect_ratio = st.slider(
            "비율",
            min_value=0.5,
            max_value=2.0,
            value=1.0,
            step=0.1,
            label_visibility="collapsed"
        )
        
        # 비율에 따른 크기 설정
        if aspect_ratio < 0.8:
            selected_size = "1024x1792"  # 세로형
        elif aspect_ratio > 1.3:
            selected_size = "1792x1024"  # 가로형
        else:
            selected_size = "1024x1024"  # 정사각형
        
        # 이미지 수 선택
        st.markdown('<div class="section-header">🔢 이미지 수</div>', unsafe_allow_html=True)
        
        col1, col2, col3, col4, col5 = st.columns([1,1,1,1,6])
        
        for i, num in enumerate([1, 2, 3, 4]):
            with [col1, col2, col3, col4][i]:
                if st.button(str(num), key=f"num_{num}", use_container_width=True):
                    st.session_state.selected_num_images = num
        
        # 고급 옵션 (참고 이미지와 동일)
        with st.expander("🔧 고급 컨트롤"):
            st.slider("지침 스케일", min_value=1, max_value=20, value=7)
            st.toggle("고정된 시드 사용")
        
        # 버튼들
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
            if st.button("⚡ 즉시 생성", use_container_width=True):
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
            st.markdown('<div class="section-header">🤖 생성된 프롬프트</div>', unsafe_allow_html=True)
            st.code(st.session_state.eng_prompt, language='text')
            
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
            st.markdown('<div class="section-header">🖼️ 생성된 이미지</div>', unsafe_allow_html=True)
            
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
