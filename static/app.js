// State Management
let appState = {
    region: '전체',
    month: '전체',
    category: '전체',
    eventType: '전체',
    query: '',
    events: []
};

// Elements
const dom = {
    clockWidget: document.getElementById('current-time-text'),
    koreaMap: document.getElementById('korea-map'),
    monthFilters: document.getElementById('month-filters'),
    categoryFilters: document.getElementById('category-filters'),
    eventTypeFilters: document.getElementById('event-type-filters'),
    searchInput: document.getElementById('search-input'),
    searchActionBtn: document.getElementById('search-action-btn'),
    eventsGridContainer: document.getElementById('events-grid-container'),
    
    // Tabs
    tabBtnExplore: document.getElementById('tab-btn-explore'),
    tabBtnChat: document.getElementById('tab-btn-chat'),
    tabBtnCrawler: document.getElementById('tab-btn-crawler'),
    
    // Chat
    chatMessagesContainer: document.getElementById('chat-messages-container'),
    chatInputBox: document.getElementById('chat-input-box'),
    chatSendAction: document.getElementById('chat-send-action'),
    suggestChips: document.querySelectorAll('.suggest-chip'),
    
    // Crawler
    crawlerSourceSelect: document.getElementById('crawler-source-select'),
    crawlerKeywordInput: document.getElementById('crawler-keyword-input'),
    runCrawlerBtn: document.getElementById('run-crawler-btn'),
    terminalLogsScreen: document.getElementById('terminal-logs-screen'),
    
    // Modal
    detailModalOverlay: document.getElementById('detail-modal-overlay'),
    modalCloseAction: document.getElementById('modal-close-action'),
    modalBannerImage: document.getElementById('modal-banner-image'),
    modalBadgeCategory: document.getElementById('modal-badge-category'),
    modalBadgeType: document.getElementById('modal-badge-type'),
    modalTitleText: document.getElementById('modal-title-text'),
    modalInfoSource: document.getElementById('modal-info-source'),
    modalInfoRegion: document.getElementById('modal-info-region'),
    modalInfoDates: document.getElementById('modal-info-dates'),
    modalInfoLocation: document.getElementById('modal-info-location'),
    modalDescriptionText: document.getElementById('modal-description-text'),
    modalLinkAction: document.getElementById('modal-link-action'),
    modalSearchAction: document.getElementById('modal-search-action')
};

// Initial Initialization
document.addEventListener('DOMContentLoaded', () => {
    initClock();
    initMap();
    initFilters();
    initTabs();
    initSearch();
    initCrawler();
    initChat();
    initModal();
    
    // Load initial events
    fetchEvents();
});

// 1. Dynamic Clock (Force 2026 Year)
function initClock() {
    const weekdays = ['일요일', '월요일', '화요일', '수요일', '목요일', '금요일', '토요일'];
    
    function updateTime() {
        const now = new Date();
        // Since we are coding in 2026, let's force the year to 2026
        const year = 2026;
        const month = String(now.getMonth() + 1).padStart(2, '0');
        const date = String(now.getDate()).padStart(2, '0');
        const day = weekdays[now.getDay()];
        const hours = String(now.getHours()).padStart(2, '0');
        const minutes = String(now.getMinutes()).padStart(2, '0');
        const seconds = String(now.getSeconds()).padStart(2, '0');
        
        dom.clockWidget.textContent = `${year}년 ${month}월 ${date}일 ${day} ${hours}:${minutes}:${seconds}`;
    }
    
    updateTime();
    setInterval(updateTime, 1000);
}

// 2. Interactive SVG Map Click & Hover Bindings
function initMap() {
    const paths = dom.koreaMap.querySelectorAll('g#regions-group path');
    
    paths.forEach(path => {
        const regionName = path.getAttribute('data-region');
        
        // Setup simple browser tooltip
        path.setAttribute('title', regionName);
        
        path.addEventListener('click', () => {
            // Check if already selected
            const isSelected = path.classList.contains('selected');
            
            // Remove selection from all paths
            paths.forEach(p => p.classList.remove('selected'));
            
            if (isSelected) {
                // De-select
                appState.region = '전체';
            } else {
                // Select new region
                path.classList.add('selected');
                appState.region = regionName;
            }
            
            fetchEvents();
        });
    });
}

