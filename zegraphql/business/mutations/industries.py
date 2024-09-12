from typing import List
import strawberry
from strawberry.permission import PermissionExtension
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from business.types import IndustryType, CreateIndustryInput, UpdateIndustryInput
from business.db_models.industries_model import IndustryModel, IndustriesAccess
from core.constants import AppConstants as AC
from core.depends import GraphQLContext
from core.auth import Protect
from core import log

@strawberry.type
class IndustryMutation:
    @strawberry.mutation(extensions=[PermissionExtension(permissions=[Protect(IndustriesAccess.create_roles())])])
    async def create_industry(self, input: CreateIndustryInput, info: strawberry.Info[GraphQLContext]) -> IndustryType:
        db = info.context.db
        try:
            obj = IndustryModel.objects(db)
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
            new_industry = await obj.create(**kwargs)
            return new_industry
        except HTTPException as e:
            raise e
        except IntegrityError as e:
            raise HTTPException(422, e.orig.args[-1])
        except Exception as e:
            log.debug(AC.ERROR_TEMPLATE.format(f"create_industry", type(e), str(e)))
            raise HTTPException(500, f"creation of new industry failed")

    @strawberry.mutation(extensions=[PermissionExtension(permissions=[Protect(IndustriesAccess.update_roles())])])
    async def update_industry(self, industry_id: strawberry.ID, input: UpdateIndustryInput, info: strawberry.Info[GraphQLContext]) -> IndustryType:
        db = info.context.db
        try:
            obj = IndustryModel.objects(db)
            data = await obj.get(id=industry_id)
            if not data:
                raise HTTPException(404, f"<{industry_id}> record not found in industries")
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
            result = await obj.update(industry_id, **kwargs)
            return result
        except HTTPException as e:
            raise e
        except IntegrityError as e:
            raise HTTPException(422, e.orig.args[-1])
        except Exception as e:
            log.debug(AC.ERROR_TEMPLATE.format(f"update_industry with id <{industry_id}>", type(e), str(e)))
            raise HTTPException(500, f"failed updating record with id <{industry_id}> in industries")

    @strawberry.mutation(extensions=[PermissionExtension(permissions=[Protect(IndustriesAccess.delete_roles())])])
    async def delete_industry(self, industry_id: strawberry.ID, info: strawberry.Info[GraphQLContext]) -> bool:
        db = info.context.db
        try:
            obj = IndustryModel.objects(db)
            old_data = await obj.get(id=industry_id)
            if not old_data:
                raise HTTPException(404, f"<{industry_id}> record not found in industries")
            kwargs = {
                "model_data": {},
                "signal_data": {
                    "jwt": info.context.jwt,
                    "new_data": {},
                    "old_data": old_data.to_dict() if old_data else {},
                    "well_known_urls": {"zeauth": AC.ZEAUTH_BASE_URL, "self": str(info.context.request.base_url)}
                }
            }
            result = await obj.delete(industry_id, **kwargs)
            return True
        except Exception as e:
            log.debug(AC.ERROR_TEMPLATE.format("delete_industry", type(e), str(e)))
            raise HTTPException(500, f"failed deleting industry with id <{industry_id}>")

    @strawberry.mutation(extensions=[PermissionExtension(permissions=[Protect(IndustriesAccess.update_roles() + IndustriesAccess.create_roles())])])
    async def upsert_multiple_industries(self, inputs: List[CreateIndustryInput], info: strawberry.Info[GraphQLContext]) -> List[IndustryType]:
        db = info.context.db
        try:
            new_items, errors_info = [], []
            for industry_index, industry in enumerate(inputs):
                try:
                    obj = IndustryModel.objects(db)
                    new_data = industry.to_dict(exclude_null=True)
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
                        new_industry = await obj.create(**kwargs)
                        new_items.append(new_industry)
                except HTTPException as e:
                    errors_info.append({"index": industry_index, "errors": e.detail})
            return new_items
        except HTTPException as e:
            raise e
        except IntegrityError as e:
            raise HTTPException(422, e.orig.args[-1])
        except Exception as e:
            log.debug(AC.ERROR_TEMPLATE.format("upsert_multiple_industries", type(e), str(e)))
            raise HTTPException(500, f"upsert multiple industries failed")

    @strawberry.mutation(extensions=[PermissionExtension(permissions=[Protect(IndustriesAccess.delete_roles())])])
    async def delete_multiple_industries(self, industry_ids: List[strawberry.ID], info: strawberry.Info[GraphQLContext]) -> bool:
        db = info.context.db
        try:
            obj = IndustryModel.objects(db)
            old_data = await obj.get_multiple(industry_ids)
            if not old_data:
                raise HTTPException(404, f"<{industry_ids}> records not found in industries")
            kwargs = {
                "model_data": {},
                "signal_data": {
                    "jwt": info.context.jwt,
                    "new_data": {},
                    "old_data": old_data,
                    "well_known_urls": {"zeauth": AC.ZEAUTH_BASE_URL, "self": str(info.context.request.base_url)}
                }
            }
            result = await obj.delete_multiple(industry_ids, **kwargs)
            return True
        except Exception as e:
            log.debug(AC.ERROR_TEMPLATE.format("delete_multiple_industries", type(e), str(e)))
            raise HTTPException(500, f"failed deleting industries_ids <{industry_ids}>")
