import csv
import sqlite3
import os
import re
import urllib.parse

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "events.db")

def clean_date_to_2026(date_str):
    if not date_str:
        return "2026-06-15"
    date_str = str(date_str).strip()
    nums = re.findall(r'\d+', date_str)
    if len(nums) >= 3:
        year = "2026"
        month = f"{int(nums[1]):02d}"
        day = f"{int(nums[2]):02d}"
        m_val = int(nums[1])
        d_val = int(nums[2])
        if not (1 <= m_val <= 12): month = "06"
        if not (1 <= d_val <= 31): day = "15"
        return f"{year}-{month}-{day}"
    elif len(nums) == 2:
        month = f"{int(nums[0]):02d}"
        day = f"{int(nums[1]):02d}"
        return f"2026-{month}-{day}"
    return "2026-06-15"

def map_region(text):
    if not text:
        return "경기"
    text = str(text)
    for r in ["서울", "경기", "인천", "강원", "충북", "충남", "대전", "세종", "경북", "대구", "울산", "부산", "경남", "전북", "전남", "광주", "제주"]:
        if r in text:
            return r
    if "강원특별자치도" in text: return "강원"
    if "제주" in text or "제주특별자치도" in text: return "제주"
    if "전라남도" in text: return "전남"
    if "전라북도" in text: return "전북"
    if "경상남도" in text: return "경남"
    if "경상북도" in text: return "경북"
    if "충청남도" in text: return "충남"
    if "충청북도" in text: return "충북"
    return "경기"

def classify_event_type(genre):
    if not genre:
        return "기타"
    genre = str(genre).strip()
    if any(w in genre for w in ["클래식", "국악", "연극", "무용", "뮤지컬", "콘서트", "가요", "독창회", "음악", "오케스트라", "공연"]):
        return "공연"
    elif any(w in genre for w in ["미술", "전시", "사진", "갤러리", "박물관", "비엔날레"]):
        return "전시"
    elif any(w in genre for w in ["교육", "강좌", "아카데미", "세미나", "클래스"]):
        return "강좌"
    elif any(w in genre for w in ["체험", "만들기", "트레킹", "투어", "캠핑"]):
        return "체험"
    elif any(w in genre for w in ["축제", "페스티벌", "페스타", "행사"]):
        return "축제"
    return "기타"

def is_specific_url(url):
    if not url or url.strip() == "#" or url.strip() == "":
        return False
    try:
        clean_url = url.strip().lower()
        if not (clean_url.startswith("http://") or clean_url.startswith("https://")):
            clean_url = "https://" + clean_url
            
        parsed = urllib.parse.urlparse(clean_url)
        domain = parsed.netloc
        path = parsed.path
        query = parsed.query
        
        path_segments = [s for s in path.split("/") if s]
        if len(path_segments) == 0 and not query:
            return False
            
        generic_portals = [
            'ticketlink.co.kr',
            'visitkorea.or.kr',
            'ehyundai.com',
            'lotteshopping.com',
            'shinsegae.com',
            'shinan.go.kr',
            'gangjin.go.kr',
            'ycf.or.kr',
            'ulsanmaduhee.co.kr',
            'festivalbusan.com',
            'jangseong.go.kr',
            'jangheung.go.kr',
            'gumiramyun.com',
            'dg.go.kr',
            'cng.go.kr',
            'icheon.go.kr',
            'dongnae.go.kr',
            'ulsan.go.kr'
        ]
        
        for portal in generic_portals:
            if portal in domain:
                if 'ticketlink.co.kr' in domain:
                    if '/product/' in path or '/booking/' in path:
                        return True
                    return False
                if not query and len(path_segments) <= 2:
                    return False
                    
        if len(path_segments) <= 1 and not query:
            return False
            
        return True
    except Exception:
        return False