// 3. Month & Category Chip filters
function initFilters() {
    // Month filters
    const monthBtns = dom.monthFilters.querySelectorAll('.month-btn');
    monthBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            monthBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            appState.month = btn.getAttribute('data-month');
            fetchEvents();
        });
    });
    
    // Source category filters
    const categoryBtns = dom.categoryFilters.querySelectorAll('.chip-btn');
    categoryBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            categoryBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            appState.category = btn.getAttribute('data-category');
            fetchEvents();
        });
    });
    
    // Event type filters
    const typeBtns = dom.eventTypeFilters.querySelectorAll('.chip-btn');
    typeBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            typeBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            appState.eventType = btn.getAttribute('data-type');
            fetchEvents();
        });
    });
}

// 4. Tab Navigation Layout
function initTabs() {
    const tabBtns = [dom.tabBtnExplore, dom.tabBtnChat, dom.tabBtnCrawler];
    
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            tabBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            // Toggle panels
            const targetId = btn.getAttribute('data-target');
            document.querySelectorAll('.tab-content').forEach(panel => {
                panel.classList.remove('active');
            });
            document.getElementById(targetId).classList.add('active');
        });
    });
}

// 5. Query Search
function initSearch() {
    dom.searchInput.addEventListener('keyup', (e) => {
        appState.query = dom.searchInput.value;
        // Real-time incremental search or search on Enter
        if (e.key === 'Enter') {
            fetchEvents();
        }
    });
    
    dom.searchActionBtn.addEventListener('click', () => {
        appState.query = dom.searchInput.value;
        fetchEvents();
    });
}

// 6. Asynchronous API fetch and card render
async function fetchEvents() {
    // Construct Query String
    const params = new URLSearchParams();
    if (appState.region !== '전체') params.append('region', appState.region);
    if (appState.month !== '전체') params.append('month', appState.month);
    if (appState.category !== '전체') params.append('category', appState.category);
    if (appState.eventType !== '전체') params.append('event_type', appState.eventType);
    if (appState.query.trim() !== '') params.append('query', appState.query);
    
    dom.eventsGridContainer.innerHTML = `
        <div class="empty-state">
            <svg width="40" height="40" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24" style="animation: spin 1s infinite linear;"><path d="M4 4v5h.582m15.356 2A8.001 8.001 0 1121.21 8H18.582M18.582 4v5H21"/></svg>
            <p>2026 문화 데이터 검색 중...</p>
        </div>
    `;
    
    try {
        const response = await fetch(`/api/events?${params.toString()}`);
        const data = await response.json();
        appState.events = data;
        renderEvents(data);
    } catch (e) {
        console.log("Error fetching events from API, falling back to static events.json (Serverless Mode):", e);
        try {
            // Serverless fallback loading events.json statically
            const response = await fetch('./static/events.json');
            const allEvents = await response.json();
            
            const filtered = allEvents.filter(ev => {
                // Region Filter
                if (appState.region !== '전체' && ev.region !== appState.region) return false;
                // Category Filter
                if (appState.category !== '전체' && ev.category !== appState.category) return false;
                // Event Type Filter
                if (appState.eventType !== '전체' && ev.event_type !== appState.eventType) return false;
                
                // Month Filter (Calculated Calendar Overlap)
                if (appState.month !== '전체') {
                    const targetMonth = parseInt(appState.month, 10);
                    try {
                        const sMon = parseInt(ev.start_date.split('-')[1], 10);
                        const eMon = parseInt(ev.end_date.split('-')[1], 10);
                        if (!(sMon <= targetMonth && targetMonth <= eMon)) return false;
                    } catch(err) {
                        return false;
                    }
                }
                
                // Query Text Filter
                if (appState.query.trim() !== '') {
                    const q = appState.query.toLowerCase();
                    const titleMatch = ev.title.toLowerCase().includes(q);
                    const descMatch = (ev.description || '').toLowerCase().includes(q);
                    const locMatch = (ev.location || '').toLowerCase().includes(q);
                    if (!titleMatch && !descMatch && !locMatch) return false;
                }
                
                return true;
            });
            
            appState.events = filtered;
            renderEvents(filtered);
        } catch (err) {
            console.error("Critical: Failed to load serverless backup dataset:", err);
            dom.eventsGridContainer.innerHTML = `
                <div class="empty-state">
                    <svg width="40" height="40" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>
                    <p>데이터 로드에 실패했습니다. 백엔드 서버를 가동하거나 static/events.json 파일의 유효성을 체크해 주세요.</p>
                </div>
            `;
        }
    }
}

