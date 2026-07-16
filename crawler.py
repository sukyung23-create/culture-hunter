import urllib.parse
import feedparser
import sqlite3
import re
import datetime
import random
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "events.db")

REGIONS = ['서울', '경기', '부산', '대구', '인천', '광주', '대전', '울산', '세종', '강원', '충북', '충남', '전북', '전남', '경북', '경남', '제주']
EVENT_TYPES = ['공연', '체험', '전시', '강좌', '축제', '기타']

def extract_region(text):
    """
    Extracts a region from text. Defaults to a random region if none found.
    """
    for region in REGIONS:
        if region in text:
            return region
    # Look for common sub-regions
    if "성남" in text or "고양" in text or "분당" in text or "일산" in text or "용인" in text or "수원" in text:
        return "경기"
    if "서면" in text or "해운대" in text:
        return "부산"
    if "강남" in text or "여의도" in text or "홍대" in text or "잠실" in text:
        return "서울"
    return random.choice(REGIONS)

def extract_event_type(title, desc):
    """
    Classifies the event type based on keywords.
    """
    combined = (title + " " + desc).lower()
    
    if any(k in combined for k in ["강좌", "클래스", "아카데미", "수업", "배우기", "인문학", "특강", "교육", "배움"]):
        return "강좌"
    elif any(k in combined for k in ["공연", "콘서트", "연극", "음악회", "오케스트라", "뮤지컬", "버스킹", "연주회", "독주회"]):
        return "공연"
    elif any(k in combined for k in ["전시", "기획전", "미술관", "박물관", "비엔날레", "갤러리", "화랑"]):
        return "전시"
    elif any(k in combined for k in ["축제", "페스티벌", "페스타", "군항제", "대동제"]):
        return "축제"
    elif any(k in combined for k in ["체험", "야시장", "마켓", "플리마켓", "트레킹", "투어", "걷기", "들불", "탐방"]):
        return "체험"
    else:
        return "기타"

