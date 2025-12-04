from llama_cloud_services import LlamaParse
import os
from typing import List, Dict, Any
from langchain_text_splitters import RecursiveCharacterTextSplitter
import re


class ZipFitParser():
    
    def __init__(self):
        self.multiple_spaces_regex = re.compile(r'\s{2,}')
        # 임베딩용: 마크다운 테이블 헤더 구분선 감지용 정규식 (여러 열 포함 패턴까지 허용)
        self.table_divider_regex_embedding = re.compile(r'^\s*\|\s*(:?-+\s*\|\s*)+:?\s*$')
        print('v20251204.24')

    # --- 텍스트 정규화 헬퍼 함수 ---

    def _normalize_for_embedding(self, text: str, is_table: bool = False) -> str:
        # 임베딩용 텍스트 정규화

        if is_table:
            # --- 임베딩용 (테이블 전용) ---
            # 1) 줄 단위로 나눈 뒤, 구분선(divider) 행 제거
            lines = text.split('\n')
            filtered_lines = []
            for line in lines:
                if self.table_divider_regex_embedding.match(line):
                    continue
                stripped = line.strip()
                if stripped == '|':
                    continue
                filtered_lines.append(line)

            text = '\n'.join(filtered_lines)

            # 2) 테이블은 행 경계를 유지하기 위해 줄바꿈을 특수 토큰으로 치환
            text = text.replace('\n', ' <ROW> ')

            # 3) 연속된 공백을 하나로 줄임
            text = self.multiple_spaces_regex.sub(' ', text)

            return text.strip()

        # --- 임베딩용 (일반 텍스트) ---
        # 1. 문단 구분(두 줄바꿈 이상)은 특수 토큰으로 치환해 경계 정보 유지
        text = re.sub(r'\n{2,}', ' <P> ', text)

        # 2. 나머지 줄바꿈은 공백으로 치환
        text = text.replace('\n', ' ')

        # 3. 연속된 공백을 하나로 줄임
        text = self.multiple_spaces_regex.sub(' ', text)

        return text.strip()

    def _normalize_for_llm_context(self, text: str, is_table: bool = False) -> str:
        # LLM 컨텍스트용 텍스트 정규화: 문단/테이블 구조 보존에 중점
        
        if is_table:
            # --- LLM 제공용 (테이블 전용) ---
            # 테이블은 행/열 구조와 마크다운 형태가 중요하므로,
            # 구분선(divider)을 포함한 전체 표 구조를 최대한 그대로 보존하되
            # 각 셀 내부의 과도한 공백만 정리
            lines = text.split('\n')
            normalized_lines = []
            for line in lines:
                leading_spaces = re.match(r'^(\s*)', line).group(1)
                content = line[len(leading_spaces):]
                content = self.multiple_spaces_regex.sub(' ', content)
                normalized_lines.append(f"{leading_spaces}{content}")

            text = '\n'.join(normalized_lines)
            return text.strip()

        # --- LLM 제공용 (일반 텍스트) ---
        # 1. 3개 이상의 연속 줄바꿈을 2개로 제한 (문단 구조 보존)
        text = re.sub(r'\n{3,}', '\n\n', text)

        # 2. 각 줄 내부의 연속된 공백만 하나로 줄이고, 선행 공백(인덴트)은 유지
        lines = text.split('\n')
        normalized_lines = []
        for line in lines:
            leading_spaces = re.match(r'^(\s*)', line).group(1)
            content = line[len(leading_spaces):]
            content = self.multiple_spaces_regex.sub(' ', content)
            normalized_lines.append(f"{leading_spaces}{content}")

        text = '\n'.join(normalized_lines)
        
        return text.strip()


    # --- 1. 구조 추출 함수 ---
    
    def extract_elements_from_markdown(self, markdown_content: str, page_number: int) -> List[Dict[str, Any]]:
        elements: List[Dict[str, Any]] = []
        lines = markdown_content.split('\n')

        current_text: List[str] = []
        current_table: List[str] = []
        in_table = False
        
        last_heading_content: str = ""
        last_heading_level: int = 0
        

        def _save_text_element(text_list: List[str]):
            if not text_list:
                return
            
            text = '\n'.join(text_list).strip()
            if not text:
                return

            metadata = {
                'page_number': page_number,
                'heading_context': last_heading_content,
                'heading_level': last_heading_level
            }
            
            elements.append({
                'content': text,
                'element_type': 'text',
                'page_number': page_number,
                'metadata': metadata
            })
            text_list.clear()

        def _save_table_element():
            if not current_table:
                return

            cleaned_table_rows: List[str] = []
            actual_data_rows: List[str] = []
            
            for row in current_table:
                if row.strip() == '|':
                    continue
                
                cleaned_table_rows.append(row)
                actual_data_rows.append(row)

            table_content = '\n'.join(cleaned_table_rows)

            if table_content:
                metadata = {
                    'page_number': page_number,
                    'row_count': len(actual_data_rows),
                    'heading_context': last_heading_content,
                    'heading_level': last_heading_level
                }
                
                elements.append({
                    'content': table_content,
                    'element_type': 'table',
                    'page_number': page_number,
                    'metadata': metadata
                })
            
            current_table.clear()

        blank_line_count = 0

        for line in lines:
            stripped_line = line.strip()

            # 공백 줄 카운트 (테이블 내부 연속 공백 허용을 위해 사용)
            if stripped_line == '':
                blank_line_count += 1
            else:
                blank_line_count = 0

            # 1. 헤딩 처리
            if stripped_line.startswith('#'):
                _save_text_element(current_text)
                if in_table:
                    _save_table_element()
                    in_table = False
                
                match = re.match(r'(#+)\s*(.*)', stripped_line)
                if match:
                    hashes, heading_text = match.groups()
                    level = len(hashes)
                    
                    if heading_text:
                        last_heading_content = heading_text
                        last_heading_level = level
                        
                        elements.append({
                            'content': heading_text,
                            'element_type': 'heading',
                            'page_number': page_number,
                            'metadata': {'page_number': page_number, 'level': level}
                        })

            # 2. 테이블 처리 (파이프 시작 + 너무 짧지 않은 행만 테이블 후보로)
            elif stripped_line.startswith('|') and len(stripped_line) > 3:
                if not in_table:
                    _save_text_element(current_text)
                    in_table = True
                current_table.append(line)

            # 3. 기타 텍스트 / 공백 줄 처리
            else:
                # 테이블 내부에서 완전히 비어 있는 줄이 1~2개 나오는 것은 허용
                if in_table and blank_line_count >= 2:
                    _save_table_element()
                    in_table = False

                if not in_table and stripped_line:
                    current_text.append(line)

        if in_table:
            _save_table_element()
        elif current_text:
            _save_text_element(current_text)

        return elements
    
    # --- 2. 청킹 및 최종 정규화 함수 ---

    def chunk(self, elements, chunk_size: int=400, chunk_overlap: int=40) -> List[Dict[str, Any]]:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, 
            chunk_overlap=chunk_overlap,
        )
        new_elements = []

        for element in elements:
            element_type = element.get('element_type','')
            page_number = element.get('page_number', 0)
            metadata = element.get('metadata', None)
            content = element.get('content', '')

            # 요소 타입에 따라 테이블 여부를 가장 먼저 결정
            is_table = (element_type == 'table')

            # 1. 헤딩 요소 처리 (항상 일반 텍스트로 간주)
            if element_type == 'heading':
                normalized_content = self._normalize_for_embedding(content, is_table=False)
                new_elements.append({
                    'content': normalized_content,          
                    'origin_content': normalized_content,
                    'element_type': element_type,
                    'page_number': page_number,
                    'metadata': metadata,
                })
                continue

            # 2. 내용 길이가 Chunk Size보다 큰 경우에만 분할 수행
            if len(content) > splitter._chunk_size:
                chunks = splitter.split_text(content)
                
                # A. LLM 컨텍스트용 원본 정규화 (테이블 포함)
                normalized_origin_content = self._normalize_for_llm_context(content, is_table=is_table)
                
                for chunk_content in chunks:
                    # B. 임베딩용 청크 정규화 
                    normalized_chunk_content = self._normalize_for_embedding(chunk_content, is_table=is_table)
                        
                    new_elements.append({
                        'content': normalized_chunk_content,
                        'origin_content': normalized_origin_content, 
                        'element_type': element_type,
                        'page_number': page_number,
                        'metadata': metadata,
                    })
            
            # 3. 분할되지 않는 요소 (Chunk Size보다 작거나 같음)
            else:
                # 임베딩용과 LLM 제공용을 각각 용도에 맞게 정규화
                normalized_content = self._normalize_for_embedding(content, is_table=is_table)
                normalized_origin_content = self._normalize_for_llm_context(content, is_table=is_table)
                new_elements.append({
                    'content': normalized_content, 
                    'origin_content': normalized_origin_content, 
                    'element_type': element_type,
                    'page_number': page_number,
                    'metadata': metadata,
                })
        
        return new_elements

    # --- 3. 파일 파싱 함수 ---
    
    def get_llama_parsed_docs(self, file_path: str) -> List[Dict[str, Any]]:
        lp_api_key = os.getenv("LLAMA_CLOUD_API_KEY")
        parser = LlamaParse(
            api_key=lp_api_key,
            verbose=True,
            result_type="markdown",
            language="ko",
        )
        docs_llama_parsed = parser.load_data(file_path)
    
        elements = []

        for idx, doc in enumerate(docs_llama_parsed):
            page_num = idx + 1
            content = doc.text

            parsed_elements = self.extract_elements_from_markdown(content, page_num)
            elements.extend(parsed_elements)

        return self.chunk(elements)