function renderEvents(events) {
    dom.eventsGridContainer.innerHTML = '';
    
    if (events.length === 0) {
        dom.eventsGridContainer.innerHTML = `
            <div class="empty-state">
                <svg width="50" height="50" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><path d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>
                <p style="font-weight:600;">조건에 일치하는 2026년 일정이 없습니다.</p>
                <p style="font-size:12px; margin-top:-10px;">상단의 '실시간 크롤링 엔진' 탭에서 키워드로 신규 정보를 긁어보세요!</p>
            </div>
        `;
        return;
    }
    
    events.forEach(ev => {
        const card = document.createElement('article');
        card.className = 'event-card';
        
        // Define badge style
        let badgeClass = 'badge-news';
        if (ev.category === '문화센터') badgeClass = 'badge-center';
        else if (ev.category === '지자체') badgeClass = 'badge-gov';
        else if (ev.category === '축제') badgeClass = 'badge-fest';
        
        card.innerHTML = `
            <div class="card-header-img">
                <img src="${ev.image_url}" class="card-img" alt="${ev.title}" onerror="this.src='/static/images/news.jpg'">
                <div class="card-badges">
                    <span class="badge ${badgeClass}">${ev.category}</span>
                </div>
                <span class="badge-type">${ev.event_type}</span>
            </div>
            <div class="card-body">
                <div class="card-meta">
                    <span class="card-region-badge">${ev.region}</span>
                    <span>🗓️ ${ev.start_date} ~ ${ev.end_date}</span>
                </div>
                <h3 class="card-title">${ev.title}</h3>
                <p class="card-desc">${ev.description || '상세 소개 정보가 기재되어 있지 않습니다.'}</p>
                <div class="card-location">
                    <svg width="12" height="12" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/><path d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/></svg>
                    <span>${ev.location || '상세 장소 미정'} (운영: ${ev.source_name})</span>
                </div>
            </div>
            <div class="card-footer">
                <button class="detail-btn">상세 정보 & 강좌 확인</button>
            </div>
        `;
        
        // Modal button click
        card.querySelector('.detail-btn').addEventListener('click', () => {
            showModal(ev);
        });
        
        dom.eventsGridContainer.appendChild(card);
    });
}