def import_data():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("Clearing events table...")
    cursor.execute("DELETE FROM events")
    
    # Department store culture centers are excluded by user request.
    print("Skipping premium seed elements (Department store culture centers excluded by user request).")

    # 1. Parse '서울시 문화행사 정보.csv' - ONLY import rows passing the specific URL filter
    seoul_file = "서울시 문화행사 정보.csv"
    if os.path.exists(seoul_file):
        print("Importing SPECIFIC links from 서울시 문화행사 정보.csv...")
        count = 0
        with open(seoul_file, mode="r", encoding="cp949") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if count >= 150:
                    break
                try:
                    url = row.get("문화포털상세URL", "").strip() or row.get("홈페이지?주소", "").strip() or "#"
                    if not is_specific_url(url):
                        continue # Skip non-specific link
                        
                    title = row.get("공연/행사명", "").strip()
                    if not title: continue
                    
                    category = "지자체"
                    event_type = classify_event_type(row.get("분류", "기타"))
                    source_name = row.get("기관명", "서울시") or "서울문화포털"
                    region = "서울"
                    start_date = clean_date_to_2026(row.get("시작일", "2026-06-15"))
                    end_date = clean_date_to_2026(row.get("종료일", "2026-06-15"))
                    location = row.get("장소", "").strip() or "상세 장소 미정"
                    description = row.get("프로그램소개", "").strip() or row.get("기타내용", "").strip() or f"서울시에서 열리는 고품격 {event_type} 일정입니다."
                    image_url = row.get("대표이미지", "").strip()
                    
                    if not image_url:
                        if event_type == "공연": image_url = "/static/images/orchestra.jpg"
                        elif event_type == "전시": image_url = "/static/images/media_art.jpg"
                        else: image_url = "/static/images/news.jpg"

                    cursor.execute(
                        "INSERT INTO events (title, category, event_type, source_name, region, start_date, end_date, location, description, url, image_url) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (title, category, event_type, source_name, region, start_date, end_date, location, description[:300], url, image_url)
                    )
                    count += 1
                except Exception:
                    continue
        print(f"Successfully imported {count} items from Seoul Municipal Database.")

    # 2. Parse '전국공연행사정보표준데이터.csv' - ONLY import rows passing the specific URL filter
    perf_file = "전국공연행사정보표준데이터.csv"
    if os.path.exists(perf_file):
        print("Importing SPECIFIC links from 전국공연행사정보표준데이터.csv...")
        count = 0
        with open(perf_file, mode="r", encoding="cp949") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if count >= 150:
                    break
                try:
                    url = row.get("예매정보", "").strip() or row.get("홈페이지주소", "").strip() or "#"
                    if not is_specific_url(url):
                        continue # Skip non-specific link
                        
                    title = row.get("행사명", "").strip()
                    if not title: continue
                    
                    category = "지자체"
                    event_type = "공연"
                    source_name = row.get("주최기관명", "") or row.get("제공기관명", "") or "문화행사안내"
                    region = map_region(row.get("제공기관명", "") + " " + row.get("소재지도로명주소", ""))
                    start_date = clean_date_to_2026(row.get("행사시작일자", "2026-06-15"))
                    end_date = clean_date_to_2026(row.get("행사종료일자", "2026-06-15"))
                    location = row.get("장소", "").strip() or "상세 장소 미정"
                    description = row.get("행사내용", "").strip() or f"{region} 지역에서 개최되는 풍성한 {event_type} 예술 무대입니다."
                    image_url = "/static/images/orchestra.jpg"
                    
                    cursor.execute(
                        "INSERT INTO events (title, category, event_type, source_name, region, start_date, end_date, location, description, url, image_url) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (title, category, event_type, source_name, region, start_date, end_date, location, description[:300], url, image_url)
                    )
                    count += 1
                except Exception:
                    continue
        print(f"Successfully imported {count} items from National Performance Database.")

    # 3. Parse '전국문화축제표준데이터.csv' - ONLY import rows passing the specific URL filter
    fest_file = "전국문화축제표준데이터.csv"
    if os.path.exists(fest_file):
        print("Importing SPECIFIC links from 전국문화축제표준데이터.csv...")
        count = 0
        with open(fest_file, mode="r", encoding="cp949") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if count >= 150:
                    break
                try:
                    url = row.get("홈페이지주소", "").strip() or "#"
                    if not is_specific_url(url):
                        continue # Skip non-specific link
                        
                    title = row.get("축제명", "").strip()
                    if not title: continue
                    
                    category = "축제"
                    event_type = "축제"
                    source_name = row.get("주최기관명", "") or row.get("제공기관명", "") or "축제사무국"
                    region = map_region(row.get("제공기관명", "") + " " + row.get("소재지도로명주소", ""))
                    start_date = clean_date_to_2026(row.get("축제시작일자", "2026-06-15"))
                    end_date = clean_date_to_2026(row.get("축제종료일자", "2026-06-15"))
                    location = row.get("개최장소", "").strip() or "상세 장소 미정"
                    description = row.get("축제내용", "").strip() or f"{region} 지역을 대표하는 문화예술 축제 한마당입니다."
                    image_url = "/static/images/cherry_blossom.jpg"
                    
                    if "머드" in title: image_url = "/static/images/mud_festival.jpg"
                    elif "비빔밥" in title: image_url = "/static/images/bibimbap.jpg"
                    elif "커피" in title: image_url = "/static/images/coffee.jpg"
                    elif "치맥" in title: image_url = "/static/images/chimaek.jpg"

                    cursor.execute(
                        "INSERT INTO events (title, category, event_type, source_name, region, start_date, end_date, location, description, url, image_url) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (title, category, event_type, source_name, region, start_date, end_date, location, description[:300], url, image_url)
                    )
                    count += 1
                except Exception:
                    continue
        print(f"Successfully imported {count} items from National Cultural Festival Database.")

    conn.commit()
    
    cursor.execute("SELECT COUNT(*) FROM events")
    total = cursor.fetchone()[0]
    print(f"Database fully loaded. Total elements in table: {total}")
    conn.close()

if __name__ == "__main__":
    import_data()
