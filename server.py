from starlette.applications import Starlette
from starlette.responses import JSONResponse, Response
from starlette.routing import Route, Mount
from starlette.staticfiles import StaticFiles
import uvicorn
import sqlite3
import os
import json
import re
import random

# Import crawler functions
from crawler import crawl_google_news_rss, run_agentic_sim, REGIONS, EVENT_TYPES

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "events.db")
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")

# Ensure static directories exist
os.makedirs(os.path.join(STATIC_DIR, "images"), exist_ok=True)

# Helper function to query DB
def query_db(query, args=(), one=False):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(query, args)
    rv = cursor.fetchall()
    conn.close()
    return (rv[0] if rv else None) if one else rv

# API: Get filtered events
async def get_events(request):
    import datetime
    params = request.query_params
    region = params.get("region", "")
    month = params.get("month", "") # "01" to "12"
    category = params.get("category", "") # 문화센터, 지자체, 뉴스, 축제
    event_type = params.get("event_type", "") # 공연, 체험, 전시, 강좌, 축제, 기타
    search_query = params.get("query", "")
    
    # Filter out events that have already ended before the search date
    today = datetime.date.today().strftime("%Y-%m-%d")
    search_date = today
    if month and month != "전체":
        search_date = f"2026-{month}-01"
        
    sql = "SELECT id, title, category, event_type, source_name, region, start_date, end_date, location, description, url, image_url FROM events WHERE end_date >= ?"
    args = [search_date]
    
    if region and region != "전체":
        sql += " AND region = ?"
        args.append(region)
        
    if category and category != "전체":
        sql += " AND category = ?"
        args.append(category)
        
    if event_type and event_type != "전체":
        sql += " AND event_type = ?"
        args.append(event_type)
        
    if month and month != "전체":
        # Match events that span across the chosen month in 2026
        # E.g. start_date <= '2026-month-31' AND end_date >= '2026-month-01'
        sql += " AND (start_date <= ? AND end_date >= ?)"
        args.append(f"2026-{month}-31")
        args.append(f"2026-{month}-01")
        
    if search_query:
        sql += " AND (title LIKE ? OR description LIKE ? OR location LIKE ?)"
        args.append(f"%{search_query}%")
        args.append(f"%{search_query}%")
        args.append(f"%{search_query}%")
        
    sql += " ORDER BY start_date ASC LIMIT 150"
    
    try:
        rows = query_db(sql, args)
        events = [dict(row) for row in rows]
        return JSONResponse(events)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

# API: Run crawler
async def run_crawler(request):
    try:
        body = await request.json()
    except Exception:
        body = {}
        
    category = body.get("category", "뉴스") # 문화센터, 지자체, 뉴스
    keyword = body.get("keyword", "")
    
    if not keyword:
        return JSONResponse({"error": "Keyword is required"}, status_code=400)
        
    if category == "뉴스":
        logs, new_events = crawl_google_news_rss(keyword)
    else:
        logs, new_events = run_agentic_sim(category, keyword)
        
    return JSONResponse({
        "success": True,
        "logs": logs,
        "new_events": new_events
    })

