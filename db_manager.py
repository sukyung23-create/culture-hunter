import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "events.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        category TEXT NOT NULL,
        event_type TEXT NOT NULL,
        source_name TEXT NOT NULL,
        region TEXT NOT NULL,
        start_date TEXT NOT NULL,
        end_date TEXT NOT NULL,
        location TEXT,
        description TEXT,
        url TEXT,
        image_url TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Check if we already have data
    cursor.execute("SELECT COUNT(*) FROM events")
    if cursor.fetchone()[0] == 0:
        # Seed Data
        seed_data = [
            # 1. 문화센터 (강좌)
            (
                "2026 현대백화점 가을학기 프리미엄 이탈리안 쿠킹 클래스",
                "문화센터", "강좌", "현대백화점 문화센터", "서울",
                "2026-09-01", "2026-11-30", "현대백화점 압구정본점 6층 컬처룸",
                "미슐랭 스타 레스토랑 출신 오너 셰프가 직접 전수하는 홈 파티 파스타 및 스테이크 레시피 과정입니다. 재료 손질부터 서빙 꿀팁까지 실전 위주로 진행됩니다.",
                "https://www.ehyundai.com/newCulture/main.do",
                "/static/images/cooking.jpg"
            ),
            (
                "롯데백화점 2026 봄학기 달항아리 현대 도예 클래스",
                "문화센터", "강좌", "롯데문화센터", "경기",
                "2026-03-02", "2026-05-25", "롯데백화점 분당점 문화센터",
                "한국 전통 도자기인 달항아리를 현대적으로 해석하여 손물레 작업 및 시유, 가마 소성까지 전 과정을 나만의 속도로 배워보는 힐링 아카데미 강좌입니다.",
                "https://culture.lotteshopping.com",
                "/static/images/pottery.jpg"
            ),
            (
                "신세계 아카데미 2026 초여름 와인 클래스 - 소믈리에 기초와 페어링",
                "문화센터", "강좌", "신세계 아카데미", "부산",
                "2026-06-01", "2026-07-27", "신세계백화점 센텀시티점 8층 아카데미",
                "여름 시즌에 어울리는 스파클링 와인과 화이트 와인의 기초 지식 및 세계 유명 산지별 품종 비교 테이스팅 기회를 제공합니다. 치즈 및 해산물 마리아주 실습 포함.",
                "https://www.shinsegae.com/culture/academy/index.do",
                "/static/images/wine.jpg"
            ),
            (
                "2026 직장인 퇴근길 힐링 유화 & 유화 드로잉 클래스",
                "문화센터", "강좌", "롯데문화센터", "서울",
                "2026-10-05", "2026-12-21", "롯데백화점 잠실점 문화센터",
                "지친 일상을 예술로 위로하는 저녁 시간대 드로잉 강좌입니다. 초보자도 쉽게 유화 물감 고유의 질감과 컬러를 이용하여 풍경화 및 정물화를 완성할 수 있도록 지도합니다.",
                "https://culture.lotteshopping.com",
                "/static/images/art_class.jpg"
            ),
            (
                "현대백화점 문화센터 2026 임산부를 위한 힐링 요가 & 필라테스",
                "문화센터", "강좌", "현대백화점 문화센터", "대구",
                "2026-05-04", "2026-07-27", "현대백화점 대구점 문화센터",
                "산전 임산부를 위한 체형 교정과 근력 강화, 호흡법을 안전하게 지도하는 맞춤 건강 강좌입니다. 골반 이완과 태교 명상법이 포함되어 산모와 태아의 교감을 돕습니다.",
                "https://www.ehyundai.com/newCulture/main.do",
                "/static/images/yoga.jpg"
            ),
            
            # 2. 지자체 (전시 / 공연 / 체험)
            (
                "2026 서울 한강 밤도깨비 야시장 & 푸드 트럭 페스타",
                "지자체", "체험", "서울시청", "서울",
                "2026-05-01", "2026-10-31", "여의도 한강공원 물빛광장 및 반포 한강공원",
                "매주 금, 토요일 밤을 장식하는 한강의 대표 야간 마켓입니다. 개성 넘치는 수공예품 판매대와 푸드트럭 먹거리, 그리고 밤하늘을 수놓는 소규모 버스킹 버라이어티 공연이 함께합니다.",
                "https://www.seoul.go.kr",
                "/static/images/night_market.jpg"
            ),
            (
                "부산시립미술관 2026 특별 기획전 - 미디어아트로 보는 한국 근현대사",
                "지자체", "전시", "부산미술관", "부산",
                "2026-07-01", "2026-09-30", "부산시립미술관 본관 2층 기획전시실",
                "한국 근현대사의 격동기 이정표들을 최첨단 프로젝션 맵핑 및 인터랙티브 미디어 아트로 재구성하여, 관람객이 역사의 숨결을 직접 느끼고 조작할 수 있는 체험형 대형 전시입니다.",
                "https://art.busan.go.kr",
                "/static/images/media_art.jpg"
            ),
            (
                "경기도 문화의 날 기념 찾아가는 전통 국악 관현악 대축제",
                "지자체", "공연", "경기도청", "경기",
                "2026-08-26", "2026-08-26", "수원 경기아트센터 대극장",
                "경기도 문화의 날을 맞이하여 도민들에게 전석 무료로 진행되는 고품격 오케스트라 국악 콘서트입니다. 퓨전 국악과 전통 판소리의 콜라보 무대가 선사됩니다.",
                "https://www.gg.go.kr",
                "/static/images/gugak.jpg"
            ),
            (
                "인천 송도 달빛축제공원 2026 가을 오케스트라 선율의 밤",
                "지자체", "공연", "인천시청", "인천",
                "2026-10-10", "2026-10-11", "인천 송도 달빛축제공원 야외 특설무대",
                "붉게 물드는 가을 노을 아래 시립 교향악단과 뮤지컬 디바들이 협연하는 대형 야외 음악회입니다. 돗자리를 펴고 누구나 자유롭게 명작 클래식과 오리지널 사운드트랙을 감상할 수 있습니다.",
                "https://www.incheon.go.kr",
                "/static/images/orchestra.jpg"
            ),
            (
                "제주도 돌문화공원 2026 신비로운 에코 지질 트레킹 여행",
                "지자체", "체험", "제주특별자치도", "제주",
                "2026-04-10", "2026-04-20", "제주 돌문화공원 및 곶자왈 숲길 일대",
                "화산섬 제주의 숨겨진 지질학적 가치를 전문가 해설과 함께 오감으로 체험하며 걷는 친환경 지질 여행 프로그램입니다. 돌하르방 제작 시연 및 현무암 염색 체험 클래스도 제공됩니다.",
                "https://www.jeju.go.kr",
                "/static/images/jeju_trekking.jpg"
            ),

            # 3. 주요 축제 (축제)
            (
                "2026 제64회 진해군항제 - 벚꽃 예술 축제",
                "축제", "축제", "창원시/진해군항제 조직위원회", "경남",
                "2026-03-25", "2026-04-03", "경남 창원시 진해구 중원로터리 일대 및 여좌천",
                "대한민국 최대의 벚꽃 축제인 진해군항제가 2026년 봄 만개 시기에 개최됩니다. 이충무공 승전행차 퍼레이드, 군악의장 페스티벌, 여좌천 로망스다리 불빛 연출 등 다채로운 행사가 열립니다.",
                "https://www.changwon.go.kr/culture/index.do",
                "/static/images/cherry_blossom.jpg"
            ),
            (
                "2026 보령머드축제 (Boryeong Mud Festival)",
                "축제", "축제", "보령축제관광재단", "충남",
                "2026-07-17", "2026-07-26", "보령 대천해수욕장 머드광장 일대",
                "전 세계인과 함께하는 여름 대표 글로벌 페스티벌! 머드 미끄럼틀, 머드탕, 컬러머드 페인팅 등 액티브한 체험존과 해변 야간 대형 K-POP 메가 콘서트가 연이어 개최됩니다.",
                "https://www.mudfestival.or.kr",
                "/static/images/mud_festival.jpg"
            ),
            (
                "2026 전주 비빔밥 대축제 - 미식 문화 체험",
                "축제", "축제", "전주시/전주문화재단", "전북",
                "2026-10-08", "2026-10-12", "전주 한옥마을 및 향교 일대",
                "유네스코 미식 도시 전주에서 펼쳐지는 대형 푸드 페스티벌입니다. 대형 비빔밥 퍼포먼스, 한옥마을 야간 연회, 로컬 셰프 요리 경연 대회 및 전통 한지 한복 패션쇼가 펼쳐집니다.",
                "http://www.bibimbapfest.com",
                "/static/images/bibimbap.jpg"
            ),
            (
                "2026 강릉 커피축제 - 바다와 커피의 낭만",
                "축제", "축제", "강릉문화재단", "강원",
                "2026-10-01", "2026-10-04", "강릉 안목 커피거리 및 강릉아레나",
                "대한민국 바리스타들의 성지, 강릉에서 향긋한 가을 바다 내음과 함께 명품 핸드드립 커피를 무료 시음하고 스페셜티 세미나 및 월드 바리스타 챔피언십 경연을 즐기는 축제입니다.",
                "http://www.coffeefestival.net",
                "/static/images/coffee.jpg"
            ),
            (
                "2026 경주 신라문화제 - 역사와 미래의 공존",
                "축제", "축제", "경주시/경주문화재단", "경북",
                "2026-10-09", "2026-10-15", "경주 봉황대, 대릉원 및 금관총 일대",
                "찬란한 천년 고도 신라의 숨결을 그대로 복원하는 전통 문화 종합 예술 축제입니다. 신라 제향 의식, 화랑 무예 대회, 첨성대 미디어 파사드 및 드론 라이트 쇼가 밤하늘을 수놓습니다.",
                "http://www.sillafestival.com",
                "/static/images/gyeongju.jpg"
            ),

            # 4. 뉴스 및 기사 (뉴스 / 보도)
            (
                "[기사] 2026 대구 치맥 페스티벌, 세계적 맥주 축제로 대규모 라인업 전격 강화",
                "뉴스", "공연", "대한문화통신", "대구",
                "2026-07-01", "2026-07-05", "대구 두류공원 시민광장 일대",
                "올해 2026년 대구 치맥 페스티벌은 단순 맥주 행사를 넘어 초대형 일렉트로닉 댄스 뮤직(EDM) 메인 무대와 글로벌 락 밴드 라인업을 보강하여 아시아 최고의 야외 뮤직 축제로의 도약을 선포했다.",
                "http://www.culturenews.kr/news/101",
                "/static/images/chimaek.jpg"
            ),
            (
                "[기사] 2026 광주 비엔날레 예고, 아시아의 아방가르드를 현대적으로 해석하다",
                "뉴스", "전시", "문화트렌드저널", "광주",
                "2026-09-05", "2026-11-05", "광주비엔날레 전시관 및 국립아시아문화전당",
                "세계 미술계의 이목을 끄는 2026 광주 비엔날레 총감독 인터뷰 기사. 이번 주제는 '아시아의 정신과 기술적 영성'으로, 거대한 로봇 팔 미술품과 생성형 AI 화가들의 공동 전시가 대거 예정되어 전례 없는 기술 예술의 경지를 열어낼 예정이다.",
                "http://www.culturenews.kr/news/102",
                "/static/images/biennale.jpg"
            ),
            (
                "[기사] 대전 0시 축제 2026 개막 박차, 과거와 미래를 잇는 시간여행 테마 확정",
                "뉴스", "축제", "대전매일보도", "대전",
                "2026-08-11", "2026-08-17", "대전 중앙로, 원도심 활성화 지구 및 대전천 일원",
                "대전광역시의 야간 상권 활성화를 도모하는 '대전 0시 축제'가 2026년도에도 뜨거운 한여름 밤을 장식할 계획이다. 기상천외한 우주선 미디어아트, 레트로 스트리트 댄스 대결, 심야 플리마켓 등으로 밤샘 즐거움을 제공한다.",
                "http://www.culturenews.kr/news/103",
                "/static/images/daejeon_zero.jpg"
            )
        ]
        
        cursor.executemany("""
        INSERT INTO events (title, category, event_type, source_name, region, start_date, end_date, location, description, url, image_url)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, seed_data)
        
        conn.commit()
        print(f"[DB] Initialized database and inserted {len(seed_data)} seed events.")
    else:
        print("[DB] Database already initialized and populated.")
        
    conn.close()

if __name__ == "__main__":
    init_db()
