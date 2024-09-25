from typing import List
import strawberry
from strawberry.permission import PermissionExtension
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from business.types import DocumentType, CreateDocumentInput, UpdateDocumentInput
from business.db_models.documents_model import DocumentModel, DocumentsAccess
from core.filter_type import FieldFilter, QueryOperator
from core.constants import AppConstants as AC
from core.depends import GraphQLContext
from core.auth import Protect
from core import log

@strawberry.type
class DocumentMutation:
    @strawberry.mutation(extensions=[PermissionExtension(permissions=[Protect(DocumentsAccess.create_roles())])])
    async def create_document(self, input: CreateDocumentInput, info: strawberry.Info[GraphQLContext]) -> DocumentType:
        db = info.context.db
        try:
            obj = DocumentModel.objects(db)
            new_data = input.to_dict()
            kwargs = {
                "model_data": new_data,
                "signal_data": {
                    "jwt": info.context.jwt,
                    "new_data": new_data,
                    "old_data": {},
                    "well_known_urls": {"zeauth": AC.ZEAUTH_BASE_URL, "self": str(info.context.request.base_url)}
                }
            }
            new_document = await obj.create(**kwargs)
            return new_document
        except HTTPException as e:
            raise e
        except IntegrityError as e:
            raise HTTPException(422, e.orig.args[-1])
        except Exception as e:
            log.debug(AC.ERROR_TEMPLATE.format(f"create_document", type(e), str(e)))
            raise HTTPException(500, f"creation of new document failed")

    @strawberry.mutation(extensions=[PermissionExtension(permissions=[Protect(DocumentsAccess.update_roles())])])
    async def update_document(self, document_id: strawberry.ID, input: UpdateDocumentInput, info: strawberry.Info[GraphQLContext]) -> DocumentType:
        db = info.context.db
        try:
            obj = DocumentModel.objects(db)
            data = await obj.get(id=document_id)
            if not data:
                raise HTTPException(404, f"<{document_id}> record not found in documents")
            new_data = input.to_dict(exclude_null=True)
            kwargs = {
                "model_data": new_data,
                "signal_data": {
                    "jwt": info.context.jwt,
                    "new_data": new_data,
                    "old_data": data.to_dict() if data else {},
                    "well_known_urls": {"zeauth": AC.ZEAUTH_BASE_URL, "self": str(info.context.request.base_url)}
                }
            }
            result = await obj.update(document_id, **kwargs)
            return result
        except HTTPException as e:
            raise e
        except IntegrityError as e:
            raise HTTPException(422, e.orig.args[-1])
        except Exception as e:
            log.debug(AC.ERROR_TEMPLATE.format(f"update_document with id <{document_id}>", type(e), str(e)))
            raise HTTPException(500, f"failed updating record with id <{document_id}> in documents")

    @strawberry.mutation(extensions=[PermissionExtension(permissions=[Protect(DocumentsAccess.delete_roles())])])
    async def delete_document(self, document_id: strawberry.ID, info: strawberry.Info[GraphQLContext]) -> bool:
        db = info.context.db
        try:
            obj = DocumentModel.objects(db)
            old_data = await obj.get(id=document_id)
            if not old_data:
                raise HTTPException(404, f"<{document_id}> record not found in documents")
            kwargs = {
                "model_data": {},
                "signal_data": {
                    "jwt": info.context.jwt,
                    "new_data": {},
                    "old_data": old_data.to_dict() if old_data else {},
                    "well_known_urls": {"zeauth": AC.ZEAUTH_BASE_URL, "self": str(info.context.request.base_url)}
                }
            }
            result = await obj.delete(document_id, **kwargs)
            return True
        except Exception as e:
            log.debug(AC.ERROR_TEMPLATE.format("delete_document", type(e), str(e)))
            raise HTTPException(500, f"failed deleting document with id <{document_id}>")

    @strawberry.mutation(extensions=[PermissionExtension(permissions=[Protect(DocumentsAccess.update_roles() + DocumentsAccess.create_roles())])])
    async def upsert_multiple_documents(self, inputs: List[CreateDocumentInput], info: strawberry.Info[GraphQLContext]) -> List[DocumentType]:
        db = info.context.db
        try:
            new_items, errors_info = [], []
            for document_index, document in enumerate(inputs):
                try:
                    obj = DocumentModel.objects(db)
                    new_data = document.to_dict(exclude_null=True)
                    data = await obj.get(id=new_data.get('id'))
                    kwargs = {
                        "model_data": new_data,
                        "signal_data": {
                            "jwt": info.context.jwt,
                            "new_data": new_data,
                            "old_data": {},
                            "well_known_urls": {"zeauth": AC.ZEAUTH_BASE_URL, "self": str(info.context.request.base_url)}
                        }
                    }
                    if data:
                        kwargs['signal_data']['old_data'] = data.to_dict() if data else {}
                        await obj.update(obj_id=new_data['id'], **kwargs)
                        new_items.append(data)
                    else:
                        new_document = await obj.create(**kwargs)
                        new_items.append(new_document)
                except HTTPException as e:
                    errors_info.append({"index": document_index, "errors": e.detail})
            return new_items
        except HTTPException as e:
            raise e
        except IntegrityError as e:
            raise HTTPException(422, e.orig.args[-1])
        except Exception as e:
            log.debug(AC.ERROR_TEMPLATE.format("upsert_multiple_documents", type(e), str(e)))
            raise HTTPException(500, f"upsert multiple documents failed")

    @strawberry.mutation(extensions=[PermissionExtension(permissions=[Protect(DocumentsAccess.delete_roles())])])
    async def delete_multiple_documents(self, document_ids: List[strawberry.ID], info: strawberry.Info[GraphQLContext]) -> bool:
        db = info.context.db
        try:
            obj = DocumentModel.objects(db)
            old_data = await obj.all(filters=[FieldFilter(field_path="id", operator=QueryOperator(in_=document_ids))])
            if not old_data:
                raise HTTPException(404, f"<{document_ids}> records not found in documents")
            kwargs = {
                "model_data": {},
                "signal_data": {
                    "jwt": info.context.jwt,
                    "new_data": {},
                    "old_data": old_data,
                    "well_known_urls": {"zeauth": AC.ZEAUTH_BASE_URL, "self": str(info.context.request.base_url)}
                }
            }
            result = await obj.delete_multiple(document_ids, **kwargs)
            return True
        except Exception as e:
            log.debug(AC.ERROR_TEMPLATE.format("delete_multiple_documents", type(e), str(e)))
            raise HTTPException(500, f"failed deleting documents_ids <{document_ids}>")