"""
    def get_llama_parsed_docs(self, file_path: str):
        print("v20251204.01")
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

        # # docs_llama_parsed를 JSON 파일로 저장
        # import json
        # from datetime import datetime
        
        # # 파일명 생성 (원본 파일명 기반)
        # base_name = os.path.splitext(os.path.basename(file_path))[0]
        # timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # # docs_llama_parsed 저장
        # docs_output_filename = f"{base_name}_llama_parsed_{timestamp}.json"
        # docs_output_path = os.path.join(os.path.dirname(__file__), docs_output_filename)
        
        # # Document 객체를 딕셔너리로 변환하여 저장
        # docs_serializable = []
        # for doc in docs_llama_parsed:
        #     docs_serializable.append({
        #         'text': doc.text,
        #         'metadata': doc.metadata,
        #         'id_': doc.id_,
        #     })
        
        # with open(docs_output_path, 'w', encoding='utf-8') as f:
        #     json.dump(docs_serializable, f, ensure_ascii=False, indent=2)
        
        # print(f"LlamaParse docs saved to: {docs_output_path}")
        # print(f"Total pages parsed: {len(docs_llama_parsed)}")

        for idx, doc in enumerate(docs_llama_parsed):
            # page_num = doc.metadata.get('page_label', idx + 1)
            page_num = idx + 1
            content = doc.text
            raw_markdown_parts.append(content)

            # Markdown 내용에서 요소 타입 추출
            parsed_elements = self.extract_elements_from_markdown(content, page_num)
            elements.extend(parsed_elements)

        # # elements를 JSON 파일로 저장
        # import json
        # from datetime import datetime
        
        # # 파일명 생성 (원본 파일명 기반)
        # base_name = os.path.splitext(os.path.basename(file_path))[0]
        # timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # output_filename = f"{base_name}_elements_{timestamp}.json"
        
        # # 현재 스크립트 디렉토리에 저장
        # output_path = os.path.join(os.path.dirname(__file__), output_filename)
        
        # with open(output_path, 'w', encoding='utf-8') as f:
        #     json.dump(elements, f, ensure_ascii=False, indent=2)
        
        # print(f"Elements saved to: {output_path}")
        # print(f"Total elements extracted: {len(elements)}")
        
        return self.chunk(elements)

    
    """