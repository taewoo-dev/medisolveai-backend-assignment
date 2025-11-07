"""비동기 데이터베이스 연결 관리"""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from ..configs.settings import settings

# 비동기 엔진 생성
_async_engine = create_async_engine(
    settings.database_url,
    echo=settings.is_local,
)

# 세션 팩토리 생성
_AsyncSessionFactory = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    bind=_async_engine,
)


def get_async_session() -> AsyncSession:
    """비동기 세션 생성"""
    return _AsyncSessionFactory()


# FastAPI 의존성 주입용 별칭
get_db_session = get_async_session
