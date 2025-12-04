"""
LlamaParse를 이용한 PDF 파싱 모듈
Markdown 형식으로 추출하여 RAG에 최적화
"""
import os
import re
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass, field
from llama_parse import LlamaParse
from dotenv import load_dotenv

load_dotenv()


@dataclass
class ParsedElement:
    """파싱된 문서 요소"""
    content: str           # Markdown 텍스트 내용
    element_type: str      # 'text', 'table', 'heading' 등
    page_number: int       # 페이지 번호
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ParsedDocument:
    """파싱된 전체 문서"""
    file_path: str
    external_id: str
    elements: List[ParsedElement]
    raw_markdown: str


def parse_pdf(file_path: Path, external_id: str) -> ParsedDocument:
    """
    LlamaParse API로 PDF 파싱 (Markdown 형식)

    Args:
        file_path: PDF 파일 경로
        external_id: 문서 식별자 (예: LH_lease_1113)

    Returns:
        ParsedDocument: 파싱된 문서 객체
    """
    if not os.getenv("LLAMA_CLOUD_API_KEY"):
        raise ValueError("LLAMA_CLOUD_API_KEY가 환경변수에 설정되지 않았습니다.")

    parser = LlamaParse(
        result_type="markdown",
        verbose=True
    )

    docs = parser.load_data(str(file_path))
    elements = []
    raw_markdown_parts = []

    for doc in docs:
        page_num = doc.metadata.get('page_label', 1)
        content = doc.text
        raw_markdown_parts.append(content)

        # Markdown 내용에서 요소 타입 추출
        parsed_elements = extract_elements_from_markdown(content, page_num)
        elements.extend(parsed_elements)

    return ParsedDocument(
        file_path=str(file_path),
        external_id=external_id,
        elements=elements,
        raw_markdown="\n\n".join(raw_markdown_parts)
    )


def extract_elements_from_markdown(markdown_content: str, page_number: int) -> List[ParsedElement]:
    """
    Markdown에서 요소별로 분리 (테이블, 텍스트, 헤딩 등)
    """
    elements = []
    lines = markdown_content.split('\n')

    current_text = []
    current_table = []
    in_table = False

    for line in lines:
        # 헤딩 감지 (# 으로 시작)
        if line.startswith('#'):
            # 이전 텍스트 저장
            if current_text:
                text = '\n'.join(current_text).strip()
                if text:
                    elements.append(ParsedElement(
                        content=text,
                        element_type='text',
                        page_number=page_number
                    ))
                current_text = []

            # 헤딩 레벨 추출
            level = len(line) - len(line.lstrip('#'))
            heading_text = line.lstrip('#').strip()
            if heading_text:
                elements.append(ParsedElement(
                    content=heading_text,
                    element_type='heading',
                    page_number=page_number,
                    metadata={'level': level}
                ))

        # 테이블 감지 (| 로 시작)
        elif line.strip().startswith('|'):
            if not in_table:
                # 이전 텍스트 저장
                if current_text:
                    text = '\n'.join(current_text).strip()
                    if text:
                        elements.append(ParsedElement(
                            content=text,
                            element_type='text',
                            page_number=page_number
                        ))
                    current_text = []
                in_table = True

            current_table.append(line)

        else:
            # 테이블 종료
            if in_table:
                table_content = '\n'.join(current_table)
                elements.append(ParsedElement(
                    content=table_content,
                    element_type='table',
                    page_number=page_number,
                    metadata={'row_count': len(current_table)}
                ))
                current_table = []
                in_table = False

            # 일반 텍스트
            if line.strip():
                current_text.append(line)

    # 마지막 요소 처리
    if in_table and current_table:
        table_content = '\n'.join(current_table)
        elements.append(ParsedElement(
            content=table_content,
            element_type='table',
            page_number=page_number,
            metadata={'row_count': len(current_table)}
        ))
    elif current_text:
        text = '\n'.join(current_text).strip()
        if text:
            elements.append(ParsedElement(
                content=text,
                element_type='text',
                page_number=page_number
            ))

    return elements


def parse_pdf_batch(pdf_list: List[tuple], max_workers: int = 4) -> List[ParsedDocument]:
    """
    여러 PDF를 배치로 파싱 (LlamaParse는 동시 요청을 지원하므로 비동기 방식이 더 효율적일 수 있음)
    """
    # LlamaParse는 파일 경로 리스트를 받아 한 번에 처리 가능
    # 여기서는 기존 파이프라인 구조를 유지하기 위해 동시성 처리를 유지
    from concurrent.futures import ThreadPoolExecutor, as_completed

    results = []
    failed = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(parse_pdf, path, ext_id): (ext_id, path)
            for ext_id, path in pdf_list
        }

        for future in as_completed(futures):
            ext_id, path = futures[future]
            try:
                result = future.result()
                results.append(result)
                print(f"파싱 완료: {ext_id}")
            except Exception as e:
                failed.append((ext_id, str(e)))
                print(f"파싱 실패: {ext_id} - {e}")

    if failed:
        print(f"\n파싱 실패 목록 ({len(failed)}개):")
        for ext_id, error in failed:
            print(f"  {ext_id}: {error}")

    return results


if __name__ == "__main__":
    # 테스트
    from pdf_filter import get_all_announcement_pdfs

    pdfs = get_all_announcement_pdfs()

    # 첫 번째 PDF로 테스트
    if pdfs['lease']:
        ext_id, path = pdfs['lease'][0]
        print(f"\n테스트 파싱: {ext_id}")
        print(f"파일: {path.name}")

        result = parse_pdf(path, ext_id)
        print(f"\n추출된 요소 수: {len(result.elements)}")

        for i, elem in enumerate(result.elements[:5]):
            print(f"\n--- 요소 {i+1} ({elem.element_type}, 페이지 {elem.page_number}) ---")
            preview = elem.content[:300] + "..." if len(elem.content) > 300 else elem.content
            print(preview)
