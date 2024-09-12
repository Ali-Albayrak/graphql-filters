from typing import List
import strawberry
from strawberry.permission import PermissionExtension
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from business.types import SummaryTaskType, CreateSummaryTaskInput, UpdateSummaryTaskInput
from business.db_models.summary_tasks_model import SummaryTaskModel, SummaryTasksAccess
from core.constants import AppConstants as AC
from core.depends import GraphQLContext
from core.auth import Protect
from core import log

@strawberry.type
class SummaryTaskMutation:
    @strawberry.mutation(extensions=[PermissionExtension(permissions=[Protect(SummaryTasksAccess.create_roles())])])
    async def create_summary_task(self, input: CreateSummaryTaskInput, info: strawberry.Info[GraphQLContext]) -> SummaryTaskType:
        db = info.context.db
        try:
            obj = SummaryTaskModel.objects(db)
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
            new_summary_task = await obj.create(**kwargs)
            return new_summary_task
        except HTTPException as e:
            raise e
        except IntegrityError as e:
            raise HTTPException(422, e.orig.args[-1])
        except Exception as e:
            log.debug(AC.ERROR_TEMPLATE.format(f"create_summary_task", type(e), str(e)))
            raise HTTPException(500, f"creation of new summary_task failed")

    @strawberry.mutation(extensions=[PermissionExtension(permissions=[Protect(SummaryTasksAccess.update_roles())])])
    async def update_summary_task(self, summary_task_id: strawberry.ID, input: UpdateSummaryTaskInput, info: strawberry.Info[GraphQLContext]) -> SummaryTaskType:
        db = info.context.db
        try:
            obj = SummaryTaskModel.objects(db)
            data = await obj.get(id=summary_task_id)
            if not data:
                raise HTTPException(404, f"<{summary_task_id}> record not found in summary_tasks")
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
            result = await obj.update(summary_task_id, **kwargs)
            return result
        except HTTPException as e:
            raise e
        except IntegrityError as e:
            raise HTTPException(422, e.orig.args[-1])
        except Exception as e:
            log.debug(AC.ERROR_TEMPLATE.format(f"update_summary_task with id <{summary_task_id}>", type(e), str(e)))
            raise HTTPException(500, f"failed updating record with id <{summary_task_id}> in summary_tasks")

    @strawberry.mutation(extensions=[PermissionExtension(permissions=[Protect(SummaryTasksAccess.delete_roles())])])
    async def delete_summary_task(self, summary_task_id: strawberry.ID, info: strawberry.Info[GraphQLContext]) -> bool:
        db = info.context.db
        try:
            obj = SummaryTaskModel.objects(db)
            old_data = await obj.get(id=summary_task_id)
            if not old_data:
                raise HTTPException(404, f"<{summary_task_id}> record not found in summary_tasks")
            kwargs = {
                "model_data": {},
                "signal_data": {
                    "jwt": info.context.jwt,
                    "new_data": {},
                    "old_data": old_data.to_dict() if old_data else {},
                    "well_known_urls": {"zeauth": AC.ZEAUTH_BASE_URL, "self": str(info.context.request.base_url)}
                }
            }
            result = await obj.delete(summary_task_id, **kwargs)
            return True
        except Exception as e:
            log.debug(AC.ERROR_TEMPLATE.format("delete_summary_task", type(e), str(e)))
            raise HTTPException(500, f"failed deleting summary_task with id <{summary_task_id}>")

    @strawberry.mutation(extensions=[PermissionExtension(permissions=[Protect(SummaryTasksAccess.update_roles() + SummaryTasksAccess.create_roles())])])
    async def upsert_multiple_summary_tasks(self, inputs: List[CreateSummaryTaskInput], info: strawberry.Info[GraphQLContext]) -> List[SummaryTaskType]:
        db = info.context.db
        try:
            new_items, errors_info = [], []
            for summary_task_index, summary_task in enumerate(inputs):
                try:
                    obj = SummaryTaskModel.objects(db)
                    new_data = summary_task.to_dict(exclude_null=True)
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
                        new_summary_task = await obj.create(**kwargs)
                        new_items.append(new_summary_task)
                except HTTPException as e:
                    errors_info.append({"index": summary_task_index, "errors": e.detail})
            return new_items
        except HTTPException as e:
            raise e
        except IntegrityError as e:
            raise HTTPException(422, e.orig.args[-1])
        except Exception as e:
            log.debug(AC.ERROR_TEMPLATE.format("upsert_multiple_summary_tasks", type(e), str(e)))
            raise HTTPException(500, f"upsert multiple summary_tasks failed")

    @strawberry.mutation(extensions=[PermissionExtension(permissions=[Protect(SummaryTasksAccess.delete_roles())])])
    async def delete_multiple_summary_tasks(self, summary_task_ids: List[strawberry.ID], info: strawberry.Info[GraphQLContext]) -> bool:
        db = info.context.db
        try:
            obj = SummaryTaskModel.objects(db)
            old_data = await obj.get_multiple(summary_task_ids)
            if not old_data:
                raise HTTPException(404, f"<{summary_task_ids}> records not found in summary_tasks")
            kwargs = {
                "model_data": {},
                "signal_data": {
                    "jwt": info.context.jwt,
                    "new_data": {},
                    "old_data": old_data,
                    "well_known_urls": {"zeauth": AC.ZEAUTH_BASE_URL, "self": str(info.context.request.base_url)}
                }
            }
            result = await obj.delete_multiple(summary_task_ids, **kwargs)
            return True
        except Exception as e:
            log.debug(AC.ERROR_TEMPLATE.format("delete_multiple_summary_tasks", type(e), str(e)))
            raise HTTPException(500, f"failed deleting summary_tasks_ids <{summary_task_ids}>")