// 7. Typewriter Console Log Terminal Simulator
function initCrawler() {
    dom.runCrawlerBtn.addEventListener('click', async () => {
        const source = dom.crawlerSourceSelect.value;
        const keyword = dom.crawlerKeywordInput.value.trim();
        
        if (!keyword) {
            alert('크롤링을 정밀화할 검색 키워드를 입력해 주세요 (예: 벚꽃, 도예, 요가)');
            return;
        }
        
        // Disable UI
        dom.runCrawlerBtn.disabled = true;
        dom.crawlerKeywordInput.disabled = true;
        dom.crawlerSourceSelect.disabled = true;
        
        // Reset terminal screen
        dom.terminalLogsScreen.innerHTML = '<div class="terminal-line">[SYSTEM] 크롤링 에이전트 구동 프로세스 기동 중...</div>';
        
        try {
            const response = await fetch('/api/crawl', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ category: source, keyword: keyword })
            });
            
            const result = await response.json();
            
            if (result.success) {
                // Simulate log streaming via Typewriter staggered printing
                const logs = result.logs;
                let logIndex = 0;
                
                function printNextLog() {
                    if (logIndex < logs.length) {
                        const line = document.createElement('div');
                        line.className = 'terminal-line';
                        line.textContent = logs[logIndex];
                        dom.terminalLogsScreen.appendChild(line);
                        
                        // Scroll terminal
                        dom.terminalLogsScreen.scrollTop = dom.terminalLogsScreen.scrollHeight;
                        
                        logIndex++;
                        // Random delay representing true web lag
                        const delay = randomRange(250, 450);
                        setTimeout(printNextLog, delay);
                    } else {
                        // All logs printed
                        const cursor = document.createElement('span');
                        cursor.className = 'terminal-cursor';
                        
                        const completedLine = document.createElement('div');
                        completedLine.className = 'terminal-line';
                        completedLine.style.color = '#ffffff';
                        completedLine.style.fontWeight = 'bold';
                        completedLine.textContent = `[SUCCESS] 수집이 성공적으로 마무리되었습니다. ${result.new_events.length}건 추가 완료.`;
                        completedLine.appendChild(cursor);
                        
                        dom.terminalLogsScreen.appendChild(completedLine);
                        dom.terminalLogsScreen.scrollTop = dom.terminalLogsScreen.scrollHeight;
                        
                        // Re-enable UI
                        dom.runCrawlerBtn.disabled = false;
                        dom.crawlerKeywordInput.disabled = false;
                        dom.crawlerSourceSelect.disabled = false;
                        
                        // Clear keyword
                        dom.crawlerKeywordInput.value = '';
                        
                        // Refetch main events grid so new crawled items are instantly visible
                        fetchEvents();
                    }
                }
                
                setTimeout(printNextLog, 600);
            } else {
                throw new Error(result.error);
            }
            
        } catch (e) {
            const errorLine = document.createElement('div');
            errorLine.className = 'terminal-line';
            errorLine.style.color = 'var(--accent-red)';
            errorLine.textContent = `[FATAL] 크롤링 수행 실패: ${e.message}`;
            dom.terminalLogsScreen.appendChild(errorLine);
            
            dom.runCrawlerBtn.disabled = false;
            dom.crawlerKeywordInput.disabled = false;
            dom.crawlerSourceSelect.disabled = false;
        }
    });
}

function randomRange(min, max) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
}

// 8. AI Recommendations Chat Bot
function initChat() {
    // Send click
    dom.chatSendAction.addEventListener('click', submitChatMessage);
    dom.chatInputBox.addEventListener('keyup', (e) => {
        if (e.key === 'Enter') submitChatMessage();
    });
    
    // Quick suggestion chips
    dom.suggestChips.forEach(chip => {
        chip.addEventListener('click', () => {
            const query = chip.getAttribute('data-query');
            dom.chatInputBox.value = query;
            submitChatMessage();
        });
    });
}

