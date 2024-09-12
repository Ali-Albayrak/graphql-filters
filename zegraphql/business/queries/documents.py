import strawberry
from strawberry.permission import PermissionExtension
from fastapi import HTTPException
from business.types import DocumentType
from business.db_models.documents_model import DocumentModel, DocumentsAccess
from core.constants import AppConstants as AC
from core.depends import GraphQLContext
from core.auth import Protect
from core import log

@strawberry.type
class DocumentQuery:
    @strawberry.field(extensions=[PermissionExtension(permissions=[Protect(DocumentsAccess.list_roles())])])
    async def get_document(self, id: strawberry.ID, info: strawberry.Info[GraphQLContext]) -> DocumentType:
        db = info.context.db
        try:
            obj = DocumentModel.objects(db)
            result = await obj.get(id=id)
            return result
        except Exception as e:
            log.debug(AC.ERROR_TEMPLATE.format(f"get_document with id {id}", type(e), str(e)))
            raise HTTPException(500, f"failed to fetch document with id <{id}>")

    @strawberry.field(extensions=[PermissionExtension(permissions=[Protect(DocumentsAccess.list_roles())])])
    async def list_documents(self, info: strawberry.Info[GraphQLContext]) -> list[DocumentType]:
        db = info.context.db
        try:
            obj = DocumentModel.objects(db)
            result = await obj.all()
            return result
        except Exception as e:
            log.debug(AC.ERROR_TEMPLATE.format(f"list_documents", type(e), str(e)))
            raise HTTPException(500, f"failed to fetch documents")