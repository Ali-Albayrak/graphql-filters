import strawberry
from strawberry.permission import PermissionExtension
from fastapi import HTTPException
from business.types import SummaryTaskType
from business.db_models.summary_tasks_model import SummaryTaskModel, SummaryTasksAccess
from core.constants import AppConstants as AC
from core.depends import GraphQLContext
from core.auth import Protect
from core import log

@strawberry.type
class SummaryTaskQuery:
    @strawberry.field(extensions=[PermissionExtension(permissions=[Protect(SummaryTasksAccess.list_roles())])])
    async def get_summary_task(self, id: strawberry.ID, info: strawberry.Info[GraphQLContext]) -> SummaryTaskType:
        db = info.context.db
        try:
            obj = SummaryTaskModel.objects(db)
            result = await obj.get(id=id)
            return result
        except Exception as e:
            log.debug(AC.ERROR_TEMPLATE.format(f"get_summary_task with id {id}", type(e), str(e)))
            raise HTTPException(500, f"failed to fetch summary_task with id <{id}>")

    @strawberry.field(extensions=[PermissionExtension(permissions=[Protect(SummaryTasksAccess.list_roles())])])
    async def list_summary_tasks(self, info: strawberry.Info[GraphQLContext]) -> list[SummaryTaskType]:
        db = info.context.db
        try:
            obj = SummaryTaskModel.objects(db)
            result = await obj.all()
            return result
        except Exception as e:
            log.debug(AC.ERROR_TEMPLATE.format(f"list_summary_tasks", type(e), str(e)))
            raise HTTPException(500, f"failed to fetch summary_tasks")