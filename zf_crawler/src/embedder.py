"""임베딩 모듈 - OpenAI text-embedding-3-small"""
import os
from typing import List
from langchain_openai import OpenAIEmbeddings

_model = None


def get_model() -> OpenAIEmbeddings:
    """임베딩 모델 싱글톤"""
    global _model
    if _model is None:
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY 환경변수 필요")
        _model = OpenAIEmbeddings(model="text-embedding-3-small")
    return _model


def embed_text(text: str) -> List[float]:
    """단일 텍스트 임베딩"""
    return get_model().embed_query(text)


def embed_texts(texts: List[str], batch_size: int = 20) -> List[List[float]]:
    """배치 임베딩 (API 토큰 제한 고려하여 분할 처리)"""
    if not texts:
        return []

    model = get_model()
    all_embeddings = []

    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        embeddings = model.embed_documents(batch)
        all_embeddings.extend(embeddings)

    return all_embeddings


def embed_chunks(chunks: List, batch_size: int = 20) -> List:
    """Chunk 객체 리스트에 임베딩 추가 (배치 처리)"""
    if not chunks:
        return []
    texts = [c.text for c in chunks]
    embeddings = embed_texts(texts, batch_size=batch_size)
    for chunk, emb in zip(chunks, embeddings):
        chunk.embedding = emb
    return chunks