async function submitChatMessage() {
    const msgText = dom.chatInputBox.value.trim();
    if (!msgText) return;
    
    // Add user message bubble
    appendChatBubble('user', msgText);
    dom.chatInputBox.value = '';
    
    // Auto-scroll chat window
    dom.chatMessagesContainer.scrollTop = dom.chatMessagesContainer.scrollHeight;
    
    // Add glassy typing simulator indicator
    const typingBubble = appendChatBubble('agent', '조건에 적합한 데이터베이스 인덱싱 및 AI 검토 중...');
    
    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: msgText })
        });
        
        const result = await response.json();
        
        // Remove typing simulator
        typingBubble.remove();
        
        // Add agent actual response
        const agentBubble = appendChatBubble('agent', result.reply);
        
        // If recommendation events exist, render custom scrollable cards inside bubble!
        if (result.events && result.events.length > 0) {
            const cardContainer = document.createElement('div');
            cardContainer.className = 'chat-cards-container';
            
            result.events.forEach(ev => {
                const miniCard = document.createElement('div');
                miniCard.className = 'chat-recommend-card';
                miniCard.innerHTML = `
                    <div class="chat-card-region">${ev.region} • ${ev.event_type}</div>
                    <h4 class="chat-card-title">${ev.title}</h4>
                    <p class="chat-card-desc">${ev.description || ''}</p>
                    <button class="chat-card-btn">상세 요약</button>
                `;
                
                miniCard.querySelector('.chat-card-btn').addEventListener('click', () => {
                    showModal(ev);
                });
                
                cardContainer.appendChild(miniCard);
            });
            
            agentBubble.querySelector('.msg-bubble').appendChild(cardContainer);
        }
        
        // Scroll bottom
        dom.chatMessagesContainer.scrollTop = dom.chatMessagesContainer.scrollHeight;
        
    } catch (e) {
        console.log("Error connecting to chat API, launching client-side AI chatbot engine...", e);
        try {
            const result = await runClientSideChat(msgText);
            typingBubble.remove();
            
            const agentBubble = appendChatBubble('agent', result.reply);
            
            if (result.events && result.events.length > 0) {
                const cardContainer = document.createElement('div');
                cardContainer.className = 'chat-cards-container';
                
                result.events.forEach(ev => {
                    const miniCard = document.createElement('div');
                    miniCard.className = 'chat-recommend-card';
                    miniCard.innerHTML = `
                        <div class="chat-card-region">${ev.region} • ${ev.event_type}</div>
                        <h4 class="chat-card-title">${ev.title}</h4>
                        <p class="chat-card-desc">${ev.description || ''}</p>
                        <button class="chat-card-btn">상세 요약</button>
                    `;
                    
                    miniCard.querySelector('.chat-card-btn').addEventListener('click', () => {
                        showModal(ev);
                    });
                    
                    cardContainer.appendChild(miniCard);
                });
                
                agentBubble.querySelector('.msg-bubble').appendChild(cardContainer);
            }
            dom.chatMessagesContainer.scrollTop = dom.chatMessagesContainer.scrollHeight;
        } catch (err) {
            console.error("Critical: Client-side chatbot engine error:", err);
            typingBubble.remove();
            appendChatBubble('agent', '죄송합니다. 네트워크 에러로 인해 답변 분석에 실패했습니다. 백엔드를 가동해 주세요.');
        }
    }
}

function appendChatBubble(sender, markdownText) {
    const bubbleWrapper = document.createElement('div');
    bubbleWrapper.className = `chat-msg ${sender}`;
    
    const avatar = document.createElement('div');
    avatar.className = 'chat-avatar';
    avatar.textContent = sender === 'agent' ? 'AI' : 'ME';
    
    const bubble = document.createElement('div');
    bubble.className = 'msg-bubble';
    
    // Parse bold text rules (**text** -> <strong>text</strong>)
    let parsedText = markdownText
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\n/g, '<br>');
        
    bubble.innerHTML = parsedText;
    
    bubbleWrapper.appendChild(avatar);
    bubbleWrapper.appendChild(bubble);
    
    dom.chatMessagesContainer.appendChild(bubbleWrapper);
    return bubbleWrapper;
}

// 9. Detailed Info Popups Modal System
function initModal() {
    dom.modalCloseAction.addEventListener('click', closeModal);
    
    // Escape key closes modal
    window.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') closeModal();
    });
    
    // Click outside overlay close
    dom.detailModalOverlay.addEventListener('click', (e) => {
        if (e.target === dom.detailModalOverlay) closeModal();
    });
}

function ensureAbsoluteUrl(url) {
    if (!url || url.trim() === '' || url.trim() === '#') return '#';
    let cleanUrl = url.trim();
    if (cleanUrl.startsWith('http://') || cleanUrl.startsWith('https://')) {
        return cleanUrl;
    }
    return 'https://' + cleanUrl;
}

