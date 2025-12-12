/**
 * API 호출 유틸리티 함수
 * 
 * user_key와 session_key는 프론트엔드에서 관리합니다.
 * - user_key: localStorage에 저장 (브라우저별로 유지)
 * - session_key: sessionStorage에 저장 (탭별로 유지)
 * 
 * 참고: Mock 데이터 사용 시 mockData.js 파일을 먼저 로드해야 합니다.
 */

// ============================================
// user_key 관리
// ============================================

/**
 * user_key 생성 또는 가져오기
 * 
 * TODO: API에서 user_key 생성 엔드포인트 확인 필요
 * 현재는 프론트엔드에서 생성하는 방식 사용
 */
function getOrCreateUserKey() {
    let userKey = localStorage.getItem('user_key');
    
    if (!userKey) {
        // API에서 생성하는 경우 여기서 호출
        // 또는 프론트엔드에서 생성
        userKey = generateUserKey();
        localStorage.setItem('user_key', userKey);
    }
    
    return userKey;
}

/**
 * user_key 생성 (프론트엔드 방식)
 * 
 * TODO: API에서 생성하는 방식으로 변경 가능
 */
function generateUserKey() {
    // 625가지 조합 방식
    const adjectives = [
        '매콤한', '달콤한', '상쾌한', '용감한', '귀여운', 
        '똑똑한', '빠른', '차분한', '명랑한', '활발한',
        '조용한', '친절한', '멋진', '훌륭한', '당당한',
        '부지런한', '성실한', '밝은', '따뜻한', '시원한',
        '깔끔한', '화사한', '고요한', '신나는', '편안한'
    ];
    
    const animals = [
        '숫사슴', '오로라', '팬더', '코알라', '다람쥐',
        '토끼', '고양이', '강아지', '여우', '사자',
        '호랑이', '펭귄', '돌고래', '부엉이', '독수리',
        '곰', '늑대', '사슴', '기린', '코끼리',
        '햄스터', '앵무새', '고슴도치', '수달', '표범'
    ];
    
    const adjective = adjectives[Math.floor(Math.random() * adjectives.length)];
    const animal = animals[Math.floor(Math.random() * animals.length)];
    
    return `${adjective} ${animal}`;
}

// ============================================
// session_key 관리
// ============================================

/**
 * session_key 생성 (새 채팅 시작 시)
 */
function createSessionKey() {
    // UUID v4 생성
    const sessionKey = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        const r = Math.random() * 16 | 0;
        const v = c == 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
    
    sessionStorage.setItem('current_session_key', sessionKey);
    return sessionKey;
}

/**
 * 현재 session_key 가져오기
 */
function getCurrentSessionKey() {
    return sessionStorage.getItem('current_session_key');
}

/**
 * session_key 설정 (기존 채팅 불러올 때)
 */
function setSessionKey(sessionKey) {
    sessionStorage.setItem('current_session_key', sessionKey);
}

// ============================================
// API 호출 함수
// ============================================

/**
 * CSRF 토큰 가져오기
 */
function getCsrfToken() {
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        const [name, value] = cookie.trim().split('=');
        if (name === 'csrftoken') {
            return value;
        }
    }
    return '';
}

/**
 * 채팅 메시지 전송 및 AI 응답 받기
 * 
 * @param {string} userMessage - 사용자 메시지
 * @param {string} userKey - 사용자 키 (선택사항, 없으면 자동 생성)
 * @param {string} sessionKey - 세션 키 (선택사항, 없으면 자동 생성)
 * @returns {Promise<Object>} API 응답 데이터
 */
async function sendChatMessage(userMessage, userKey = null, sessionKey = null) {
    const finalUserKey = userKey || getOrCreateUserKey();
    const finalSessionKey = sessionKey || getCurrentSessionKey() || createSessionKey();
    
    const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify({
            user_key: finalUserKey,
            session_key: finalSessionKey,
            user_message: userMessage
        })
    });
    
    if (!response.ok) {
        throw new Error(`API 호출 실패: ${response.status}`);
    }
    
    const data = await response.json();
    
    // 개발용: 응답 저장 (선택사항)
    if (window.DEBUG_MODE) {
        console.log('API 응답:', data);
    }
    
    return data;
}

/**
 * 채팅 히스토리 목록 조회
 * 
 * @param {string} userKey - 사용자 키 (선택사항)
 * @returns {Promise<Array>} 채팅 히스토리 목록
 */
async function getChatHistories(userKey = null) {
    const finalUserKey = userKey || getOrCreateUserKey();
    
    const response = await fetch(`/api/chathistories?user_key=${encodeURIComponent(finalUserKey)}`);
    
    if (!response.ok) {
        throw new Error(`API 호출 실패: ${response.status}`);
    }
    
    const data = await response.json();
    return data.data || [];
}

/**
 * 특정 채팅 히스토리 상세 조회
 * 
 * @param {string} sessionKey - 세션 키
 * @param {string} userKey - 사용자 키 (선택사항)
 * @returns {Promise<Object>} 채팅 히스토리 상세 데이터
 */
async function getChatHistoryDetail(sessionKey, userKey = null) {
    const finalUserKey = userKey || getOrCreateUserKey();
    
    const response = await fetch(
        `/api/chathistories/${encodeURIComponent(sessionKey)}?user_key=${encodeURIComponent(finalUserKey)}`
    );
    
    if (!response.ok) {
        throw new Error(`API 호출 실패: ${response.status}`);
    }
    
    const data = await response.json();
    return data.data || {};
}

/**
 * 공고 목록 조회
 * 
 * @param {Object} params - 조회 파라미터
 * @returns {Promise<Object>} 공고 목록 데이터
 */
async function getAnnouncements(params = {}) {
    const {
        annc_title = '',
        annc_status = '전체',
        annc_type = '전체',
        items_per_page = 10,
        current_page = 1
    } = params;
    
    const queryParams = new URLSearchParams({
        annc_title,
        annc_status,
        annc_type,
        items_per_page: items_per_page.toString(),
        current_page: current_page.toString()
    });
    
    const response = await fetch(`/api/anncs?${queryParams}`);
    
    if (!response.ok) {
        throw new Error(`API 호출 실패: ${response.status}`);
    }
    
    const data = await response.json();
    return data.data || {};
}

/**
 * 공고 요약 정보 조회
 * 
 * @returns {Promise<Object>} 공고 요약 데이터
 */
async function getAnnouncementSummary() {
    const response = await fetch('/api/annc_summary');
    
    if (!response.ok) {
        throw new Error(`API 호출 실패: ${response.status}`);
    }
    
    const data = await response.json();
    return data.data || {};
}

