from django.db import models
# from django.contrib.postgres.fields import ArrayField
from pgvector.django import VectorField


class TSVectorField(models.Field):
    """PostgreSQL tsvector field for full-text search."""

    description = "PostgreSQL tsvector"

    def db_type(self, connection):
        return "tsvector"


# Create your models here.

# class Post(models.Model):
#     title= models.CharField(max_length=100) # char또는 varchar로 만들어짐
#     content= models.TextField()
#     created_at= models.DateTimeField()
#     updated_at= models.DateTimeField()

#     def __str__(self):
#         return self.title

class AnncLhTemp(models.Model):
    """ LH 공고 크롤링 배치 임시 테이블 (ANNC_LH_TEMP) """

    temp_id = models.BigAutoField(primary_key=True, verbose_name="장고를 위한 SEQ")

    # 1. 키 필드
    batch_id = models.UUIDField(
        # max_length=50, 
        null=False, 
        # primary_key=True,
        verbose_name="배치 ID"
    )
    batch_seq = models.IntegerField(
        null=False, 
        verbose_name="배치 SEQ"
    )

    # 2. 데이터 필드
    annc_title = models.CharField(max_length=200, verbose_name="공고 제목")
    annc_url = models.TextField(verbose_name="공고 URL")
    batch_start_dttm = models.DateTimeField(verbose_name="배치 등록 시간")
    batch_end_dttm = models.DateTimeField(null=True, blank=True, verbose_name="배치 완료 시간")
    batch_status = models.CharField(max_length=10, verbose_name="배치 상태")
    annc_type = models.CharField(max_length=50, verbose_name="공고 유형")
    annc_dtl_type = models.CharField(max_length=20, verbose_name="공고 유형 상세")
    annc_region = models.CharField(max_length=50, verbose_name="지역")
    annc_pblsh_dt = models.CharField(max_length=50, verbose_name="게시일")
    annc_deadline_dt = models.CharField(max_length=50, verbose_name="마감일")
    annc_status = models.CharField(max_length=20, verbose_name="공고 상태")
    lh_pan_id = models.CharField(max_length=30, verbose_name="공고 식별 ID")
    lh_ais_tp_cd = models.CharField(max_length=10, verbose_name="공고 유형 코드")
    lh_upp_ais_tp_cd = models.CharField(max_length=10, verbose_name="상위 공고 유형 코드")
    lh_ccr_cnnt_sys_ds_cd = models.CharField(max_length=10, verbose_name="연계 시스템 구분 코드")
    lh_ls_sst = models.CharField(max_length=50, verbose_name="목록 상의 상태/순서")

    class Meta:
        # unique_together = ('batch_id', 'batch_seq')
        verbose_name = "LH 크롤링 배치 임시"
        verbose_name_plural = "LH 크롤링 배치 임시 기록"
        db_table = 'annc_lh_temp'
    
class AnncAll(models.Model):
    """ 공고 전체 정보를 저장하는 테이블 (ANNC_ALL) """
    
    # 기본 키 (BIGSERIAL)
    annc_id = models.BigAutoField(primary_key=True, verbose_name="공고 ID")    
    # 데이터 필드
    annc_title = models.CharField(max_length=200, verbose_name="공고 제목")
    annc_url = models.URLField(
        max_length=2000,
        verbose_name="공고 URL",
        unique=True
        ) # Django URLField 사용, TEXT 대체
    created_dttm = models.DateTimeField(verbose_name="공고 생성 일자", auto_now_add=True)
    updated_dttm = models.DateTimeField(verbose_name="공고 수정 일자", auto_now=True)
    corp_cd = models.CharField(max_length=10, verbose_name="공사 코드")
    annc_type = models.CharField(max_length=50, verbose_name="공고 유형")
    annc_dtl_type = models.CharField(max_length=20, verbose_name="공고 유형 상세")
    annc_region = models.CharField(max_length=50, verbose_name="지역")
    annc_pblsh_dt = models.CharField(max_length=50, verbose_name="게시일")
    annc_deadline_dt = models.CharField(max_length=50, verbose_name="마감일")
    annc_status = models.CharField(max_length=20, verbose_name="공고 상태")
    service_status = models.CharField(max_length=20, verbose_name="서비스 상태")
    
    class Meta:
        verbose_name = "공고 전체 테이블"
        verbose_name_plural = "공고 전체 테이블"
        db_table = 'annc_all' # 데이터베이스 테이블명을 명시적으로 지정