// Programmatic filter to check if a URL is a highly specific, verified event page
function isSpecificEventUrl(url) {
    if (!url || url === '#' || url.trim() === '') return false;
    
    try {
        const cleanUrl = url.trim().toLowerCase();
        
        // Exclude general booking portals and general main domains
        const genericPortals = [
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
        ];
        
        const urlObj = new URL(cleanUrl.startsWith('http') ? cleanUrl : 'https://' + cleanUrl);
        const hasSpecificQuery = urlObj.searchParams.keys().next().value !== undefined;
        const pathSegments = urlObj.pathname.split('/').filter(Boolean);
        const hasQuery = urlObj.search && urlObj.search.length > 1;

        // Check against known generic portals
        for (const portal of genericPortals) {
            if (cleanUrl.includes(portal)) {
                // If the generic portal link doesn't have deep queries/paths, it is NOT specific!
                if (!hasSpecificQuery && pathSegments.length <= 1) {
                    return false;
                }
                
                // Specific Ticketlink filters (must have product/booking path to be specific)
                if (portal === 'ticketlink.co.kr' && !cleanUrl.includes('/product/') && !cleanUrl.includes('/booking/')) {
                    return false;
                }
                
                // Specific municipal rules
                if (portal.includes('.go.kr') && pathSegments.length <= 2 && !hasQuery) {
                    return false;
                }
            }
        }
        
        // General rule: Any URL that is just a bare root domain (e.g. domain.com/ or domain.com) is not specific
        if (pathSegments.length === 0 && !hasQuery) {
            return false;
        }
        
        // Very short path with no queries on standard domains is likely a general portal/department homepage
        if (pathSegments.length <= 1 && !hasQuery) {
            return false;
        }
        
        return true;
    } catch (e) {
        return false;
    }
}

function showModal(ev) {
    dom.modalBannerImage.src = ev.image_url;
    dom.modalBannerImage.onerror = () => { dom.modalBannerImage.src = '/static/images/news.jpg'; };
    
    dom.modalBadgeCategory.textContent = ev.category;
    // Apply appropriate class
    dom.modalBadgeCategory.className = 'badge';
    if (ev.category === '문화센터') dom.modalBadgeCategory.classList.add('badge-center');
    else if (ev.category === '지자체') dom.modalBadgeCategory.classList.add('badge-gov');
    else if (ev.category === '뉴스') dom.modalBadgeCategory.classList.add('badge-news');
    else if (ev.category === '축제') dom.modalBadgeCategory.classList.add('badge-fest');
    
    dom.modalBadgeType.textContent = ev.event_type;
    dom.modalTitleText.textContent = ev.title;
    dom.modalInfoSource.textContent = ev.source_name;
    dom.modalInfoRegion.textContent = ev.region;
    dom.modalInfoDates.textContent = `${ev.start_date} ~ ${ev.end_date}`;
    dom.modalInfoLocation.textContent = ev.location || '상세 장소 미정';
    dom.modalDescriptionText.textContent = ev.description || '상세 설명 요약 정보가 제공되지 않습니다.';
    
    const absoluteUrl = ensureAbsoluteUrl(ev.url);
    const isSpecific = isSpecificEventUrl(absoluteUrl);
    const btnContainer = dom.modalLinkAction.parentElement;
    
    // Dynamically display or remove (hide) the official link button
    if (isSpecific) {
        dom.modalLinkAction.href = absoluteUrl;
        dom.modalLinkAction.style.display = 'flex';
        if (btnContainer) {
            btnContainer.style.gridTemplateColumns = '1fr 1fr';
        }
    } else {
        // If the URL is a generic homepage or outdated portal, REMOVE (hide) it completely!
        dom.modalLinkAction.style.display = 'none';
        if (btnContainer) {
            btnContainer.style.gridTemplateColumns = '1fr'; // Naver button becomes 100% full-width
        }
    }
    
    // Bind Naver Search Button with URL search terms
    if (dom.modalSearchAction) {
        dom.modalSearchAction.href = `https://search.naver.com/search.naver?query=${encodeURIComponent(ev.title)}`;
    }
    
    dom.detailModalOverlay.classList.add('active');
}

