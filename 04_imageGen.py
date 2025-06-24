import streamlit as st 
from openai import OpenAI

st.title("AI 이미지 생성기 GPT-Dall-e-3")
st.write("한글로 원하는 그림 설명하면 프롬프트로 완성해주고, 최종 이미지를 생성합니다")

# API KEY 입력
st.sidebar.title("API KEY 입력")
openai_api_key = st.sidebar.text_input("OpenAI API KEY 입력", type="password")

if not openai_api_key:
    st.sidebar.warning("OpenAI API KEY 입력 필수.")
    st.stop()
    
# OpenAI 클라이언트 설정
client = OpenAI(api_key=openai_api_key)

# 한글 프롬프트 입력
user_kor_prompt = st.text_area("원하는 이미지를 한글로 설명해 주세요.", height=80)

# 스타일 레퍼런스 선택
st.subheader("이미지 스타일 레퍼런스 선택")
styles = [
    "자동(Auto, best fit)",    # 프롬프트 해석에 맡김(기본)
    "사진(Real photo)",
    "디즈니 스타일(Disney style cartoon)",
    "픽사 3D 스타일(Pixar 3D animation)",
    "드림웍스 스타일(Dreamworks style)",
    "일본풍 애니메이션(Japanese anime)",
    "수채화(Watercolor painting)",
    "유화(Oil painting)",
    "연필 드로잉(Pencil sketch)",
    "픽토그램(Flat pictogram icon)",
    "미니멀리즘(Minimalist flat design)",
    "아트포스터(Vintage art poster)",
    "반 고흐(Vincent van Gogh style)",
    "에드워드 호퍼(Edward Hopper style)",
    "앤디 워홀(Andy Warhol pop art)",
    "구스타프 클림트(Gustav Klimt style)",
    "무하(Alphonse Mucha Art Nouveau)",
    "헤이즐 블룸(Hazel Bloom digital art)"
]
style_mapping = {
    "자동(Auto, best fit)": "",
    "사진(Real photo)": "in the style of a real photo",
    "디즈니 스타일(Disney style cartoon)": "in Disney cartoon style",
    "픽사 3D 스타일(Pixar 3D animation)": "in Pixar 3D animation style",
    "드림웍스 스타일(Dreamworks style)": "in Dreamworks animation style",
    "일본풍 애니메이션(Japanese anime)": "in Japanese anime style",
    "수채화(Watercolor painting)": "in watercolor painting style",
    "유화(Oil painting)": "in oil painting style",
    "연필 드로잉(Pencil sketch)": "as a pencil sketch",
    "픽토그램(Flat pictogram icon)": "as a flat pictogram icon",
    "미니멀리즘(Minimalist flat design)": "in minimalist flat design",
    "아트포스터(Vintage art poster)": "in vintage art poster style",
    "반 고흐(Vincent van Gogh style)": "in the style of Vincent van Gogh",
    "에드워드 호퍼(Edward Hopper style)": "in the style of Edward Hopper",
    "앤디 워홀(Andy Warhol pop art)": "in Andy Warhol pop art style",
    "구스타프 클림트(Gustav Klimt style)": "in the style of Gustav Klimt",
    "무하(Alphonse Mucha Art Nouveau)": "in Alphonse Mucha Art Nouveau style",
    "헤이즐 블룸(Hazel Bloom digital art)": "in Hazel Bloom digital illustration style"
}
selected_style = st.selectbox(
    "이미지 스타일/작가 레퍼런스 선택",
    styles,
    index=0  # "자동"이 기본 선택
)
#================================================================================
# 이미지 규격/비율(DALLE-3 공식 지원)
sizes = [
    ("정사각형 1:1 (1024x1024)", "1024x1024"),
    ("세로형(1024x1792)", "1024x1792"),
    ("가로형(1792x1024)", "1792x1024")
]
selected_size_label = st.selectbox(
    "이미지 비율/사이즈 선택", [x[0] for x in sizes]
)
selected_size = [x[1] for x in sizes if x[0] == selected_size_label][0]
#==================================================================================

