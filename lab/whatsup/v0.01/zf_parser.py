from llama_cloud_services import LlamaParse
import os
from typing import List, Dict, Any
from langchain_text_splitters import RecursiveCharacterTextSplitter

class ZipFitParser():

    def __init__(self):
        pass

    def extract_elements_from_markdown(self, markdown_content: str, page_number: int) -> List[dict]:
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
                        elements.append({
                            'content': text,
                            'element_type': 'text',
                            'page_number': page_number
                        })
                    current_text = []

                # 헤딩 레벨 추출
                level = 0
                for char in line:
                    if char == '#':
                        level += 1
                    else:
                        break
                heading_text = line.lstrip('#').strip()
                if heading_text:
                    elements.append({
                        'content': heading_text,
                        'element_type': 'heading',
                        'page_number': page_number,
                        'metadata': {'level': level}
                    })

            # 테이블 감지 (| 로 시작)
            elif line.strip().startswith('|'):
                if not in_table:
                    # 이전 텍스트 저장
                    if current_text:
                        text = '\n'.join(current_text).strip()
                        if text:
                            elements.append({
                                'content': text,
                                'element_type': 'text',
                                'page_number': page_number
                            })
                        current_text = []
                    in_table = True

                current_table.append(line)

            else:
                # 테이블 종료
                if in_table:
                    # 테이블 구분선(---|---) 제외하고 카운트
                    actual_rows = [row for row in current_table if not all(c in '|-: ' for c in row.strip())]
                    table_content = '\n'.join(current_table)
                    elements.append({
                        'content': table_content,
                        'element_type': 'table',
                        'page_number': page_number,
                        'metadata': {'row_count': len(actual_rows)}
                    })
                    current_table = []
                    in_table = False

                # 일반 텍스트
                if line.strip():
                    current_text.append(line)

        # 마지막 요소 처리
        if in_table and current_table:
            # 테이블 구분선(---|---) 제외하고 카운트
            actual_rows = [row for row in current_table if not all(c in '|-: ' for c in row.strip())]
            table_content = '\n'.join(current_table)
            elements.append({
                'content': table_content,
                'element_type': 'table',
                'page_number': page_number,
                'metadata': {'row_count': len(actual_rows)}
            })
        elif current_text:
            text = '\n'.join(current_text).strip()
            if text:
                elements.append({
                    'content': text,
                    'element_type': 'text',
                    'page_number': page_number
                })

        return elements
    
    def chunk(self, elements, chunk_size: int=300, chunk_overlap: int=20):

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,        # 각 Chunk의 최대 문자 수 (기본값: 1000)
            chunk_overlap=chunk_overlap       # 인접한 텍스트 조각 간 겹치는 문자 수 (기본값: 200) 교집합? 목적 - 문맥유지, n-gram과 유사
            # seperators: 텍스트 분할 구분자 우선순위 (기본값: ['\n\n', '\n', ' ', '']) 빈값의 의미?
            # \n\n: 문단의 개행
            # \n: 줄바꿈
            # ' ': 공백문자
            # '': 빈문자열, ch 단위로 자름
        )
        new_elements = []
    
        for element in elements:

            element_type = element.get('element_type','')
            page_number = element.get('page_number','')
            metadata = element.get('metadata',None)
            content = element.get('content','')

            if len(content) > splitter._chunk_size:
                chunks = splitter.split_text(content)
                if element_type == "table":
                    new_elements += [{
                        'content': s.replace('\n', ' '),
                        'origin_content': content,
                        'element_type': element_type,
                        'page_number': page_number,
                        'metadata': metadata,
                    } for s in chunks]
                else:
                    new_elements += [{
                        'content': s.replace('\n', ' '),
                        'origin_content': s,
                        'element_type': element_type,
                        'page_number': page_number,
                        'metadata': metadata,
                    } for s in chunks]
            else:
                new_elements.append({
                    'content': content.replace('\n', ' '),
                    'origin_content': content,
                    'element_type': element_type,
                    'page_number': page_number,
                    'metadata': metadata,
                })
        
        return new_elements

    def get_llama_parsed_docs(self, file_path: str):
        """
        파일 경로로 llama parser를 호출하여 docs를 반환
        """
        # print("!")
        lp_api_key = os.getenv("LLAMA_CLOUD_API_KEY")
        parser = LlamaParse(
            api_key=lp_api_key,  # can also be set in your env as LLAMA_CLOUD_API_KEY
            # num_workers=4,       # if multiple files passed, split in `num_workers` API calls
            verbose=True,
            result_type="markdown",
            language="ko",       # optionally define a language, default=en
        )
        docs_llama_parsed = parser.load_data(file_path)
    
        elements = []
        raw_markdown_parts = []

        for idx, doc in enumerate(docs_llama_parsed):
            # page_num = doc.metadata.get('page_label', idx + 1)
            page_num = idx + 1
            content = doc.text
            raw_markdown_parts.append(content)

            # Markdown 내용에서 요소 타입 추출
            parsed_elements = self.extract_elements_from_markdown(content, page_num)
            elements.extend(parsed_elements)

        # print("프로세스 완료!")
        return self.chunk(elements)

    
    