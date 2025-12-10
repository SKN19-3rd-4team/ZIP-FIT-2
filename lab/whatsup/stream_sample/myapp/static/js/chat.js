// myapp/static/js/chat.js

const chatMessages = document.getElementById('chat-messages');
const userInput = document.getElementById('user-input');
const sendButton = document.getElementById('send-button');
const csrfToken = document.getElementById('csrf_token').value;

function getCsrfToken() {
    return csrfToken;
}

// 메시지/상태를 채팅창에 추가하는 함수 (이전과 동일)
function appendMessage(text, sender, id = null) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;
    if (id) {
        messageDiv.id = `msg-${id}`;
    }
    
    if (sender === 'loading') {
        messageDiv.innerHTML = `<span class="status-text">${text}</span>`;
    } else {
        messageDiv.innerText = text;
    }
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight; 
    return messageDiv;
}

// 로딩 메시지를 제거하는 함수 (이전과 동일)
function removeLoadingMessage(id) {
    const loadingMessage = document.getElementById(`msg-${id}`);
    if (loadingMessage) {
        loadingMessage.remove();
    }
}

// 입력 컨트롤을 활성화/비활성화하는 헬퍼 함수
function toggleControls(enable) {
    sendButton.disabled = !enable;
    userInput.disabled = !enable;
    if (enable) {
        userInput.focus();
    }
}

/**
 * 챗봇과의 통신을 처리하고 서버로부터 스트리밍되는 상태 메시지를 처리하는 핵심 함수
 */
async function sendMessage(message) {
    const loadingId = Date.now();
    let loadingMessageElement = null;
    
    // 1. 사용자 메시지 표시
    appendMessage(message, 'user');
    
    // 2. 초기 로딩 메시지 DOM 생성
    loadingMessageElement = appendMessage("서버 연결 대기 중...", 'loading', loadingId);
    const statusTextElement = loadingMessageElement.querySelector('.status-text');

    // 입력 컨트롤 비활성화
    toggleControls(false);

    try {
        const response = await fetch('/api/chat/', {
            method: 'POST',
            // 중요: StreamingHttpResponse는 Chunked Encoding을 사용하므로, 
            // Content-Type: application/json은 요청에만 해당됩니다.
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken() 
            },
            body: JSON.stringify({ message: message })
        });
        
        // 4xx, 5xx 에러 처리 (CSRF 실패, 400 등)
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `HTTP 오류 ${response.status}`);
        }

        // 응답 본문 리더를 가져와 스트림 처리를 시작합니다.
        const reader = response.body.getReader();
        const decoder = new TextDecoder("utf-8");
        let buffer = ""; // 파싱되지 않은 데이터 청크를 저장할 버퍼

        // 스트림에서 데이터를 읽고 처리하는 재귀 함수
        const processStream = async ({ done, value }) => {
            if (done) {
                console.log("Stream complete.");
                // 스트림이 끝나도 로딩 메시지가 남아있다면 제거 (예: 서버에서 'complete'를 안 보냈을 경우)
                if (loadingMessageElement) {
                    removeLoadingMessage(loadingId);
                }
                toggleControls(true); // 컨트롤 재활성화
                return;
            }

            buffer += decoder.decode(value, { stream: true });
            
            // SSE 형식의 구분자 '\n\n'를 기준으로 메시지를 분리합니다.
            const messages = buffer.split('\n\n');
            buffer = messages.pop(); // 마지막 불완전한 청크는 버퍼에 남깁니다.

            for (const msg of messages) {
                if (msg.startsWith('data:')) {
                    const jsonString = msg.substring(5).trim();
                    try {
                        const data = JSON.parse(jsonString);
                        
                        if (data.status === 'processing') {
                            // 1. 서버에서 보낸 실시간 상태 메시지로 UI 업데이트
                            if (statusTextElement) {
                                statusTextElement.innerText = data.message;
                            }
                        } else if (data.status === 'complete') {
                            // 2. 최종 응답 수신
                            removeLoadingMessage(loadingId);
                            appendMessage(data.response, 'bot');
                            loadingMessageElement = null; // 처리 완료 마킹
                            
                            // 최종 응답 수신 후 컨트롤 활성화
                            toggleControls(true);
                            return; // 스트림 처리를 여기서 중단
                        }
                    } catch (e) {
                        console.error("JSON 파싱 실패:", jsonString, e);
                    }
                }
            }

            // 다음 청크를 읽습니다.
            reader.read().then(processStream).catch(streamError);
        };

        const streamError = (e) => {
             console.error("스트림 읽기 실패:", e);
             if (loadingMessageElement) removeLoadingMessage(loadingId);
             appendMessage(`서버와의 연결이 끊겼습니다: ${e.message}`, 'bot');
             toggleControls(true);
        };
        
        // 스트림 읽기 시작
        reader.read().then(processStream).catch(streamError);

    } catch (error) {
        // 초기 연결 실패 시 UI 정리 및 컨트롤 활성화
        console.error('Initial Connection Error:', error);
        if (loadingMessageElement) {
            removeLoadingMessage(loadingId);
        }
        appendMessage(`초기 연결 실패: ${error.message}`, 'bot'); 
        toggleControls(true);
    }
}

// 전송 버튼 클릭 또는 Enter 키 입력 처리 핸들러 (이전과 동일)
function handleSendMessage() {
    const message = userInput.value.trim();
    if (message && !sendButton.disabled) {
        sendMessage(message);
        userInput.value = '';
    }
}

userInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
        e.preventDefault(); 
        handleSendMessage();
    }
});