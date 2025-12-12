# web/utils.py
"""
유틸리티 함수 모음

주의: user_key와 session_key는 프론트엔드에서 관리합니다.
Django session에 저장하지 않습니다.
"""
from django.conf import settings
import json
from datetime import datetime
import os


def save_response_for_dev(response_data):
    """
    개발용: API 응답을 JSON 파일로 저장
    프로덕션(DEBUG=False)에서는 저장하지 않음
    
    사용법: API 호출 후 응답 데이터를 저장하여 디버깅에 활용
    """
    if not settings.DEBUG:
        return
    
    # 프로젝트 루트의 상위 폴더로 이동 (ZIP-FIT-2/lab/ohj/chat_responses)
    from pathlib import Path
    project_root = Path(__file__).resolve().parent.parent.parent  # figma_django
    workspace_root = project_root.parent  # ZIP-FIT-2
    
    # 폴더 생성
    save_dir = workspace_root / 'lab' / 'ohj' / 'chat_responses'
    os.makedirs(save_dir, exist_ok=True)
    
    # 파일명 생성
    filename = f"response_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    filepath = save_dir / filename
    
    # JSON 파일로 저장
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(response_data, f, ensure_ascii=False, indent=2)
    
    return filepath


# 참고: user_key와 session_key 생성 함수는 프론트엔드 JavaScript에서 구현
# - user_key: localStorage에 저장 (브라우저별로 유지)
# - session_key: sessionStorage에 저장 (탭별로 유지, 새 채팅 시작 시 생성)
# 
# 예시 JavaScript 코드:
# function generateUserKey() {
#     // API에서 생성하거나 프론트엔드에서 생성
#     // 예: "매콤한 숫사슴" 형식
# }
# 
# function generateSessionKey() {
#     // UUID 생성
#     return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
#         const r = Math.random() * 16 | 0;
#         const v = c == 'x' ? r : (r & 0x3 | 0x8);
#         return v.toString(16);
#     });
# }

