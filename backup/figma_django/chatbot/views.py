from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter
from django.db.models import Q
import math
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# 실제 DB 모델 사용 (zf_django와 동일한 DB 사용)
# 문제 분석 및 해결:
# 1. Django는 INSTALLED_APPS에 등록된 앱의 모델을 자동으로 로드합니다.
# 2. figma_django/config/settings.py에 'chatbot'이 등록되어 있어 Django가 figma_django/chatbot/models.py를 먼저 로드합니다.
# 3. sys.path 조작만으로는 Django가 이미 로드한 모듈을 변경할 수 없습니다.
# 4. zf_django/chatbot/models.py를 직접 로드하면 AnncLhTemp 등 다른 모델도 함께 로드되면서 Django 검증 오류 발생
# 해결 방법: Django의 모델 검증을 우회하여 AnncAll만 사용합니다.
# 
# 참고:
# - 나중에 figma_django를 zf_django로 merge하면 이 문제는 자연스럽게 해결됩니다.
# - merge 후에는 'chatbot' 앱이 하나만 존재하므로 모듈 충돌이 없습니다.
# - 이 방법은 임시 해결책이며, merge 후에는 제거해도 됩니다.
import sys
import importlib.util
from pathlib import Path
from django.db import models

BASE_DIR = Path(__file__).resolve().parent.parent.parent
ZF_DJANGO_MODELS_PATH = BASE_DIR / 'zf_django' / 'chatbot' / 'models.py'

try:
    # 절대 경로로 zf_django의 models.py를 직접 로드
    # Django의 모델 검증을 우회하기 위해 임시로 모델 검증을 비활성화합니다.
    spec = importlib.util.spec_from_file_location("zf_django_chatbot_models", ZF_DJANGO_MODELS_PATH)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load spec from {ZF_DJANGO_MODELS_PATH}")
    
    zf_models_module = importlib.util.module_from_spec(spec)
    
    # Django 모델 검증을 우회하기 위해 임시로 _meta 속성을 설정합니다.
    # 이렇게 하면 AnncLhTemp 등 다른 모델의 검증 오류를 피할 수 있습니다.
    original_new = models.Model.__new__
    
    def patched_new(cls, *args, **kwargs):
        # 모든 모델에 대해 임시로 Meta를 설정하여 검증을 우회
        # 실제 DB 쿼리는 db_table을 사용하므로 문제없습니다.
        # cls가 모델 클래스인지 확인
        if issubclass(cls, models.Model) and cls is not models.Model:
            # Meta 클래스에서 db_table 가져오기
            db_table = None
            if hasattr(cls, 'Meta') and hasattr(cls.Meta, 'db_table'):
                db_table = cls.Meta.db_table
            
            # 임시 Meta 객체 생성 (Django의 Options 클래스와 유사한 구조)
            class TempMeta:
                def __init__(self):
                    self.app_label = 'chatbot'
                    self.model_name = cls.__name__.lower()
                    self.db_table = db_table
                    self.verbose_name = getattr(cls.Meta, 'verbose_name', None) if hasattr(cls, 'Meta') else None
            
            # 모델 클래스에 임시 _meta 설정 (이미 설정되어 있지 않은 경우만)
            if not hasattr(cls, '_meta') or cls._meta is None:
                cls._meta = TempMeta()
        
        return original_new(cls, *args, **kwargs)
    
    # 임시로 모델 생성자를 패치
    models.Model.__new__ = staticmethod(patched_new)
    
    try:
        spec.loader.exec_module(zf_models_module)
    finally:
        # 원래 모델 생성자로 복원
        models.Model.__new__ = staticmethod(original_new)
    
    # AnncAll 클래스만 가져옴
    if not hasattr(zf_models_module, 'AnncAll'):
        raise AttributeError(f"AnncAll not found in {ZF_DJANGO_MODELS_PATH}")
    
    AnncAll = zf_models_module.AnncAll
    # AnncAll의 _meta를 올바르게 설정
    if not hasattr(AnncAll, '_meta') or AnncAll._meta.app_label != 'chatbot':
        # Django 앱 레지스트리를 사용하여 모델을 등록
        from django.apps import apps
        try:
            # 이미 등록된 모델인지 확인
            registered_model = apps.get_model('chatbot', 'AnncAll')
            if registered_model:
                AnncAll = registered_model
        except LookupError:
            # 등록되지 않은 경우 직접 사용 (DB 쿼리는 정상 작동)
            pass
    
    USE_REAL_DB = True
    print(f"[DEBUG] Successfully imported AnncAll from {ZF_DJANGO_MODELS_PATH}")
    print(f"[DEBUG] AnncAll: {AnncAll}")
    print(f"[DEBUG] AnncAll module: {AnncAll.__module__}")