class AnncFiles(models.Model):
    """ 공고 파일 정보를 저장하는 테이블 (ANNC_FILES) """

    # 기본 키 (BIGSERIAL)
    file_id = models.BigAutoField(primary_key=True, verbose_name="공고 파일 ID")
    
    # 외래 키 (BIGSERIAL) - AnncAll을 참조
    annc_id = models.ForeignKey(
        'AnncAll', 
        on_delete=models.CASCADE, 
        verbose_name="공고 ID",
        # db_column을 명시하여 실제 DB 칼럼명을 유지할 수 있지만, Django ORM은 필드명(annc_id)을 사용합니다.
        db_column='annc_id'
    ) 

    # 데이터 필드
    file_name = models.CharField(max_length=500, verbose_name="공고 파일명")
    file_type = models.CharField(max_length=10, verbose_name="공고 파일 유형")
    file_path = models.CharField(max_length=2000, verbose_name="공고 파일 경로", null=True)
    file_ext = models.CharField(max_length=10, verbose_name="공고 파일 확장자")
    file_size = models.IntegerField(verbose_name="공고 파일 사이즈")

    class Meta:
        verbose_name = "공고 파일"
        verbose_name_plural = "공고 파일"
        db_table = 'annc_files'
        # 복합 기본 키 역할: FILE_ID와 ANNC_ID의 조합이 고유해야 함 (스키마 기준)
        # Django는 단일 PK를 선호하므로, 고유성 제약만 추가합니다.
        unique_together = ('file_id', 'annc_id')


class DocChunks(models.Model):
    """ 공고 파일 청크 벡터 테이블 (DOC_CHUNKS) """

    # 기본 키 (BIGSERIAL)
    chunk_id = models.BigAutoField(primary_key=True, verbose_name="청크 ID")
    
    # 외래 키 (BIGSERIAL)
    file_id = models.ForeignKey(
        'AnncFiles', 
        on_delete=models.CASCADE, 
        verbose_name="공고 파일 ID",
        db_column='file_id'
    )
    annc_id = models.ForeignKey(
        'AnncAll', 
        on_delete=models.CASCADE, 
        verbose_name="공고 ID",
        db_column='annc_id'
    )

    # 데이터 필드
    chunk_type = models.CharField(max_length=20, verbose_name="청크 타입")
    chunk_text = models.TextField(verbose_name="청크 텍스트")
    page_num = models.SmallIntegerField(verbose_name="페이지 번호")
    
    # 임베딩 벡터 (VECTOR(1536) 매핑)
    # PostgreSQL에서 벡터 타입을 직접 지원하는 라이브러리(예: pgvector)를 사용하지 않을 경우
    # 임시로 JSONField나 CharField를 사용하거나, ArrayField(IntegerField/FloatField)를 사용합니다.
    # 여기서는 JSONField를 사용하며, 실제 운영시 ArrayField(FloatField)나 pgvector 사용이 권장됨.
    embedding = VectorField(dimensions=1536, verbose_name="임베딩 벡터")
    
    # 메타데이터 (JSONB 매핑)
    metadata = models.JSONField(verbose_name="메타데이터") 

    # 전문검색용 tsvector 컬럼
    fts_vector = TSVectorField(null=True, blank=True, verbose_name="전문 검색 벡터")
    
    class Meta:
        verbose_name = "공고 파일 청크 벡터"
        verbose_name_plural = "공고 파일 청크 벡터"
        db_table = 'doc_chunks'
        # 복합 기본 키 역할
        unique_together = ('chunk_id', 'file_id', 'annc_id')


class ChatHistory(models.Model):
    """
    익명 사용자와 챗봇 간의 대화 기록을 저장하는 모델입니다.
    세션 키를 사용하여 익명 사용자의 대화 세션을 추적합니다.
    """
    # 1. 메시지 유형 선택지 정의
    MESSAGE_CHOICES = [
        ('system', 'System Message'),
        ('user', 'User Message'),
        ('bot', 'Bot Response'),
    ]

    # 기본 키 (BIGSERIAL)
    id = models.BigAutoField(primary_key=True, verbose_name="기록 ID")

    # 세션 ID (익명 사용자 식별자 - CharField로 설정)
    session_key = models.UUIDField(
        # max_length=40,
        null=False,
        verbose_name="세션 키"
    )
    
    # 세션 내 메시지 순서 (Integer, 1부터 시작하여 메시지 순서 보장)
    sequence = models.IntegerField(
        null=False,
        verbose_name="메시지 순서"
    )

    # 메시지 내용 (TEXT)
    message = models.TextField(
        verbose_name="메시지 내용"
    )

    max_length = max(len(item[0]) for item in MESSAGE_CHOICES)

    # 메시지 유형 (user 또는 bot)
    message_type = models.CharField(
        max_length=max_length,
        choices=MESSAGE_CHOICES,
        null=False,
        verbose_name="메시지 유형"
    )

    # 생성 시간 (TIMESTAMPZ, 레코드 생성 시 자동 기록)
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="생성일시"
    )
    
    class Meta:
        verbose_name = "챗봇 대화 기록"
        verbose_name_plural = "챗봇 대화 기록"
        # 데이터베이스 테이블명 지정
        db_table = 'chat_history'
        # 세션 내에서 순서(sequence)가 고유해야 함 (복합 고유성)
        unique_together = ('session_key', 'sequence')
        # 세션 키와 순서대로 정렬 (대화 흐름)
        ordering = ['session_key', 'sequence'] 

    def __str__(self):
        return f'[{self.created_at.strftime("%Y-%m-%d %H:%M")}] [{self.message_type}] {self.message[:30]}...'