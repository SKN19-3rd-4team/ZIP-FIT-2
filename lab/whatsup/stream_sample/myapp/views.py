import json
import time
from django.shortcuts import render
# StreamingHttpResponse를 사용하여 응답을 청크 단위로 보냅니다.
from django.http import StreamingHttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils.decorators import decorator_from_middleware
from django.middleware.csrf import CsrfViewMiddleware

# 템플릿 렌더링 뷰 (CSRF 토큰 전달)
def index(request):
    return render(request, 'myapp/index.html')

# 실제 스트리밍 데이터를 생성하는 제너레이터 함수
def chat_generator(user_message):
    """
    서버의 실제 처리 단계에 맞춰 상태 메시지를 JSON 형태로 생성하여 yield 합니다.
    SSE 표준을 위해 각 데이터는 'data: '로 시작하고 '\n\n'로 끝나야 합니다.
    """
    
    # 1. 임베딩 단계 시작
    status1 = {'status': 'processing', 'message': '임베딩 작업 중...'}
    yield 'data: ' + json.dumps(status1) + '\n\n'
    print(f"[{time.time():.2f}] 1단계: 임베딩 처리 시작 (2초 지연)")
    time.sleep(2) 
    
    # 2. LLM 연결 단계 시작
    status2 = {'status': 'processing', 'message': 'LLM (대규모 언어 모델) 연결 중...'}
    yield 'data: ' + json.dumps(status2) + '\n\n'
    print(f"[{time.time():.2f}] 2단계: LLM 연결 시작 (3초 지연)")
    time.sleep(3) 

    # 3. 최종 응답 생성 및 전달
    if "안녕" in user_message or "하이" in user_message:
        bot_response = "안녕하세요! 서버로부터 전달받은 최종 응답입니다."
    else:
        bot_response = f"사용자 메시지 '{user_message}'에 대한 상세 답변입니다. 총 5초간 서버 단계별 처리를 완료했습니다."
    
    final_data = {'status': 'complete', 'response': bot_response}
    yield 'data: ' + json.dumps(final_data) + '\n\n'
    print(f"[{time.time():.2f}] 3단계: 최종 응답 완료")


# POST 요청을 받고 스트리밍 응답을 반환하는 API 뷰
@require_http_methods(["POST"])
def chat_api(request):
    """
    StreamingHttpResponse를 사용하여 응답 본문이 스트리밍되도록 설정합니다.
    """
    try:
        # Django 미들웨어에서 CSRF 토큰을 자동으로 검증합니다.
        
        # 요청 본문에서 사용자 메시지 추출
        data = json.loads(request.body)
        user_message = data.get('message', '')

        if not user_message:
            return JsonResponse({'error': '메시지 내용이 없습니다.'}, status=400)
            
        # StreamingHttpResponse를 사용하여 제너레이터 함수를 실행합니다.
        response = StreamingHttpResponse(
            chat_generator(user_message),
            # 클라이언트가 SSE 스트림으로 인식하도록 Content-Type을 설정합니다.
            content_type='text/event-stream'
        )
        response['Cache-Control'] = 'no-cache'
        return response

    except json.JSONDecodeError:
        # JSON 형식 오류 (일반 HTTP 응답)
        return JsonResponse({'error': '유효하지 않은 JSON 형식입니다.'}, status=400)
    except Exception as e:
        # 기타 서버 오류 (일반 HTTP 응답)
        print(f"Error during chat processing: {e}")
        return JsonResponse({'error': '내부 서버 오류가 발생했습니다.'}, status=500)