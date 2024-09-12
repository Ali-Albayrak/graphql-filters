import os
import enum
import uuid
import datetime
import importlib

from fastapi import HTTPException
from sqlalchemy import DATETIME, String, ForeignKey
from sqlalchemy import DATE, Column, Text, String, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import select
from core.base_model import BaseModel
from core.manager import Manager
from core.logger import log
from core.custom_exceptions import TriggerException










class DocumentModel(BaseModel):
    __tablename__ = 'documents'
    __table_args__ = {'schema': os.environ.get('DEFAULT_SCHEMA', 'public')}

    name: Mapped[str] = mapped_column(Text, nullable=False, default=None)
    report_source: Mapped[str] = mapped_column(Text, nullable=False, default=None)
    release_date: Mapped[datetime.date] = mapped_column(DATE, nullable=False, default=None)
    expiry_date: Mapped[datetime.date] = mapped_column(DATE, nullable=True, default=None)


    industry_document = mapped_column(UUID(as_uuid=True), ForeignKey(os.environ.get('DEFAULT_SCHEMA', 'public') + ".industries.id"))
    industry_document__details = relationship("IndustryModel", foreign_keys=[industry_document], back_populates='industry_document', lazy='selectin')
    category: Mapped[str] = mapped_column(Text, nullable=False, default=None)
    tags: Mapped[str] = mapped_column(Text, nullable=True, default=None)

    original_pdf: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("public.files.id"))
    status: Mapped[str] = mapped_column(Text, nullable=True, default=None)

    @classmethod
    def objects(cls, session):
        return Manager(cls, session)





class DocumentsAccess:
    related_access_roles = ['cybernetic-karari-documents-list', 'cybernetic-karari-documents-tenant-list', 'cybernetic-karari-documents-root-list', 'cybernetic-karari-industries-list', 'cybernetic-karari-industries-tenant-list', 'cybernetic-karari-industries-root-list']

    @classmethod
    def list_roles(cls):
        list_roles = ['cybernetic-karari-documents-list', 'cybernetic-karari-documents-tenant-list', 'cybernetic-karari-documents-root-list']
        return list(set(list_roles + cls.related_access_roles))

    @classmethod
    def create_roles(cls):
        create_roles = ['cybernetic-karari-documents-create', 'cybernetic-karari-documents-tenant-create', 'cybernetic-karari-documents-root-create']
        return create_roles + cls.related_access_roles

    @classmethod
    def update_roles(cls):
        update_roles = ['cybernetic-karari-documents-update', 'cybernetic-karari-documents-tenant-update', 'cybernetic-karari-documents-root-update']
        return update_roles + cls.related_access_roles

    @classmethod
    def delete_roles(cls):
        delete_roles = ['cybernetic-karari-documents-delete', 'cybernetic-karari-documents-tenant-delete', 'cybernetic-karari-documents-root-delete']
        return delete_roles + cls.related_access_roles