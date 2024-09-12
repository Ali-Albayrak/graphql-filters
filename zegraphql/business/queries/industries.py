import strawberry
from strawberry.permission import PermissionExtension
from fastapi import HTTPException
from business.types import IndustryType
from business.db_models.industries_model import IndustryModel, IndustriesAccess
from core.constants import AppConstants as AC
from core.depends import GraphQLContext
from core.auth import Protect
from core import log

@strawberry.type
class IndustryQuery:
    @strawberry.field(extensions=[PermissionExtension(permissions=[Protect(IndustriesAccess.list_roles())])])
    async def get_industry(self, id: strawberry.ID, info: strawberry.Info[GraphQLContext]) -> IndustryType:
        db = info.context.db
        try:
            obj = IndustryModel.objects(db)
            result = await obj.get(id=id)
            return result
        except Exception as e:
            log.debug(AC.ERROR_TEMPLATE.format(f"get_industry with id {id}", type(e), str(e)))
            raise HTTPException(500, f"failed to fetch industry with id <{id}>")

    @strawberry.field(extensions=[PermissionExtension(permissions=[Protect(IndustriesAccess.list_roles())])])
    async def list_industries(self, info: strawberry.Info[GraphQLContext]) -> list[IndustryType]:
        db = info.context.db
        try:
            obj = IndustryModel.objects(db)
            result = await obj.all()
            return result
        except Exception as e:
            log.debug(AC.ERROR_TEMPLATE.format(f"list_industries", type(e), str(e)))
            raise HTTPException(500, f"failed to fetch industries")