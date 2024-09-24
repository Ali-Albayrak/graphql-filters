import uuid
import strawberry
from strawberry.permission import PermissionExtension
from fastapi import HTTPException
from business.types import DocumentType, ReadDocuments
from business.db_models.documents_model import DocumentModel, DocumentsAccess
from core.constants import AppConstants as AC
from core.depends import GraphQLContext
from core.filter_type import QuerySchema
from core.auth import Protect
from core import log

@strawberry.type
class DocumentQuery:
    @strawberry.field(extensions=[PermissionExtension(permissions=[Protect(DocumentsAccess.list_roles())])])
    async def get_document(self, id: strawberry.ID, info: strawberry.Info[GraphQLContext]) -> DocumentType:
        db = info.context.db
        try:
            obj = DocumentModel.objects(db)
            result = await obj.get(id=uuid.UUID(id))
            return result
        except Exception as e:
            log.debug(AC.ERROR_TEMPLATE.format(f"get_document with id {id}", type(e), str(e)))
            raise HTTPException(500, f"failed to fetch document with id <{id}>")

    @strawberry.field(extensions=[PermissionExtension(permissions=[Protect(DocumentsAccess.list_roles())])])
    async def list_documents(self, info: strawberry.Info[GraphQLContext], q:QuerySchema) -> ReadDocuments:
        db = info.context.db
        try:
            obj = DocumentModel.objects(db)
            offset = (q.page-1)*q.page_size if q.page_size > 0 else 0
            result = await obj.all(offset=offset, limit=q.page_size, sort=q.sort, filters=q.filters)
            # log.debug(f"Result: {result[0].id}, Count: {len(result)}")
            # return ReadDocuments(documents=result, page_size=q.limit, next_page=q.skip+q.limit if len(result) == q.limit else None)
            return ReadDocuments(documents=result, page_size=q.page_size, next_page=q.page+1 if len(result) == q.page_size else None)
        except Exception as e:
            log.debug(AC.ERROR_TEMPLATE.format(f"list_documents", type(e), str(e)))
            raise HTTPException(500, f"failed to fetch documents")