# API: Intelligent Agent Chat recommendation engine
# API: Intelligent Agent Chat recommendation engine
async def run_chat(request):
    try:
        body = await request.json()
    except Exception:
        body = {}
        
    message = body.get("message", "").strip()
    if not message:
        return JSONResponse({"error": "Message is required"}, status_code=400)
        
    # 1. Clean message and extract words
    # Remove punctuation for clean tokenization
    clean_message = re.sub(r'[^\w\s]', ' ', message)
    words = [w.strip() for w in clean_message.split() if len(w.strip()) >= 2]
    
    # 2. Rich synonyms dictionary for semantic expansion (요리 -> 쿠킹, 힐링 -> 요가 등)
    synonyms = {
        "요리": ["요리", "쿠킹", "레시피", "쿠킹클래스", "셰프", "음식", "미식", "비빔밥", "치맥", "푸드", "먹거리", "베이킹"],
        "쿠킹": ["요리", "쿠킹", "레시피", "쿠킹클래스", "셰프", "음식", "미식", "비빔밥", "치맥", "푸드", "먹거리", "베이킹"],
        "음식": ["요리", "쿠킹", "레시피", "쿠킹클래스", "셰프", "음식", "미식", "비빔밥", "치맥", "푸드", "먹거리", "베이킹"],
        "미식": ["요리", "쿠킹", "레시피", "쿠킹클래스", "셰프", "음식", "미식", "비빔밥", "치맥", "푸드", "먹거리", "베이킹"],
        "레시피": ["요리", "쿠킹", "레시피", "쿠킹클래스", "셰프", "음식", "미식", "비빔밥", "치맥", "푸드", "먹거리", "베이킹"],
        "힐링": ["힐링", "요가", "도예", "명상", "교감", "커피", "온전한", "휴식", "트레킹"],
        "요가": ["요가", "필라테스", "임산부", "명상", "스트레칭", "체형", "건강", "운동"],
        "운동": ["요가", "필라테스", "스트레칭", "운동", "체력", "헬스", "트레킹", "도보"],
        "미술": ["미술", "도예", "그림", "드로잉", "유화", "비엔날레", "미디어아트", "전시", "갤러리", "화가", "아트"],
        "그림": ["미술", "도예", "그림", "드로잉", "유화", "비엔날레", "미디어아트", "전시", "갤러리", "화가", "아트"],
        "전시": ["미술", "도예", "그림", "드로잉", "유화", "비엔날레", "미디어아트", "전시", "갤러리", "화가", "아트", "박물관"],
        "도예": ["도예", "도자기", "달항아리", "물레", "공예", "가마"],
        "음악": ["음악", "공연", "오케스트라", "콘서트", "연주", "국악", "버스킹", "디바", "교향악단", "클래식", "선율", "심포니", "가수", "노래"],
        "공연": ["음악", "공연", "오케스트라", "콘서트", "연주", "국악", "버스킹", "디바", "교향악단", "클래식", "선율", "심포니", "가수", "노래", "뮤지컬", "연극"],
        "콘서트": ["음악", "공연", "오케스트라", "콘서트", "연주", "국악", "버스킹", "디바", "교향악단", "클래식", "선율", "심포니", "가수", "노래", "뮤지컬", "연극"],
        "축제": ["축제", "페스티벌", "페스타", "행사", "군항제", "야시장", "마켓", "0시", "머드"],
        "페스티벌": ["축제", "페스티벌", "페스타", "행사", "군항제", "야시장", "마켓", "0시", "머드"],
        "여행": ["여행", "트레킹", "투어", "관광", "에코", "제주도", "산책", "지질", "코스"]
    }
    
    expanded_keywords = set()
    for w in words:
        expanded_keywords.add(w)
        # Check direct or substring matching for synonym keys
        for key, syns in synonyms.items():
            if key in w or w in key:
                expanded_keywords.add(key)
                for syn in syns:
                    expanded_keywords.add(syn)
                    
    # 3. Intelligent entity detection with robust alias/synonym mapping
    detected_region = None
    region_mapping = {
        "서울": "서울", "경기": "경기", "인천": "인천", "강원": "강원", 
        "충북": "충북", "충청북도": "충북", "충남": "충남", "충청남도": "충남", 
        "대전": "대전", "세종": "세종", "경북": "경북", "경상북도": "경북", 
        "대구": "대구", "울산": "울산", "부산": "부산", "경남": "경남", "경상남도": "경남", 
        "전북": "전북", "전라북도": "전북", "전남": "전남", "전라남도": "전남", 
        "광주": "광주", "제주": "제주", "제주도": "제주", "특별자치도": "제주"
    }
    for alias, canonical in region_mapping.items():
        if alias in message:
            detected_region = canonical
            break
            
    detected_type = None
    type_mapping = {
        "공연": "공연", "콘서트": "공연", "연주": "공연", "음악": "공연", "오케스트라": "공연", "뮤지컬": "공연", "연극": "공연",
        "체험": "체험", "만들기": "체험", "투어": "체험", "트레킹": "체험", "도보": "체험",
        "전시": "전시", "미술": "전시", "그림": "전시", "박물관": "전시", "갤러리": "전시", "비엔날레": "전시",
        "강좌": "강좌", "교육": "강좌", "수업": "강좌", "아카데미": "강좌", "클래스": "강좌",
        "축제": "축제", "페스티벌": "축제", "페스타": "축제"
    }
    for alias, canonical in type_mapping.items():
        if alias in message:
            detected_type = canonical
            break
            
    detected_month = None
    month_match = re.search(r'(\d{1,2})\s*월', message)
    if month_match:
        m = int(month_match.group(1))
        if 1 <= m <= 12:
            detected_month = m
            
    # 4. Query all active events from local SQLite database (filtering out ended events relative to search month)
    import datetime
    today = datetime.date.today().strftime("%Y-%m-%d")
    search_date = today
    if detected_month:
        search_date = f"2026-{detected_month:02d}-01"
        
    all_rows = query_db("SELECT id, title, category, event_type, source_name, region, start_date, end_date, location, description, url, image_url FROM events WHERE end_date >= ?", (search_date,))
    events = [dict(row) for row in all_rows]
    
    # 5. Dynamic scoring matrix matching
    scored_events = []
    for ev in events:
        score = 0
        
        # Region Match (Weight: 15)
        if detected_region and ev["region"] == detected_region:
            score += 15
            
        # Event Type Match (Weight: 10)
        if detected_type and ev["event_type"] == detected_type:
            score += 10
            
        # Category Match (Weight: 8)
        for cat in ["문화센터", "지자체", "뉴스", "축제"]:
            if cat in message and ev["category"] == cat:
                score += 8
                
        # Calendar Month Match (Strict Exclusion)
        if detected_month:
            try:
                import calendar
                import datetime
                s_yr, s_mon, s_day = map(int, ev["start_date"].split("-"))
                e_yr, e_mon, e_day = map(int, ev["end_date"].split("-"))
                
                _, last_day = calendar.monthrange(2026, detected_month)
                ev_start = datetime.date(s_yr, s_mon, s_day)
                ev_end = datetime.date(e_yr, e_mon, e_day)
                
                target_start = datetime.date(2026, detected_month, 1)
                target_end = datetime.date(2026, detected_month, last_day)
                
                if ev_start <= target_end and ev_end >= target_start:
                    score += 50  # Heavy boost for perfect calendar month overlap!
                else:
                    continue  # Strict Exclusion: Skip events that do not run during the requested month!
            except Exception:
                continue
                
        # Semantic Expansion Keywords Matches (Weights: Title 10, Description 4, Location 2)
        for kw in expanded_keywords:
            if kw.lower() in ev["title"].lower():
                score += 10
            if ev["description"] and kw.lower() in ev["description"].lower():
                score += 4
            if ev["location"] and kw.lower() in ev["location"].lower():
                score += 2
            if ev["source_name"] and kw.lower() in ev["source_name"].lower():
                score += 2
                
        if score > 0:
            scored_events.append((score, ev))
            
    # Sort ranked events by score descending
    scored_events.sort(key=lambda x: x[0], reverse=True)
    matched_events = [item[1] for item in scored_events[:4]]
    
    # 6. Compose conversational response
    filters_desc = []
    if detected_region: filters_desc.append(f"**{detected_region}** 지역")
    if detected_month: filters_desc.append(f"**{detected_month}월**")
    if detected_type: filters_desc.append(f"**{detected_type}** 유형")
    
    # Add other matching keywords that are not filters
    non_filter_kws = [f"**{w}**" for w in words if w not in [detected_region, f"{detected_month}월" if detected_month else "", detected_type]]
    if non_filter_kws:
        filters_desc.extend(non_filter_kws)
        
    filters_str = ", ".join(filters_desc) if filters_desc else "전체"
    
    if matched_events:
        reply = f"안녕하세요! **문화공연 사냥꾼 지능형 비서**입니다. 🏹\n\n질문하신 키워드({filters_str})를 기반으로 데이터베이스를 실시간 분석해 최적의 추천 문화 일정을 선별해 냈습니다! 마음에 드는 일정이 있다면 상세 카드를 눌러 출처 및 위치 정보를 확인해보세요."
        return JSONResponse({
            "reply": reply,
            "events": matched_events
        })
    else:
        # Fallback to random featured events that are still active relative to today
        featured_rows = query_db("SELECT id, title, category, event_type, source_name, region, start_date, end_date, location, description, url, image_url FROM events WHERE end_date >= ? ORDER BY RANDOM() LIMIT 3", (today,))
        fallback_events = [dict(row) for row in featured_rows]
        reply = f"안녕하세요! **문화공연 사냥꾼 지능형 비서**입니다. 🏹\n\n죄송합니다. 현재 데이터베이스에서 검색어({filters_str})에 매칭되는 2026년 일정을 찾지 못했습니다.\n\n대신 우측 상단의 **[실시간 크롤링 엔진]** 탭에서 관련 키워드를 입력해 직접 최신 정보를 긁어모아 보세요! 아래는 현재 다른 사용자들이 가장 눈여겨보고 있는 실시간 대표 문화 강좌 및 축제들입니다."
        return JSONResponse({
            "reply": reply,
            "events": fallback_events
        })

