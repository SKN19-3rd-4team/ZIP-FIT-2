# web/views.py
import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


# -------------------
# 홈 화면
# -------------------
def home_view(request):
    return render(request, "web/home.html")


# -------------------
# 채팅 화면
# -------------------
def chat_view(request):
    return render(request, "web/chat.html")


# -------------------
# 프로필 화면
# -------------------
def profile_view(request):
    user_context = request.session.get("user_context", {})
    children_options = ["1", "2", "3", "4"]

    if request.method == "POST":
        context = {
            "region": request.POST.get("region"),
            "age": request.POST.get("age"),
            "married": request.POST.get("married"),
            "children": request.POST.get("children"),
            "income": request.POST.get("income"),
        }
        request.session["user_context"] = context

        return render(request, "web/profile.html", {
            "user_context": context,
            "saved": True,
            "children_options": children_options,
        })

    return render(request, "web/profile.html", {
        "user_context": user_context,
        "children_options": children_options,
    })


# =====================================================================
# 공고 목록 — 필터 + 검색 + 상태 + 즐겨찾기 + 페이지네이션
# =====================================================================
def announcements_view(request):
    from django.core.paginator import Paginator
    import random

    # -------------------------------
    # 1) 더미 데이터 생성
    # -------------------------------
    STATUS_LIST = ["공고중", "정정공고중", "접수중", "접수마감"]

    announcements = [
        {
            "id": i,
            "title": f"테스트 공고 {i}",
            "category": "청년행복주택",
            "institution": "LH",
            "region": "경기",  # 기본값
            "status": random.choice(STATUS_LIST),
            "date_range": "2025.01.01 - 2025.01.20",
            "summary": "테스트 요약 내용입니다.",
            "detail_url": "#"
        }
        for i in range(1, 73)
    ]

    # -------------------------------
    # 2) 즐겨찾기 상태 (세션)
    # -------------------------------
    favorites = request.session.get("favorites", [])
    favorite_ids = {int(f["id"]) for f in favorites}

    # -------------------------------
    # 3) GET 필터 값
    # -------------------------------
    type_filter = request.GET.get("type")
    region_filter = request.GET.get("region")
    status_filter = request.GET.get("status")
    query = request.GET.get("q")

    # -------------------------------
    # 4) 필터링 적용
    # -------------------------------
    filtered = announcements

    # 유형 (category)
    if type_filter:
        filtered = [a for a in filtered if a["category"] == type_filter]

    # 지역
    if region_filter:
        filtered = [a for a in filtered if a["region"] == region_filter]

    # 상태
    if status_filter:
        filtered = [a for a in filtered if a["status"] == status_filter]

    # 검색
    if query:
        filtered = [
            a for a in filtered
            if query.lower() in a["title"].lower() or query.lower() in a["summary"].lower()
        ]

    # -------------------------------
    # 5) 페이지네이션 (6개씩)
    # -------------------------------
    paginator = Paginator(filtered, 6)
    page_obj = paginator.get_page(request.GET.get("page"))

    total = paginator.num_pages
    current = page_obj.number

    # 5페이지씩 묶기
    group_start = ((current - 1) // 5) * 5 + 1
    group_end = min(group_start + 4, total)
    page_numbers = range(group_start, group_end + 1)

    # -------------------------------
    # 6) 템플릿 렌더링
    # -------------------------------
    return render(request, "web/announcements.html", {
        "page_obj": page_obj,
        "favorite_ids": favorite_ids,

        # 페이지네이션 데이터
        "total": total,
        "current": current,
        "group_start": group_start,
        "group_end": group_end,
        "page_numbers": page_numbers,

        # 필터 GET 값 유지
        "request": request,
    })


# =====================================================================
# 즐겨찾기 추가 / 삭제
# =====================================================================
@csrf_exempt
def add_favorite(request):
    data = json.loads(request.body)
    favorites = request.session.get("favorites", [])

    if not any(f["id"] == data["id"] for f in favorites):
        favorites.append({"id": data["id"], "title": data["title"]})

    request.session["favorites"] = favorites
    return JsonResponse({"ok": True, "favorites": favorites})


@csrf_exempt
def remove_favorite(request):
    data = json.loads(request.body)
    favorites = request.session.get("favorites", [])

    favorites = [f for f in favorites if f["id"] != data["id"]]
    request.session["favorites"] = favorites
    return JsonResponse({"ok": True, "favorites": favorites})


# =====================================================================
# 챗봇 → LangGraph 중계
# =====================================================================
@csrf_exempt
def ask_view(request):
    payload = json.loads(request.body)
    user_context = request.session.get("user_context", {})

    import requests
    res = requests.post(
        "http://localhost:8000/chatbot/ask/",
        json={"query": payload.get("query", ""), "context": user_context}
    ).json()

    return JsonResponse(res)





