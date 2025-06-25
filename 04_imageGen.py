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

# 커스텀 CSS 스타일
st.markdown("""
<style>
    /* 메인 컨테이너 스타일링 */
    .main-container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 2rem;
    }
    
    /* 헤더 스타일 */
    .header {
        text-align: center;
        margin-bottom: 3rem;
        padding: 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        color: white;
    }
    
    .header h1 {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
        font-weight: 700;
    }
    
    .header p {
        font-size: 1.2rem;
        opacity: 0.9;
    }
    
    /* 카드 스타일 */
    .card {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
        border: 1px solid #e0e0e0;
    }
    
    /* 입력 섹션 스타일 */
    .input-section {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    
    /* 옵션 그룹 스타일 */
    .option-group {
        display: flex;
        gap: 1rem;
        margin-bottom: 1rem;
    }
    
    .option-item {
        flex: 1;
        background: white;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #ddd;
    }
    
    /* 버튼 스타일 */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
    }
    
    /* 이미지 갤러리 스타일 */
    .image-gallery {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 1.5rem;
        margin-top: 2rem;
    }
    
    .image-item {
        background: white;
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        transition: transform 0.3s ease;
    }
    
    .image-item:hover {
        transform: translateY(-5px);
    }
    
    /* 사이드바 스타일 */
    .sidebar .element-container {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    
    /* 사이드바 전체 배경 강제 설정 */
    .css-1d391kg,
    [data-testid="stSidebar"] {
        background-color: #ffffff !important;
    }
    
    /* 사이드바 내부 컨테이너 */
    [data-testid="stSidebar"] > div {
        background-color: #ffffff !important;
    }
    
    /* 사이드바 모든 텍스트 색상 강제 설정 */
    [data-testid="stSidebar"] .stMarkdown, 
    [data-testid="stSidebar"] .stText,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] div,
    [data-testid="stSidebar"] span {
        color: #333333 !important;
    }
    
    /* 사이드바 헤더 스타일 */
    [data-testid="stSidebar"] h3 {
        color: #2c3e50 !important;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    
    /* 사이드바 입력 필드 스타일 */
    [data-testid="stSidebar"] .stTextInput > div > div > input {
        background-color: #ffffff !important;
        color: #333333 !important;
        border: 2px solid #e9ecef !important;
        border-radius: 8px;
    }
    
    /* 사이드바 입력 필드 라벨 */
    [data-testid="stSidebar"] .stTextInput > label {
        color: #495057 !important;
        font-weight: 500;
    }
    
    /* 사이드바 체크박스 */
    [data-testid="stSidebar"] .stCheckbox > label {
        color: #495057 !important;
    }
    
    /* 사이드바 도움말 텍스트 */
    [data-testid="stSidebar"] .stTextInput > div > div > div {
        color: #6c757d !important;
    }
    
    /* 사이드바 체크박스 텍스트 */
    [data-testid="stSidebar"] .stCheckbox label span {
        color: #495057 !important;
    }
    
    /* 상태 표시 스타일 */
    .status-info {
        background: #e8f5e8;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #28a745;
        margin-bottom: 1rem;
    }
    
    .status-warning {
        background: #fff3cd;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #ffc107;
        margin-bottom: 1rem;
    }
    
    .status-error {
        background: #f8d7da;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #dc3545;
        margin-bottom: 1rem;
    }
    
    /* 프롬프트 표시 스타일 */
    .prompt-display {
        background: #f1f3f4;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #667eea;
    }
    
    /* 반응형 디자인 */
    @media (max-width: 768px) {
        .option-group {
            flex-direction: column;
        }
        
        .header h1 {
            font-size: 2rem;
        }
        
        .card {
            padding: 1rem;
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
    """보안이 강화된 세션 ID 생성"""
    if 'secure_session_id' not in st.session_state:
        # 세션별 고유 ID 생성 (랜덤 + 타임스탬프 기반)
        import random
        import string
        random_str = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        session_data = f"{random_str}_{time.time()}_{os.getpid()}"
        st.session_state.secure_session_id = hashlib.sha256(session_data.encode()).hexdigest()[:16]
    return st.session_state.secure_session_id

def get_fail_log_path():
    """세션별 실패 로그 경로"""
    try:
        session_id = get_secure_session_id()
        today = datetime.now().strftime("%Y%m%d")
        return f".failcount_{session_id}_{today}.json"
    except Exception:
        # 세션 ID 생성 실패 시 기본값 사용
        today = datetime.now().strftime("%Y%m%d")
        fallback_id = hashlib.sha256(f"fallback_{time.time()}".encode()).hexdigest()[:8]
        return f".failcount_{fallback_id}_{today}.json"

def get_fail_info():
    """실패 정보 조회"""
    try:
        path = get_fail_log_path()
        if os.path.exists(path):
            with open(path, "r") as f:
                data = json.load(f)
                return data.get("fail_count", 0), data.get("fail_time", 0)
    except Exception:
        # 파일 읽기 실패 시 기본값 반환
        pass
    return 0, 0

def set_fail_info(fail_count, fail_time):
    """실패 정보 저장"""
    try:
        path = get_fail_log_path()
        with open(path, "w") as f:
            json.dump({"fail_count": fail_count, "fail_time": fail_time}, f)
    except Exception:
        # 파일 저장 실패 시 무시 (메모리에서만 관리)
        pass

def check_user_access(user_code):
    """사용자 접근 권한 확인"""
    if not user_code:
        return False, 0, "코드를 입력해주세요."
    
    # 실패 정보 확인
    fail_count, fail_time = get_fail_info()
    block_seconds = 30 * 60  # 30분
    
    if fail_count >= 5:
        now = time.time()
        if now - fail_time < block_seconds:
            left_min = int((block_seconds - (now - fail_time)) // 60) + 1
            return False, 0, f"5회 이상 오류로 {left_min}분간 접근이 제한됩니다."
        else:
            # 제한 해제
            set_fail_info(0, 0)
            fail_count = 0
    
    # 코드 검증 - secrets 파일 안전하게 읽기
    try:
        user_limits = st.secrets.get("user_codes", {})
        # 문자열로 저장된 경우를 대비해 안전하게 변환
        limit_value = user_limits.get(user_code, "0")
        limit = int(limit_value)
    except Exception as e:
        st.error(f"설정 파일 읽기 오류: {e}")
        return False, 0, "시스템 오류가 발생했습니다."
    
    if limit > 0 or limit == -1:
        # 성공 시 실패 카운트 초기화
        set_fail_info(0, 0)
        return True, limit, ""
    else:
        # 실패 카운트 증가
        fail_count += 1
        current_time = int(time.time()) if fail_count >= 5 else fail_time
        set_fail_info(fail_count, current_time)
        
        if fail_count >= 5:
            return False, 0, "5회 이상 오류로 30분간 접근이 제한됩니다."
        else:
            return False, 0, f"유효하지 않은 코드입니다. (실패 {fail_count}/5회)"

def generate_prompt(user_input, style):
    """프롬프트 생성"""
    gpt_prompt = f"""당신은 AI 이미지 프롬프트 엔지니어입니다.
아래는 사용자의 간단한 한글 설명입니다.
---
{user_input} {f'({style})' if style != '자동(Auto, best fit)' else ''}
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
    
    # 영어 프롬프트와 설명 추출
    eng_match = re.search(r"\[English Prompt\]\s*```([\s\S]+?)```", ai_response)
    desc_match = re.search(r"\[프롬프트 설명\]\s*([\s\S]+)", ai_response)
    
    eng_prompt = eng_match.group(1).strip() if eng_match else ""
    kor_desc = desc_match.group(1).strip() if desc_match else ""
    
    # 요약 생성
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
    """이미지 생성"""
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
    if "last_user_code" not in st.session_state:
        st.session_state.last_user_code = ""

init_session_state()

# 메인 레이아웃
st.markdown('<div class="main-container">', unsafe_allow_html=True)

# 헤더
st.markdown("""
<div class="header">
    <h1>🎨 AI 이미지 생성기</h1>
    <p>한글로 원하는 그림을 설명하면 AI가 프롬프트를 완성하고 이미지를 생성합니다</p>
</div>
""", unsafe_allow_html=True)

# 사이드바 - 이용자 코드만
with st.sidebar:
    st.markdown("### 🔐 이용자 인증")
    
    # 디버그 정보 (개발 중에만 사용)
    if st.checkbox("디버그 모드", value=False):
        try:
            available_codes = list(st.secrets.get("user_codes", {}).keys())
            st.write(f"등록된 코드 수: {len(available_codes)}")
            st.write("등록된 코드들:", available_codes)
        except Exception as e:
            st.error(f"Secrets 파일 읽기 오류: {e}")
    
    # 보안 강화된 코드 입력 (자동완성 방지)
    user_code = st.text_input(
        "이용자 코드",
        max_chars=16,
        type="password",  # 패스워드 타입으로 변경하여 자동완성 방지
        help="제공받은 이용자 코드를 입력하세요",
        key="user_code_input"
    )
    
    # 접근 권한 확인
    is_valid, limit, error_msg = check_user_access(user_code)
    
    if error_msg:
        if "제한" in error_msg:
            st.markdown(f'<div style="background: #f8d7da; padding: 1rem; border-radius: 8px; border-left: 4px solid #dc3545; margin-bottom: 1rem; color: #721c24 !important;"><strong>⚠️ {error_msg}</strong></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div style="background: #fff3cd; padding: 1rem; border-radius: 8px; border-left: 4px solid #ffc107; margin-bottom: 1rem; color: #856404 !important;"><strong>⚠️ {error_msg}</strong></div>', unsafe_allow_html=True)
    elif is_valid:
        if limit == -1:
            st.markdown('<div style="background: #d4edda; padding: 1rem; border-radius: 8px; border-left: 4px solid #28a745; margin-bottom: 1rem; color: #155724 !important;"><strong>✅ 무제한 코드</strong></div>', unsafe_allow_html=True)
        else:
            remaining = limit - st.session_state.used_count
            st.markdown(f'<div style="background: #d4edda; padding: 1rem; border-radius: 8px; border-left: 4px solid #28a745; margin-bottom: 1rem; color: #155724 !important;"><strong>✅ 사용 가능: {remaining}장 남음</strong></div>', unsafe_allow_html=True)
    
    # 코드가 변경되면 사용량 초기화
    if st.session_state.last_user_code != user_code:
        st.session_state.used_count = 0
        st.session_state.last_user_code = user_code

# 메인 콘텐츠
if is_valid:
    # 입력 섹션
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 📝 이미지 설명 입력")
    
    user_input = st.text_area(
        "원하는 이미지를 한글로 자세히 설명해주세요",
        height=120,
        placeholder="예: 석양이 지는 바다가에서 혼자 앉아있는 소녀, 따뜻한 분위기, 파스텔 톤"
    )
    
    st.markdown("### ⚙️ 생성 옵션")
    
    # 옵션을 나란히 배치
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**이미지 크기/비율**")
        sizes = [
            ("1:1 정사각형 (1024×1024)", "1024x1024"),
            ("세로형 (1024×1792)", "1024x1792"),
            ("가로형 (1792×1024)", "1792x1024")
        ]
        size_labels = [x[0] for x in sizes]
        selected_size_idx = st.selectbox(
            "크기 선택",
            range(len(size_labels)),
            format_func=lambda x: size_labels[x],
            label_visibility="collapsed"
        )
        selected_size = sizes[selected_size_idx][1]
    
    with col2:
        st.markdown("**스타일/화풍**")
        styles = [
            "자동(Auto, best fit)", "사진(Real photo)", "디즈니 스타일(Disney style cartoon)",
            "픽사 3D 스타일(Pixar 3D animation)", "드림웍스 스타일(Dreamworks style)",
            "일본풍 애니메이션(Japanese anime)", "수채화(Watercolor painting)", "유화(Oil painting)",
            "연필 드로잉(Pencil sketch)", "픽토그램(Flat pictogram icon)", "미니멀리즘(Minimalist flat design)",
            "아트포스터(Vintage art poster)", "반 고흐(Vincent van Gogh style)", "에드워드 호퍼(Edward Hopper style)",
            "앤디 워홀(Andy Warhol pop art)", "구스타프 클림트(Gustav Klimt style)", "무하(Alphonse Mucha Art Nouveau)",
            "헤이즐 블룸(Hazel Bloom digital art)"
        ]
        selected_style = st.selectbox(
            "스타일 선택",
            styles,
            label_visibility="collapsed"
        )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 버튼 섹션
    st.markdown('<div class="card">', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔧 프롬프트 생성", use_container_width=True):
            if not user_input.strip():
                st.warning("먼저 이미지 설명을 입력해주세요!")
            else:
                with st.spinner("AI가 디테일한 프롬프트를 생성 중입니다..."):
                    eng_prompt, kor_desc, summary = generate_prompt(user_input, selected_style)
                    st.session_state.eng_prompt = eng_prompt
                    st.session_state.kor_desc = kor_desc
                    st.session_state.summary = summary
    
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
                    images = generate_images(st.session_state.eng_prompt, selected_size, 1)
                    if images:
                        st.session_state.all_images.append({
                            "url": images[0],
                            "caption": st.session_state.get("summary", "")
                        })
                        if limit > 0:
                            st.session_state.used_count += 1
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 프롬프트 표시
    if st.session_state.get('eng_prompt'):
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 🤖 생성된 프롬프트")
        
        st.markdown('<div class="prompt-display">', unsafe_allow_html=True)
        st.markdown("**영어 프롬프트:**")
        st.code(st.session_state.eng_prompt, language='text')
        st.markdown('</div>', unsafe_allow_html=True)
        
        with st.expander("프롬프트 설명 및 수정"):
            st.markdown("**프롬프트 해석:**")
            st.info(st.session_state.get('kor_desc', ''))
            
            kor_prompt_update = st.text_area(
                "프롬프트를 수정하거나 추가 요청사항을 입력하세요",
                value=st.session_state.get('kor_desc', ''),
                height=100
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
        st.markdown("### 🎨 이미지 생성")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            num_images = st.selectbox(
                "생성할 이미지 수",
                [1, 2, 3, 4],
                index=0
            )
        
        with col2:
            if st.button("🎨 이미지 생성", use_container_width=True):
                if limit > 0 and st.session_state.used_count + num_images > limit:
                    st.error(f"생성 가능 횟수를 초과합니다. (현재: {st.session_state.used_count}/{limit})")
                else:
                    with st.spinner(f"{num_images}장의 이미지를 생성 중입니다..."):
                        images = generate_images(st.session_state.eng_prompt, selected_size, num_images)
                        
                        for url in images:
                            st.session_state.all_images.append({
                                "url": url,
                                "caption": st.session_state.summary
                            })
                        
                        if limit > 0:
                            st.session_state.used_count += num_images
                        
                        st.success(f"{len(images)}장의 이미지가 생성되었습니다!")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # 생성된 이미지 갤러리
    if st.session_state.all_images:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 🖼️ 생성된 이미지")
        
        images = st.session_state.all_images
        n_images = len(images)
        
        # 그리드 레이아웃 결정
        if n_images == 1:
            cols = 1
        elif n_images <= 3:
            cols = n_images
        else:
            cols = 2
        
        # 이미지 표시
        for i in range(0, n_images, cols):
            row_cols = st.columns(cols)
            
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
        
        # 전체 이미지 삭제 버튼
        if st.button("🗑️ 모든 이미지 삭제", type="secondary"):
            st.session_state.all_images = []
            st.experimental_rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

else:
    # 접근 권한이 없는 경우
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 🔒 접근 권한 필요")
    st.markdown("""
    이 서비스를 이용하려면 유효한 이용자 코드가 필요합니다.
    
    **이용 방법:**
    1. 좌측 사이드바에서 제공받은 이용자 코드를 입력하세요
    2. 코드가 확인되면 AI 이미지 생성 기능을 사용할 수 있습니다
    
    **문의사항이 있으시면 관리자에게 연락해주세요.**
    """)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# 푸터
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666; padding: 1rem;'>"
    "© 2025 AI 이미지 생성기 | Powered by OpenAI DALL-E 3"
    "</div>",
    unsafe_allow_html=True
)