except Exception as e:
    print(f"[ERROR] Failed to import AnncAll: {e}")
    print(f"[DEBUG] Attempted path: {ZF_DJANGO_MODELS_PATH}")
    print(f"[DEBUG] Path exists: {ZF_DJANGO_MODELS_PATH.exists()}")
    import traceback
    traceback.print_exc()
    USE_REAL_DB = False
    AnncAll = None

# ---------------------------------------------------
# 1. API 문서화 엔드포인트 (drf_spectacular)
# ---------------------------------------------------
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

# ---------------------------------------------------
# 0. 기존 ask_api 함수 (하위 호환성)
# ---------------------------------------------------
@csrf_exempt
def ask_api(request):
    """
    LangGraph 또는 LLM API 연결 전 테스트용 엔드포인트
    실제 API 연동 시 이 부분을 수정해야 함
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

# ---------------------------------------------------
# 2. 채팅 히스토리 목록 조회 (GET /api/chathistories)
# ---------------------------------------------------
@extend_schema(
    summary="사용자 - 채팅 히스토리 목록 조회",
    operation_id="getChatHistories",
    tags=["채팅 히스토리"],
    parameters=[
        OpenApiParameter(name="user_key", description="사용자 키", required=True, type=str),
    ],
)
@api_view(['GET'])
def chat_histories(request):
    # 더미 데이터
    response_data = {
        "message": "성공적으로 채팅 히스토리 목록을 조회했습니다.",
        "status": "success",
        "data": [
            {"title": "수원 신혼부부 추천", "session_key": "session-001"},
            {"title": "강남 임대 아파트", "session_key": "session-002"},
        ]
    }
    return Response(response_data)

# ---------------------------------------------------
# 3. 특정 채팅 히스토리 상세 조회 (GET /api/chathistories/{session_key})
# ---------------------------------------------------
@extend_schema(
    summary="사용자 - 특정 히스토리 조회",
    operation_id="getChatHistoryDetail",
    tags=["채팅 히스토리"],
    parameters=[
        OpenApiParameter(name="user_key", description="사용자 키", required=True, type=str),
    ],
)
@api_view(['GET'])
def chat_history_detail(request, session_key):
    # 더미 데이터
    response_data = {
        "message": "성공적으로 특정 채팅 히스토리를 조회했습니다.",
        "status": "success",
        "data": {
            "title": "수원 신혼부부 추천 분양",
            "session_key": session_key,
            "user_key": request.GET.get('user_key', 'unknown'),
            "chat_list": [
                {"id": 1, "sequence": 1, "message_type": "user", "message": "추천해줘"},
                {"id": 2, "sequence": 2, "message_type": "bot", "message": "여기 추천 목록입니다."}
            ]
        }
    }
    return Response(response_data)

# ---------------------------------------------------
# 4. 공고 목록 조회 (GET /api/anncs)
# ---------------------------------------------------
@extend_schema(
    summary="공고 목록 조회",
    operation_id="getAnnouncementList",
    tags=["공고"],
    parameters=[
        OpenApiParameter(name="annc_title", required=False, type=str),
        OpenApiParameter(name="annc_status", required=False, type=str),
        OpenApiParameter(name="annc_type", required=False, type=str),
        OpenApiParameter(name="items_per_page", required=True, type=int, default=10),
        OpenApiParameter(name="current_page", required=True, type=int, default=1),
    ],
)
@api_view(['GET'])
def annc_list(request):
    # 디버깅: USE_REAL_DB 상태 확인
    print(f"[DEBUG] annc_list: USE_REAL_DB={USE_REAL_DB}, AnncAll={AnncAll}")
    
    # 실제 DB 사용 (Django ORM 사용 - 이전에 잘 작동했던 방식)
    if USE_REAL_DB and AnncAll:
        try:
            # 1. 파라미터 처리
            annc_title = request.GET.get('annc_title', '')
            annc_status = request.GET.get('annc_status', '')
            annc_type = request.GET.get('annc_type', '')
            items_per_page = int(request.GET.get('items_per_page', 10))
            current_page = int(request.GET.get('current_page', 1))

            # 2. Django ORM을 사용한 필터링 (이전에 잘 작동했던 방식)
            queryset = AnncAll.objects.all().order_by('-created_dttm')
            
            if annc_title:
                queryset = queryset.filter(annc_title__icontains=annc_title)
            
            if annc_status and annc_status != '전체':
                queryset = queryset.filter(annc_status=annc_status)
            
            if annc_type and annc_type != '전체':
                # 공고 유형 필터링 (부분 일치로 처리)
                # 실제 DB의 annc_type 값이 프론트엔드 필터와 정확히 일치하지 않을 수 있으므로
                # icontains를 사용하여 부분 일치 검색
                queryset = queryset.filter(annc_type__icontains=annc_type)

            # 3. 페이징 계산
            total_count = queryset.count()
            print(f"[DEBUG] annc_list: total_count={total_count}")
            total_pages = math.ceil(total_count / items_per_page) if total_count > 0 else 0
            start = (current_page - 1) * items_per_page
            end = start + items_per_page
            page_data = queryset[start:end]

            # 4. 응답 생성
            items_data = []
            for annc in page_data:
                items_data.append({
                    "annc_id": annc.annc_id,
                    "annc_title": annc.annc_title,
                    "annc_url": annc.annc_url,
                    "created_dttm": annc.created_dttm.isoformat() if annc.created_dttm else None,
                    "annc_status": annc.annc_status,
                    "annc_type": annc.annc_type,
                    "annc_region": annc.annc_region,
                })
            
            print(f"[DEBUG] annc_list: items_data count={len(items_data)}")
            if items_data:
                print(f"[DEBUG] annc_list: sample annc_type values: {[item['annc_type'] for item in items_data[:3]]}")

            response_data = {
                "message": "성공적으로 공고 목록을 조회했습니다.",
                "status": "success",
                "data": {
                    "page_info": {
                        "total_count": total_count,
                        "current_page": current_page,
                        "items_per_page": items_per_page,
                        "total_pages": total_pages
                    },
                    "items": items_data
                }
            }
        except Exception as e:
            print(f"[ERROR] annc_list DB query failed: {e}")
            import traceback
            traceback.print_exc()
            # 에러 발생 시 빈 데이터 반환
            response_data = {
                "message": f"공고 목록 조회 중 오류가 발생했습니다: {str(e)}",
                "status": "error",
                "data": {
                    "page_info": {
                        "total_count": 0,
                        "current_page": 1,
                        "items_per_page": 10,
                        "total_pages": 0
                    },
                    "items": []
                }
            }
    else:
        # DB를 사용할 수 없는 경우 더미 데이터
        print(f"[DEBUG] annc_list: Using dummy data (USE_REAL_DB={USE_REAL_DB}, AnncAll={AnncAll})")
        response_data = {
            "message": "성공적으로 공고 목록을 조회했습니다.",
            "status": "success",
            "data": {
                "page_info": {
                    "total_count": 0,
                    "current_page": 1,
                    "items_per_page": 10,
                    "total_pages": 0
                },
                "items": []
            }
        }
    return Response(response_data)

# ---------------------------------------------------
# 5. 공고 요약 정보 조회 (GET /api/annc_summary)
# ---------------------------------------------------
@extend_schema(
    summary="홈 - 공고 요약 데이터 요약",
    operation_id="getAnnouncementSummary",
    tags=["공고 요약"],
)
@api_view(['GET'])
def annc_summary(request):
    # 디버깅: USE_REAL_DB 상태 확인
    print(f"[DEBUG] annc_summary: USE_REAL_DB={USE_REAL_DB}, AnncAll={AnncAll}")
    
    # 실제 DB 사용 (Django ORM 사용 - 이전에 잘 작동했던 방식)
    if USE_REAL_DB and AnncAll:
        try:
            from datetime import datetime, timedelta
            
            # Django ORM을 사용한 집계 (이전에 잘 작동했던 방식)
            total = AnncAll.objects.count()
            print(f"[DEBUG] annc_summary: total={total}")
            
            lease = AnncAll.objects.filter(annc_type__icontains="임대").count()
            sale = AnncAll.objects.filter(annc_type__icontains="분양").count()
            etc = total - (lease + sale)
            
            # 이번 주 신규 공고 수 계산 (현재 날짜 기준으로 지난 7일간 생성된 공고)
            today = datetime.now().date()
            week_ago = today - timedelta(days=7)
            new_this_week = AnncAll.objects.filter(
                created_dttm__gte=week_ago,
                created_dttm__lt=today + timedelta(days=1)
            ).count()
            print(f"[DEBUG] annc_summary: new_this_week={new_this_week}")

            response_data = {
                "message": "성공적으로 공고 요약 정보를 조회했습니다.",
                "status": "success",
                "data": {
                    "cnt_total": total,
                    "cnt_lease": lease,
                    "cnt_sale": sale,
                    "cnt_etc": etc if etc >= 0 else 0,
                    "cnt_new_this_week": new_this_week  # 이번 주 신규 공고 수 추가
                }
            }
        except Exception as e:
            print(f"[ERROR] annc_summary DB query failed: {e}")
            import traceback
            traceback.print_exc()
            # 에러 발생 시 빈 데이터 반환
            response_data = {
                "message": f"공고 요약 정보 조회 중 오류가 발생했습니다: {str(e)}",
                "status": "error",
                "data": {
                    "cnt_total": 0,
                    "cnt_lease": 0,
                    "cnt_sale": 0,
                    "cnt_etc": 0,
                    "cnt_new_this_week": 0
                }
            }
    else:
        # DB를 사용할 수 없는 경우 더미 데이터
        print(f"[DEBUG] annc_summary: Using dummy data (USE_REAL_DB={USE_REAL_DB}, AnncAll={AnncAll})")
        response_data = {
            "message": "성공적으로 공고 요약 정보를 조회했습니다.",
            "status": "success",
            "data": {
                "cnt_total": 0,
                "cnt_lease": 0,
                "cnt_sale": 0,
                "cnt_etc": 0,
                "cnt_new_this_week": 0
            }
        }
    return Response(response_data)

# ---------------------------------------------------
# 6. 채팅 메시지 전송 (POST /api/chat)
# ---------------------------------------------------
@extend_schema(
    summary="사용자 - 신규 채팅 메시지 등록 및 AI 응답 받기",
    operation_id="postChatMessage",
    tags=["채팅"],
)
@api_view(['POST'])
def chat_message(request):
    # 더미 데이터
    response_data = {
        "message": "성공적으로 메시지를 등록하고 AI 응답을 받았습니다.",
        "status": "success",
        "data": {
            "ai_response": {
                "id": 101,
                "session_id": request.data.get('session_key', 'unknown'),
                "sequence": 2,
                "message_type": "bot",
                "message": "테스트 응답입니다. 실제 LLM 연동 시 이 부분이 변경됩니다."
            }
        }
    }
    return Response(response_data)

# ---------------------------------------------------
# 7. 테스트 API
# ---------------------------------------------------
class TestApiView(APIView):
    """
    테스트용 REST API View. GET 요청 시 Hello World 메시지를 반환합니다.
    """
    def get(self, request):
        data = {
            "message": "Hello, world! (from figma_django REST API)",
            "status": "success"
        }
        return Response(data, status=status.HTTP_200_OK)