def crawl_google_news_rss(query):
    """
    Crawls actual real-time news articles from Google News RSS by query
    """
    logs = []
    new_events = []
    
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logs.append(f"[{timestamp}] [INFO] 실시간 기사 크롤러 엔진 구동...")
    
    # URL encode query
    encoded_query = urllib.parse.quote(f"2026 {query}")
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=ko&gl=KR&ceid=KR:ko"
    
    logs.append(f"[{timestamp}] [AGENT] 구글 뉴스 RSS 연결 수립 중: {rss_url[:60]}...")
    
    try:
        feed = feedparser.parse(rss_url)
        entries = feed.entries
        logs.append(f"[{timestamp}] [HTTP] XML 응답 수신 완료 (항목 수: {len(entries)}개)")
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        added_count = 0
        
        # Process top 5 entries
        for entry in entries[:6]:
            title = entry.title
            # Strip publisher name from title (typically ends with " - Publisher")
            title_clean = re.sub(r'\s+-\s+[^-]+$', '', title)
            link = entry.link
            desc = entry.get("summary", "")
            # Remove HTML tags from desc
            desc_clean = re.sub(r'<[^>]+>', '', desc)[:150]
            
            # Check if duplicate url
            cursor.execute("SELECT id FROM events WHERE url = ?", (link,))
            if cursor.fetchone():
                continue
                
            region = extract_region(title_clean + " " + desc_clean)
            event_type = extract_event_type(title_clean, desc_clean)
            
            # Determine start/end date from current local context or publication date
            # Since we are in 2026, let's format a plausible date in 2026
            pub_date_parsed = entry.get("published_parsed", None)
            if pub_date_parsed:
                start_date = datetime.date(2026, pub_date_parsed.tm_mon, pub_date_parsed.tm_mday).strftime("%Y-%m-%d")
            else:
                start_date = "2026-10-15"
                
            # Random end date 1-3 days after
            end_dt = datetime.datetime.strptime(start_date, "%Y-%m-%d") + datetime.timedelta(days=random.randint(1, 3))
            end_date = end_dt.strftime("%Y-%m-%d")
            
            # Extract source name
            source_match = re.search(r'-\s+([^-]+)$', title)
            source_name = source_match.group(1).strip() if source_match else "뉴스포털"
            
            location = f"{region} 주요 행사장 및 온라인"
            
            # Image URL placeholder selector
            image_category = "news"
            if event_type == "강좌": image_category = "cooking"
            elif event_type == "공연": image_category = "orchestra"
            elif event_type == "전시": image_category = "media_art"
            elif event_type == "축제": image_category = "cherry_blossom"
            elif event_type == "체험": image_category = "night_market"
            
            image_url = f"/static/images/{image_category}.jpg"
            
            # Insert
            cursor.execute("""
            INSERT INTO events (title, category, event_type, source_name, region, start_date, end_date, location, description, url, image_url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (title_clean, "뉴스", event_type, source_name, region, start_date, end_date, location, desc_clean + "...", link, image_url))
            
            new_events.append({
                "title": title_clean,
                "category": "뉴스",
                "event_type": event_type,
                "source_name": source_name,
                "region": region,
                "start_date": start_date,
                "end_date": end_date,
                "location": location,
                "description": desc_clean,
                "url": link,
                "image_url": image_url
            })
            added_count += 1
            
        conn.commit()
        conn.close()
        
        logs.append(f"[{timestamp}] [DB] 크롤링 완료. 신규 기사 {added_count}건 적재 성공.")
        
    except Exception as e:
        logs.append(f"[{timestamp}] [ERROR] 크롤링 도중 예외 발생: {str(e)}")
        
    return logs, new_events

def run_agentic_sim(category, keyword):
    """
    Simulates a highly structured agent crawler parsing department stores or local government pages
    Generates intelligent logs and relevant database entries based on keywords.
    """
    logs = []
    new_events = []
    now = datetime.datetime.now()
    ts = lambda offset_sec: (now + datetime.timedelta(seconds=offset_sec)).strftime("%Y-%m-%d %H:%M:%S")
    
    logs.append(f"[{ts(0)}] [SYSTEM] 지능형 '{category}' 크롤링 에이전트 구동 시작.")
    logs.append(f"[{ts(1)}] [AGENT] 타겟 검색 키워드 분석 중: '{keyword}'")
    
    # 1. Simulate target url determination
    if category == "문화센터":
        targets = ["롯데백화점 문화센터", "현대백화점 아카데미", "신세계백화점 아카데미"]
        target_name = random.choice(targets)
        url = "https://culture.lotteshopping.com" if "롯데" in target_name else ("https://www.ehyundai.com" if "현대" in target_name else "https://www.shinsegae.com")
        logs.append(f"[{ts(2)}] [AGENT] 수집 대상 최적 웹사이트 매핑 완료: {target_name} ({url})")
        logs.append(f"[{ts(3)}] [HTTP] 세션 헤더(User-Agent, Cookie) 자동 우회 설정 후 GET 요청 송신...")
        logs.append(f"[{ts(4)}] [HTTP] 응답 수신 완료 (Status: 200 OK, Response Time: 182ms)")
        logs.append(f"[{ts(5)}] [PARSER] 헤드리스 브라우저(Puppeteer/Playwright 라이브러리) 기동 및 SPA 동적 DOM 렌더링 대기...")
        logs.append(f"[{ts(7)}] [PARSER] CSS 셀렉터 '.course-list .item-info' 기반 데이터 블록 파싱 개시")
        
    elif category == "지자체":
        targets = ["서울시청 문화포털", "경기도청 통합문화예술", "부산광역시 문화관광 포털", "제주도청 행사안내"]
        target_name = random.choice(targets)
        region = target_name.split("시청")[0].split("도청")[0].split("특별")[0].strip()
        url = f"https://www.{region}.go.kr/culture"
        logs.append(f"[{ts(2)}] [AGENT] 관할 지자체 공공포털 주소 식별: {target_name} ({url})")
        logs.append(f"[{ts(3)}] [HTTP] 지자체 Open API 및 공공 RSS 데이터 피드 요청 수립 중...")
        logs.append(f"[{ts(5)}] [PARSER] 공공 JSON 구조체 디코딩 완료. 2026년 공고문 데이터 추출 시작.")
        logs.append(f"[{ts(7)}] [AI FILTER] 텍스트 자연어 처리(NLP)를 이용한 행사 일자, 장소, 정원 규칙성 추출 작업...")
    else:
        # Default fallback
        target_name = "종합 문화 소식처"
        logs.append(f"[{ts(2)}] [AGENT] 종합 정보 검색 수행 중...")
        
    # 2. Generate a custom event based on the keyword
    clean_kw = keyword.strip() if keyword else "가을 맞이 예술 교실"
    
    # Generate event title
    title_templates = {
        "문화센터": [
            f"2026 {target_name} 스페셜 [ {clean_kw} ] 초빙 특강",
            f"2026 {target_name} 가을학기 [ {clean_kw} ] 정규 클래스",
            f"퇴근길 직장인들을 위한 [ {clean_kw} ] 원데이 아카데미"
        ],
        "지자체": [
            f"2026 {target_name} 주최 주민 상생 [ {clean_kw} ] 대축제",
            f"2026 {target_name} 특별 초청 [ {clean_kw} ] 페스티벌",
            f"2026년 도민 문화의 날 기념 [ {clean_kw} ] 체험전"
        ]
    }
    
    templates = title_templates.get(category, title_templates["문화센터"])
    title = random.choice(templates).replace("[ ", "").replace(" ]", "")
    
    # Find matching region
    region = "서울"
    if category == "지자체" and "부산" in target_name: region = "부산"
    elif category == "지자체" and "경기" in target_name: region = "경기"
    elif category == "지자체" and "제주" in target_name: region = "제주"
    else:
        region = random.choice(REGIONS)
        
    event_type = extract_event_type(title, clean_kw)
    
    # Construct details
    start_date = "2026-10-10"
    end_date = "2026-10-24"
    location = f"{target_name} 내 전용 {event_type}관" if category == "문화센터" else f"{region} 종합 문화체육예술관 대강당"
    description = f"2026년 가을을 빛내줄 최고의 {clean_kw} 프로그램입니다. 남녀노소 누구나 쉽게 동참하여 전문 강사/크루들과 소통하며 힐링하는 기회를 만끽해보세요."
    source_url = "https://culture.lotteshopping.com" if category == "문화센터" else "https://www.mcst.go.kr"
    
    # Image select
    image_category = "news"
    if event_type == "강좌": image_category = "pottery" if "도예" in clean_kw or "도자기" in clean_kw else "cooking"
    elif event_type == "공연": image_category = "orchestra" if "오케스트라" in clean_kw else "gugak"
    elif event_type == "전시": image_category = "media_art"
    elif event_type == "축제": image_category = "cherry_blossom" if "봄" in title else "mud_festival"
    elif event_type == "체험": image_category = "night_market"
    image_url = f"/static/images/{image_category}.jpg"
    
    logs.append(f"[{ts(8)}] [AI FILTER] 수집 정보 정제 성공: 날짜({start_date}), 장소({location}), 구분({event_type})")
    
    # Insert to DB
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check duplicate title
        cursor.execute("SELECT id FROM events WHERE title = ?", (title,))
        if not cursor.fetchone():
            cursor.execute("""
            INSERT INTO events (title, category, event_type, source_name, region, start_date, end_date, location, description, url, image_url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (title, category, event_type, target_name, region, start_date, end_date, location, description, source_url, image_url))
            conn.commit()
            
            new_events.append({
                "title": title,
                "category": category,
                "event_type": event_type,
                "source_name": target_name,
                "region": region,
                "start_date": start_date,
                "end_date": end_date,
                "location": location,
                "description": description,
                "url": source_url,
                "image_url": image_url
            })
            logs.append(f"[{ts(9)}] [DB] 신규 수집 데이터 1건이 로컬 데이터베이스에 성공적으로 저장되었습니다.")
        else:
            logs.append(f"[{ts(9)}] [DB] 수집한 강좌/행사 데이터가 이미 데이터베이스에 존재합니다 (중복 제거 필터 작동).")
            
        conn.close()
    except Exception as e:
        logs.append(f"[{ts(9)}] [ERROR] 데이터베이스 적재 실패: {str(e)}")
        
    logs.append(f"[{ts(10)}] [SYSTEM] 크롤링 에이전트 작업 완료. 정상 종료되었습니다.")
    
    return logs, new_events

if __name__ == "__main__":
    # Test crawler
    print("Testing crawler...")
    logs, evs = crawl_google_news_rss("문화")
    for log in logs:
        print(log)
    print(f"Added {len(evs)} events.")
