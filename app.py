
import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

# 페이지 기본 설정
st.set_page_config(page_title="청소년 장보기 미션 앱", page_icon="🛒", layout="wide")

# 세션 상태 초기화
if 'page' not in st.session_state:
    st.session_state.page = 'start'
if 'selected_mission' not in st.session_state:
    st.session_state.selected_mission = None
if 'budget' not in st.session_state:
    st.session_state.budget = 0
if 'cart' not in st.session_state:
    st.session_state.cart = {}
if 'submitted' not in st.session_state:
    st.session_state.submitted = False

# 미션 및 예산 설정
MISSIONS = {
    "🍛 카레 만들기": {"name": "카레 만들기", "budget": 20000, "desc": "맛있는 카레를 만들기 위해 필요한 재료를 구입해 보세요! (예산: 20,000원)"},
    "⛺ 여름캠핑 준비하기": {"name": "여름캠핑 준비하기", "budget": 50000, "desc": "즐거운 여름캠핑을 위한 필수품과 먹거리를 준비해 보세요! (예산: 50,000원)"},
    "🎉 친구 생일파티 준비하기": {"name": "친구 생일파티 준비하기", "budget": 35000, "desc": "소중한 친구의 생일파티를 풍성하게 만들어 보세요! (예산: 35,000원)"}
}

# products.csv 파일 불러오기 함수
@st.cache_data
def load_products():
    try:
        df = pd.read_csv('products.csv')
    except Exception:
        # 파일이 없을 시 예시 데이터 생성
        sample_data = {
            '품명': ['양파', '감자', '당근', '돼지고기', '카레가루', '햇반'],
            '가격': [3000, 4000, 2000, 8000, 3500, 1500],
            '이미지 url': ['https://via.placeholder.com/150'] * 6
        }
        df = pd.DataFrame(sample_data)
        df.to_csv('products.csv', index=False, encoding='utf-8-sig')
    return df

# ----------------------------------------------------
# 1. 시작 화면
# ----------------------------------------------------
if st.session_state.page == 'start':
    st.title("🛒 청소년 장보기 미션 앱")
    st.subheader("도전하고 싶은 장보기 미션을 선택하세요!")
    st.write("---")

    for m_key, m_info in MISSIONS.items():
        with st.container():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"### {m_key}")
                st.write(m_info["desc"])
            with col2:
                if st.button("미션 선택하기", key=f"btn_{m_key}"):
                    st.session_state.selected_mission = m_info["name"]
                    st.session_state.budget = m_info["budget"]
                    st.session_state.cart = {}
                    st.session_state.submitted = False
                    st.session_state.page = 'shopping'
                    st.rerun()
            st.write("---")

# ----------------------------------------------------
# 2. 쇼핑 화면
# ----------------------------------------------------
elif st.session_state.page == 'shopping':
    st.title(f"🎯 미션: {st.session_state.selected_mission}")
    st.info(f"💵 **총 예산:** {st.session_state.budget:,}원")
    
    products_df = load_products()

    st.subheader("🛍️ 상품 목록")
    
    # 4열 격자로 상품 진열
    cols_per_row = 4
    for i in range(0, len(products_df), cols_per_row):
        cols = st.columns(cols_per_row)
        for j in range(cols_per_row):
            if i + j < len(products_df):
                row = products_df.iloc[i + j]
                name = row['품명']
                price = int(row['가격'])
                img_url = row['이미지 url']

                with cols[j]:
                    st.image(img_url, use_container_width=True)
                    st.markdown(f"**{name}**")
                    st.write(f"{price:,}원")

                    # 수량 조절 버튼
                    qty_key = f"qty_{name}"
                    if qty_key not in st.session_state:
                        st.session_state[qty_key] = st.session_state.cart.get(name, {}).get('qty', 0)

                    col_btn1, col_qty, col_btn2 = st.columns([1, 1, 1])
                    with col_btn1:
                        if st.button("➖", key=f"minus_{name}"):
                            if st.session_state[qty_key] > 0:
                                st.session_state[qty_key] -= 1
                    with col_qty:
                        st.write(f"**{st.session_state[qty_key]}**")
                    with col_btn2:
                        if st.button("➕", key=f"plus_{name}"):
                            st.session_state[qty_key] += 1

                    if st.button("장바구니 담기", key=f"add_{name}"):
                        if st.session_state[qty_key] > 0:
                            st.session_state.cart[name] = {
                                'price': price,
                                'qty': st.session_state[qty_key],
                                'img_url': img_url
                            }
                            st.toast(f"'{name}' {st.session_state[qty_key]}개가 장바구니에 담겼습니다!")
                        else:
                            st.session_state.cart.pop(name, None)
                            st.toast(f"'{name}'이(가) 장바구니에서 제외되었습니다.")

    st.write("---")

    # 하단 장바구니 영역
    st.subheader("🛒 나의 장바구니")
    
    total_spent = 0
    if st.session_state.cart:
        cart_data = []
        for item, data in st.session_state.cart.items():
            if data['qty'] > 0:
                item_total = data['price'] * data['qty']
                total_spent += item_total
                cart_data.append({
                    "품명": item,
                    "단가": f"{data['price']:,}원",
                    "수량": data['qty'],
                    "소계": f"{item_total:,}원"
                })
        if cart_data:
            st.table(pd.DataFrame(cart_data))
        else:
            st.write("장바구니에 담긴 물건이 없습니다.")
    else:
        st.write("장바구니에 담긴 물건이 없습니다.")

    remaining = st.session_state.budget - total_spent

    # 실시간 예산 현황
    col_stat1, col_stat2, col_stat3 = st.columns(3)
    col_stat1.metric("총 예산", f"{st.session_state.budget:,}원")
    col_stat2.metric("총 사용 금액", f"{total_spent:,}원")
    col_stat3.metric("남은 금액", f"{remaining:,}원")

    # 예산 초과 시 비활성화 처리 및 경고 표시
    is_over_budget = remaining < 0

    if is_over_budget:
        st.error(f"⚠️ 예산을 {abs(remaining):,}원 초과했습니다! 수량을 조절해 주세요.")
        st.button("제출하기", disabled=True, key="submit_disabled")
    else:
        if st.button("제출하기", key="submit_enabled", type="primary"):
            if total_spent == 0:
                st.warning("물건을 최소 1개 이상 장바구니에 담아주세요!")
            else:
                st.session_state.submitted = True
                st.session_state.page = 'result'
                st.rerun()

    if st.button("🔙 미션 다시 선택하기"):
        st.session_state.page = 'start'
        st.rerun()

