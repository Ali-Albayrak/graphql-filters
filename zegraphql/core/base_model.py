import uuid
from uuid import UUID
from datetime import datetime
from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column

from .db_config import Base
from .depends import current_user_uuid, current_user_tenant


class BaseModel(Base):
    """
    Default fileds for any table 
    """
    __abstract__ = True

    id: Mapped[UUID] = mapped_column(primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[UUID] = mapped_column(default=current_user_tenant)
    created_by: Mapped[UUID] = mapped_column(default=current_user_uuid)
    updated_by: Mapped[UUID] = mapped_column(default=current_user_uuid, onupdate=current_user_uuid)
    created_on: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_on: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())


    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class TenantModel(Base):
    __tablename__ = 'tenants'
    __table_args__ = {'schema': 'zekoder_zeauth'}

    id: Mapped[UUID] = mapped_column(primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(nullable=False)
    created_on: Mapped[datetime] = mapped_column(default=datetime.now())
    updated_on: Mapped[datetime] = mapped_column(default=datetime.now(), onupdate=datetime.now())


class UserModel(Base):
    __tablename__ = 'users'
    __table_args__ = {'schema': 'zekoder_zeauth'}

    id: Mapped[UUID] = mapped_column(primary_key=True, default=lambda: str(uuid.uuid4()))
    email: Mapped[str] = mapped_column(nullable=False)
    created_on: Mapped[datetime] = mapped_column(default=datetime.now())
    updated_on: Mapped[datetime] = mapped_column(default=datetime.now(), onupdate=datetime.now())

class FilesModel(Base):
    __tablename__ = 'files'
    __table_args__ = {'schema': 'public'}

    id: Mapped[UUID] = mapped_column(primary_key=True, default=lambda: str(uuid.uuid4()))
    minio_address: Mapped[str] = mapped_column(nullable=False)
    minio_thumbnail_address: Mapped[str] = mapped_column()
    width: Mapped[int] = mapped_column()
    height: Mapped[int] = mapped_column()
    tn_width: Mapped[int] = mapped_column()
    tn_height: Mapped[int] = mapped_column()
    file_size: Mapped[int] = mapped_column(nullable=False)
    file_name: Mapped[str] = mapped_column(nullable=False)
    file_extension: Mapped[str] = mapped_column()
    file_description: Mapped[str] = mapped_column()
    created_on: Mapped[datetime] = mapped_column(default=datetime.now())
    updated_on: Mapped[datetime] = mapped_column(default=datetime.now(), onupdate=datetime.now())