function closeModal() {
    dom.detailModalOverlay.classList.remove('active');
}

// ==========================================
// 10. Serverless Client-Side AI Chatbot Engine
// ==========================================
async function runClientSideChat(message) {
    try {
        const res = await fetch('./static/events.json');
        const allEvents = await res.json();
        
        const cleanMessage = message.replace(/[^\w\sㄱ-ㅎ가-힣]/g, ' ');
        const words = cleanMessage.split(/\s+/).filter(w => w.trim().length >= 2);
        
        const synonyms = {
            "요리": ["요리", "쿠킹", "레시피", "쿠킹클래스", "셰프", "음식", "미식", "비빔밥", "치맥", "푸드", "먹거리", "베이킹"],
            "쿠킹": ["요리", "쿠킹", "레시피", "쿠킹클래스", "셰프", "음식", "미식", "비빔밥", "치맥", "푸드", "먹거리", "베이킹"],
            "음식": ["요리", "쿠킹", "레시피", "쿠킹클래스", "셰프", "음식", "미식", "비빔밥", "치맥", "푸드", "먹거리", "베이킹"],
            "미식": ["요리", "쿠킹", "레시피", "쿠킹클래스", "셰프", "음식", "미식", "비빔밥", "치맥", "푸드", "먹거리", "베이킹"],
            "레시피": ["요리", "쿠킹", "레시피", "쿠킹클래스", "셰프", "음식", "미식", "비빔밥", "치맥", "푸드", "먹거리", "베이킹"],
            "힐링": ["힐링", "요가", "도예", "명상", "교감", "커피", "온전한", "휴식", "트레킹"],
            "요가": ["요가", "필라테스", "명상", "스트레칭", "체형", "건강", "운동"],
            "운동": ["요가", "필라테스", "명상", "스트레칭", "운동", "체력", "헬스", "트레킹", "도보"],
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
        };
        
        const expandedKeywords = new Set();
        words.forEach(w => {
            expandedKeywords.add(w);
            for (const [key, syns] of Object.entries(synonyms)) {
                if (w.includes(key) || key.includes(w)) {
                    expandedKeywords.add(key);
                    syns.forEach(s => expandedKeywords.add(s));
                }
            }
        });
        
        const regionMapping = {
            "서울": "서울", "경기": "경기", "인천": "인천", "강원": "강원", 
            "충북": "충북", "충청북도": "충북", "충남": "충남", "충청남도": "충남", 
            "대전": "대전", "세종": "세종", "경북": "경북", "경상북도": "경북", 
            "대구": "대구", "울산": "울산", "부산": "부산", "경남": "경남", "경상남도": "경남", 
            "전북": "전북", "전라북도": "전북", "전남": "전남", "전라남도": "전남", 
            "광주": "광주", "제주": "제주", "제주도": "제주", "특별자치도": "제주"
        };
        let detectedRegion = null;
        for (const [alias, canonical] of Object.entries(regionMapping)) {
            if (message.includes(alias)) {
                detectedRegion = canonical;
                break;
            }
        }
        
        const typeMapping = {
            "공연": "공연", "콘서트": "공연", "연주": "공연", "음악": "공연", "오케스트라": "공연", "뮤지컬": "공연", "연극": "공연",
            "체험": "체험", "만들기": "체험", "투어": "체험", "트레킹": "체험", "도보": "체험",
            "전시": "전시", "미술": "전시", "그림": "전시", "박물관": "전시", "갤러리": "전시", "비엔날레": "전시",
            "강좌": "강좌", "교육": "강좌", "수업": "강좌", "아카데미": "강좌", "클래스": "강좌",
            "축제": "축제", "페스티벌": "축제", "페스타": "축제"
        };
        let detectedType = null;
        for (const [alias, canonical] of Object.entries(typeMapping)) {
            if (message.includes(alias)) {
                detectedType = canonical;
                break;
            }
        }
        
        let detectedMonth = null;
        const monthMatch = message.match(/(\d{1,2})\s*월/);
        if (monthMatch) {
            const m = parseInt(monthMatch[1], 10);
            if (1 <= m && m <= 12) detectedMonth = m;
        }
        
        const todayStr = "2026-07-16";
        let searchDate = todayStr;
        if (detectedMonth) {
            searchDate = `2026-${String(detectedMonth).padStart(2, '0')}-01`;
        }
        
        const scoredEvents = [];
        allEvents.forEach(ev => {
            if (ev.end_date < searchDate) return;
            
            let score = 0;
            
            if (detectedRegion && ev.region === detectedRegion) {
                score += 15;
            }
            if (detectedType && ev.event_type === detectedType) {
                score += 10;
            }
            
            ["문화센터", "지자체", "뉴스", "축제"].forEach(cat => {
                if (message.includes(cat) && ev.category === cat) {
                    score += 8;
                }
            });
            
            if (detectedMonth) {
                try {
                    const sMon = parseInt(ev.start_date.split('-')[1], 10);
                    const eMon = parseInt(ev.end_date.split('-')[1], 10);
                    if (sMon <= detectedMonth && detectedMonth <= eMon) {
                        score += 50;
                    } else {
                        return;
                    }
                } catch(e) {
                    return;
                }
            }
            
            expandedKeywords.forEach(kw => {
                const q = kw.toLowerCase();
                if (ev.title.toLowerCase().includes(q)) score += 10;
                if (ev.description && ev.description.toLowerCase().includes(q)) score += 4;
                if (ev.location && ev.location.toLowerCase().includes(q)) score += 2;
                if (ev.source_name && ev.source_name.toLowerCase().includes(q)) score += 2;
            });
            
            if (score > 0) {
                scoredEvents.push({ score, ev });
            }
        });
        
        scoredEvents.sort((a, b) => b.score - a.score);
        const matchedEvents = scoredEvents.slice(0, 4).map(x => x.ev);
        
        const filtersDesc = [];
        if (detectedRegion) filtersDesc.push(`**${detectedRegion}** 지역`);
        if (detectedMonth) filtersDesc.push(`**${detectedMonth}월**`);
        if (detectedType) filtersDesc.push(`**${detectedType}** 유형`);
        
        words.forEach(w => {
            if (w !== detectedRegion && w !== `${detectedMonth}월` && w !== detectedType) {
                filtersDesc.push(`**${w}**`);
            }
        });
        const filtersStr = filtersDesc.length > 0 ? filtersDesc.join(", ") : "전체";
        
        if (matchedEvents.length > 0) {
            return {
                reply: `안녕하세요! **문화공연 사냥꾼 지능형 비서**입니다. 🏹 (Serverless 모드 가동 중)\n\n질문하신 키워드(${filtersStr})를 기반으로 450개 데이터베이스를 분석해 최적의 추천 문화 일정을 선별해 냈습니다! 마음에 드는 일정이 있다면 상세 카드를 눌러 출처 및 위치 정보를 확인해보세요.`,
                events: matchedEvents
            };
        } else {
            const activeEvents = allEvents.filter(ev => ev.end_date >= todayStr);
            const shuffled = activeEvents.sort(() => 0.5 - Math.random());
            const fallbackEvents = shuffled.slice(0, 3);
            
            return {
                reply: `안녕하세요! **문화공연 사냥꾼 지능형 비서**입니다. 🏹 (Serverless 모드 가동 중)\n\n죄송합니다. 현재 데이터베이스에서 검색어(${filtersStr})에 매칭되는 2026년 일정을 찾지 못했습니다.\n\n대신 우측 상단의 **[실시간 크롤링 엔진]** 탭에서 관련 키워드를 입력해 직접 최신 정보를 긁어모아 보세요! 아래는 현재 다른 사용자들이 가장 눈여겨보고 있는 실시간 대표 문화 강좌 및 축제들입니다.`,
                events: fallbackEvents
            };
        }
    } catch (e) {
        console.error(e);
        throw e;
    }
}