# ----------------------------------------------------
# 3. 결과 화면
# ----------------------------------------------------
elif st.session_state.page == 'result':
    # 유의사항: 제출 버튼을 누른 경우에만 접속 허용
    if not st.session_state.submitted:
        st.warning("잘못된 접근입니다. 장보기 후 제출하기 버튼을 눌러주세요.")
        if st.button("쇼핑 화면으로 돌아가기"):
            st.session_state.page = 'shopping'
            st.rerun()
    else:
        st.title("🎉 장보기 결과 리포트")
        st.subheader(f"미션: {st.session_state.selected_mission}")
        
        total_spent = sum(item['price'] * item['qty'] for item in st.session_state.cart.values())
        remaining = st.session_state.budget - total_spent

        st.markdown("### 📊 금액 요약")
        c1, c2, c3 = st.columns(3)
        c1.metric("설정 예산", f"{st.session_state.budget:,}원")
        c2.metric("사용한 금액", f"{total_spent:,}원")
        c3.metric("남은 돈 (차액)", f"{remaining:,}원")

        st.write("---")
        st.markdown("### 📦 구매한 물건 목록")

        res_cols = st.columns(4)
        idx = 0
        for name, data in st.session_state.cart.items():
            if data['qty'] > 0:
                with res_cols[idx % 4]:
                    st.image(data['img_url'], use_container_width=True)
                    st.write(f"**{name}**")
                    st.write(f"수량: {data['qty']}개")
                    st.write(f"가격: {data['price'] * data['qty']:,}원")
                idx += 1

        st.write("---")
        st.markdown("### 📝 구매 이유 작성")
        reason = st.text_area("이 물건들을 선택하고 예산을 이렇게 사용한 이유를 적어주세요:", 
                              placeholder="예: 예산 한도 내에서 필요한 재료들을 알맞게 골랐습니다.",
                              height=120)

        # 구매 이유 작성이 완료되면 그림으로 저장 버튼 출력
        if reason.strip():
            st.success("구매 이유 생성이 완료되었습니다!")

            # 결과 이미지 캔버스 생성 (Pillow 라이브러리 활용)
            img_w, img_h = 800, 600 + (len(st.session_state.cart) * 35)
            img = Image.new('RGB', (img_w, img_h), color=(255, 255, 255))
            draw = ImageDraw.Draw(img)

            font = ImageFont.load_default()

            # 상단 제목 및 내역 그리기
            y_pos = 30
            draw.text((30, y_pos), f"미션: {st.session_state.selected_mission}", fill=(0, 0, 0), font=font)
            y_pos += 40
            draw.text((30, y_pos), f"총 예산: {st.session_state.budget:,}원 | 사용 금액: {total_spent:,}원 | 남은 돈: {remaining:,}원", fill=(0, 102, 204), font=font)
            y_pos += 40
            draw.line([(30, y_pos), (770, y_pos)], fill=(200, 200, 200), width=2)
            y_pos += 20

            draw.text((30, y_pos), "[ 구매 물건 목록 ]", fill=(0, 0, 0), font=font)
            y_pos += 30

            for name, data in st.session_state.cart.items():
                if data['qty'] > 0:
                    line = f"- {name}: {data['qty']}개 ({data['price'] * data['qty']:,}원)"
                    draw.text((40, y_pos), line, fill=(50, 50, 50), font=font)
                    y_pos += 30

            y_pos += 10
            draw.line([(30, y_pos), (770, y_pos)], fill=(200, 200, 200), width=2)
            y_pos += 20

            draw.text((30, y_pos), "[ 구매 이유 ]", fill=(0, 0, 0), font=font)
            y_pos += 30
            
            # 구매 이유 텍스트 줄바꿈 처리
            words = reason.split()
            current_line = ""
            for word in words:
                if len(current_line + word) > 40:
                    draw.text((40, y_pos), current_line, fill=(30, 30, 30), font=font)
                    y_pos += 25
                    current_line = word + " "
                else:
                    current_line += word + " "
            if current_line:
                draw.text((40, y_pos), current_line, fill=(30, 30, 30), font=font)

            # 바이너리 스트림 변환 후 다운로드 버튼 생성
            buf = BytesIO()
            img.save(buf, format="PNG")
            byte_im = buf.getvalue()

            st.download_button(
                label="🖼️ 그림으로 저장",
                data=byte_im,
                file_name=f"mission_result_{st.session_state.selected_mission}.png",
                mime="image/png"
            )
        else:
            st.info("💡 구매 이유를 작성하시면 '그림으로 저장' 버튼이 나타납니다.")

        if st.button("🔄 처음으로 돌아가기"):
            st.session_state.page = 'start'
            st.session_state.submitted = False
            st.rerun()
