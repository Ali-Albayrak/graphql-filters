import os
import enum
import uuid
import datetime

from fastapi import HTTPException
from sqlalchemy import DATETIME, String, ForeignKey
from sqlalchemy import DATE, Column, Text, ARRAY
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import select
from core.base_model import BaseModel
from core.manager import Manager
from core.logger import log
from core.custom_exceptions import TriggerException










class SummaryTaskModel(BaseModel):
    __tablename__ = 'summary_tasks'
    __table_args__ = {'schema': os.environ.get('DEFAULT_SCHEMA', 'public')}

    status: Mapped[str] = mapped_column(Text, nullable=False, default=None)
    questions: Mapped[list[str]] = mapped_column(ARRAY(Text), nullable=False, default=None)
    min_max: Mapped[str] = mapped_column(Text, nullable=False, default=None)
    word_count: Mapped[str] = mapped_column(Text, nullable=False, default=None)
    source: Mapped[str] = mapped_column(Text, nullable=True, default=None)
    industry: Mapped[list[str]] = mapped_column(ARRAY(Text), nullable=True, default=None)
    category: Mapped[list[str]] = mapped_column(ARRAY(Text), nullable=False, default=None)
    tags: Mapped[list[str]] = mapped_column(ARRAY(Text), nullable=True, default=None)
    release_date: Mapped[datetime.date] = mapped_column(DATE, nullable=True, default=None)
    expiry_date: Mapped[datetime.date] = mapped_column(DATE, nullable=True, default=None)
    html: Mapped[str] = mapped_column(Text, nullable=True, default=None)

    pdf: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("public.files.id"))
    name: Mapped[str] = mapped_column(Text, nullable=True, default=None)

    @classmethod
    def objects(cls, session):
        return Manager(cls, session)





class SummaryTasksAccess:
    related_access_roles = ['cybernetic-karari-summary_tasks-list', 'cybernetic-karari-summary_tasks-tenant-list', 'cybernetic-karari-summary_tasks-root-list']

    @classmethod
    def list_roles(cls):
        list_roles = ['cybernetic-karari-summary_tasks-list', 'cybernetic-karari-summary_tasks-tenant-list', 'cybernetic-karari-summary_tasks-root-list']
        return list(set(list_roles + cls.related_access_roles))

    @classmethod
    def create_roles(cls):
        create_roles = ['cybernetic-karari-summary_tasks-create', 'cybernetic-karari-summary_tasks-tenant-create', 'cybernetic-karari-summary_tasks-root-create']
        return create_roles + cls.related_access_roles

    @classmethod
    def update_roles(cls):
        update_roles = ['cybernetic-karari-summary_tasks-update', 'cybernetic-karari-summary_tasks-tenant-update', 'cybernetic-karari-summary_tasks-root-update']
        return update_roles + cls.related_access_roles

    @classmethod
    def delete_roles(cls):
        delete_roles = ['cybernetic-karari-summary_tasks-delete', 'cybernetic-karari-summary_tasks-tenant-delete', 'cybernetic-karari-summary_tasks-root-delete']
        return delete_roles + cls.related_access_roles