# 1차 프롬프트 자동 생성: 한글/영문 둘 다 풍성하게, 코드블럭 표시
if st.button("1차 프롬프트 자동 생성"):
    if not user_kor_prompt.strip():
        st.warning("먼저 한글로 원하는 그림 설명을 입력하세요!")
    else:
        with st.spinner("AI가 디테일하고 풍성한 프롬프트를 만드는 중입니다..."):
            gpt_prompt = (
                f"""당신은 AI 이미지 프롬프트 엔지니어입니다.
                아래는 사용자의 간단한 한글 설명입니다.
                ---
                {user_kor_prompt} {f'({selected_style})' if selected_style != '자동(Auto, best fit)' else ''}
                ---
                1. 이 내용을 바탕으로 색상, 질감, 배경, 분위기, 조명, 카메라 각도, 디테일, 동작, 감정 등 시각적 정보까지 추가해 풍성한 한글 프롬프트를 완성해줘.
                2. 두 번째로, 이 한글 프롬프트를 AI가 잘 이해할 수 있는 영어 프롬프트로 자연스럽게 번역해줘.
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
            )
            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[{"role": "user", "content": gpt_prompt}],
                temperature=0.6
            )
            ai_response = response.choices[0].message.content.strip()
            import re
            eng_block = ""
            eng_match = re.search(r"\[English Prompt\]\s*```([\s\S]+?)```", ai_response)
            desc_match = re.search(r"\[프롬프트 설명\]\s*([\s\S]+)", ai_response)
            if eng_match:
                eng_block = eng_match.group(1).strip()
            if desc_match:
                kor_desc = desc_match.group(1).strip()
            else:
                kor_desc = ""
            # 세션 상태에 저장
            st.session_state['eng_prompt'] = eng_block
            st.session_state['kor_desc'] = kor_desc

# 2차: 프롬프트 결과/수정/리프롬프트
if st.session_state.get('eng_prompt'):
    st.markdown("**[자동 생성된 영어 프롬프트]**")
    st.code(st.session_state['eng_prompt'], language='text')
    st.markdown("**[프롬프트 한국어 설명 및 해석]**")
    st.info(st.session_state.get('kor_desc', ''))

    # 프롬프트 해설/의도(한국어) 직접 보완 입력
    kor_prompt_update = st.text_area(
        "의도, 세부 묘사, 추가 요청사항 등 원하는 내용을 기록해두세요.",
        value=st.session_state.get('kor_desc', ''),
        height=100
    )

    # 리프롬프트(수정한 한글로 다시 영어 프롬프트)
    if st.button("리프롬프트-프롬프트를 수정합니다"):
        with st.spinner("수정된 내용을 반영해서 프롬프트 재작업 중..."):
            gpt_re_prompt = (
                f"""아래 한글 프롬프트를 더 디테일하게 보완해 AI가 잘 이해할 수 있는 영어 프롬프트로 자연스럽게 번역해줘.
                색감, 분위기, 질감, 동작, 감정, 세부 연출 등 시각적 디테일을 추가하고,
                선택한 스타일 레퍼런스(화풍/작가)도 자연스럽게 포함해줘.
                반드시 코드블럭(플레인텍스트)로 출력해.
                ```
                {kor_prompt_update}
                ```
                """
            )
            re_response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[{"role": "user", "content": gpt_re_prompt}],
                temperature=0.6  # 창의성 설정
            )
            re_eng_match = re.search(r"```([\s\S]+?)```", re_response.choices[0].message.content)
            if re_eng_match:
                st.session_state['eng_prompt'] = re_eng_match.group(1).strip()
            st.session_state['kor_desc'] = kor_prompt_update

# 이미지 생성 버튼
if st.button("이미지 생성"):
    if not st.session_state.get('eng_prompt'):
        st.warning("먼저 1차 프롬프트 자동 생성 또는 리프롬프트를 해주세요!")
    else:
        with st.spinner("이미지를 생성 중입니다..."):
            try:
                response = client.images.generate(
                    prompt=st.session_state['eng_prompt'],
                    model="dall-e-3",
                    n=1,
                    size=selected_size            
                )
                image_url = response.data[0].url
                st.image(image_url, caption="생성된 이미지", use_container_width=True)
            except Exception as e:
                st.error(f"이미지 생성 중 오류가 발생했습니다: {e}")