# Fallback dynamic SVG Image generator to handle missing image assets
async def serve_dynamic_image(request):
    image_name = request.path_params.get("filename", "news.jpg")
    base_name = image_name.split(".")[0]
    
    # Elegant custom HSL-based gradient backgrounds for different event categories
    color_schemes = {
        "cooking": ("#FF6B6B", "#FF8E53", "Cooking & Baking"),
        "pottery": ("#8E44AD", "#C39BD3", "Ceramics & Craft"),
        "wine": ("#7D3C98", "#F1948A", "Wine & Tasting"),
        "art_class": ("#3498DB", "#85C1E9", "Oil Painting & Art"),
        "yoga": ("#1ABC9C", "#76D7C4", "Yoga & Wellness"),
        "night_market": ("#2C3E50", "#FD746C", "River Night Market"),
        "media_art": ("#00C9FF", "#92FE9D", "Interactive Media Art"),
        "gugak": ("#E67E22", "#F9E79F", "Traditional Gugak"),
        "orchestra": ("#2E4053", "#5D6D7E", "Classical Symphony"),
        "jeju_trekking": ("#2ECC71", "#27AE60", "Jeju Eco Trekking"),
        "cherry_blossom": ("#F78DA7", "#FFCCD5", "Cherry Blossom Fest"),
        "mud_festival": ("#7F8C8D", "#BDC3C7", "Boryeong Mud Play"),
        "bibimbap": ("#D35400", "#F39C12", "Gastronomy Food Festival"),
        "coffee": ("#6E2C00", "#A04000", "Spacialty Coffee Day"),
        "gyeongju": ("#112233", "#D4AF37", "Silla Historical Fest"),
        "chimaek": ("#FF9F43", "#FF5252", "Daegu Chimaek Fest"),
        "biennale": ("#3F3D56", "#6C63FF", "Gwangju Biennale"),
        "daejeon_zero": ("#0F2027", "#203A43", "Daejeon Midnight Tour"),
        "news": ("#4A00E0", "#8E2DE2", "Culture News Bulletin")
    }
    
    scheme = color_schemes.get(base_name, color_schemes["news"])
    grad_start, grad_end, text = scheme
    
    # Modern minimalist vector SVG illustration representing the event
    svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 240" width="100%" height="100%">
        <defs>
            <linearGradient id="grad_{base_name}" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:{grad_start};stop-opacity:1" />
                <stop offset="100%" style="stop-color:{grad_end};stop-opacity:1" />
            </linearGradient>
            <filter id="glow">
                <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
                <feMerge>
                    <feMergeNode in="coloredBlur"/>
                    <feMergeNode in="SourceGraphic"/>
                </feMerge>
            </filter>
        </defs>
        <rect width="100%" height="100%" fill="url(#grad_{base_name})" rx="12" />
        <rect x="15" y="15" width="370" height="210" fill="none" stroke="#ffffff" stroke-width="1.5" stroke-opacity="0.2" rx="8" />
        
        <!-- Decorative abstract geometric grids -->
        <circle cx="350" cy="50" r="80" fill="#ffffff" fill-opacity="0.05" />
        <circle cx="50" cy="190" r="40" fill="#ffffff" fill-opacity="0.05" />
        
        <!-- Central text representing event type -->
        <g transform="translate(200, 110)">
            <text text-anchor="middle" font-family="'Outfit', 'Inter', sans-serif" font-weight="900" font-size="24" fill="#ffffff" filter="url(#glow)">2026 CULTURE</text>
            <text y="35" text-anchor="middle" font-family="'Outfit', 'Inter', sans-serif" font-weight="500" font-size="14" fill="#ffffff" fill-opacity="0.9" letter-spacing="2">{text.upper()}</text>
        </g>
        
        <!-- Bottom Tag -->
        <rect x="30" y="180" width="90" height="26" rx="13" fill="#ffffff" fill-opacity="0.2" />
        <text x="75" y="197" text-anchor="middle" font-family="'Inter', sans-serif" font-weight="700" font-size="10" fill="#ffffff">PREMIUM</text>
    </svg>"""
    
    return Response(content=svg_content, media_type="image/svg+xml")

# Serve main index.html directly on root
async def homepage(request):
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return Response(content=f.read(), media_type="text/html")
    return Response("Welcome! Static frontend files are being prepared.", media_type="text/plain")

# App Setup
routes = [
    Route("/", endpoint=homepage, methods=["GET"]),
    Route("/api/events", endpoint=get_events, methods=["GET"]),
    Route("/api/crawl", endpoint=run_crawler, methods=["POST"]),
    Route("/api/chat", endpoint=run_chat, methods=["POST"]),
    Route("/static/images/{filename}", endpoint=serve_dynamic_image, methods=["GET"]),
]

app = Starlette(debug=True, routes=routes)

# Mount the static files directory for normal assets
app.mount("/static", app=StaticFiles(directory=STATIC_DIR), name="static")

if __name__ == "__main__":
    print("[SERVER] Starting Antigravity 2026 Culture Agent server on http://localhost:8000")
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
