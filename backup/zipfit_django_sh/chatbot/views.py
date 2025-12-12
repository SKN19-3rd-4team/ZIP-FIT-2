from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def ask_api(request):
    """
    LangGraph 또는 LLM API 연결 전 테스트용 엔드포인트
    """
    if request.method == "POST":
        data = json.loads(request.body)
        query = data.get("query", "")
        context = data.get("context", {})

        return JsonResponse({
            "answer": f"테스트 응답입니다. 질문: {query}",
            "received_context": context
        })

    return JsonResponse({"error": "POST 요청만 지원합니다."}, status=400)

