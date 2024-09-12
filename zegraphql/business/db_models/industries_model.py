import os
import enum
import uuid
import datetime
import importlib

from fastapi import HTTPException
from sqlalchemy import DATETIME, String, ForeignKey
from sqlalchemy import Column, String, ForeignKey, Text
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import select
from core.base_model import BaseModel
from core.manager import Manager
from core.logger import log
from core.custom_exceptions import TriggerException










class IndustryModel(BaseModel):
    __tablename__ = 'industries'
    __table_args__ = {'schema': os.environ.get('DEFAULT_SCHEMA', 'public')}


    from business.db_models.documents_model import DocumentModel
    industry_document = relationship('DocumentModel', foreign_keys=[DocumentModel.industry_document], back_populates='industry_document__details', lazy='selectin')
    industry_name: Mapped[str] = mapped_column(Text, nullable=True, default=None)

    @classmethod
    def objects(cls, session):
        return Manager(cls, session)





class IndustriesAccess:
    related_access_roles = ['cybernetic-karari-industries-list', 'cybernetic-karari-industries-tenant-list', 'cybernetic-karari-industries-root-list', 'cybernetic-karari-documents-list', 'cybernetic-karari-documents-tenant-list', 'cybernetic-karari-documents-root-list']

    @classmethod
    def list_roles(cls):
        list_roles = ['cybernetic-karari-industries-list', 'cybernetic-karari-industries-tenant-list', 'cybernetic-karari-industries-root-list']
        return list(set(list_roles + cls.related_access_roles))

    @classmethod
    def create_roles(cls):
        create_roles = ['cybernetic-karari-industries-create', 'cybernetic-karari-industries-tenant-create', 'cybernetic-karari-industries-root-create']
        return create_roles + cls.related_access_roles

    @classmethod
    def update_roles(cls):
        update_roles = ['cybernetic-karari-industries-update', 'cybernetic-karari-industries-tenant-update', 'cybernetic-karari-industries-root-update']
        return update_roles + cls.related_access_roles

    @classmethod
    def delete_roles(cls):
        delete_roles = ['cybernetic-karari-industries-delete', 'cybernetic-karari-industries-tenant-delete', 'cybernetic-karari-industries-root-delete']
        return delete_roles + cls.related_access_roles