import datetime
from typing import Optional, List
import strawberry
import enum



class BaseType:
    def to_dict(self, exclude: Optional[List[str]] = None, exclude_null: bool = False):
        return {k: v for k, v in self.__dict__.items() if not k.startswith("_") and not callable(v) and (not exclude or k not in exclude) and (not exclude_null or v is not None)}


@strawberry.enum
class DocumentCategoryEnum(str, enum.Enum):
    hr = "hr"
    it = "it"
    marketing = "marketing"
    market_research = "market_research"
    finance = "finance"
    sales = "sales"
    startegy = "startegy"
    plan = "plan"
    operations = "operations"
    research_development = "research_development"
    product_management = "product_management"
    service_management = "service_management"
    customer_service = "customer_service"
    risk_management = "risk_management"
    audit = "audit"
    investment = "investment"

@strawberry.enum
class DocumentStatusEnum(str, enum.Enum):
    new = "new"
    in_progress = "in_progress"
    completed = "completed"
    failed = "failed"
    update = "update"
    delete = "delete"

@strawberry.type
class DocumentType(BaseType):
    id: Optional[strawberry.ID] = None
    created_on: datetime.datetime
    updated_on: datetime.datetime
    created_by: Optional[strawberry.ID] = None
    updated_by: Optional[strawberry.ID] = None
    tenant_id: Optional[strawberry.ID]  = None
    name: str
    report_source: str
    release_date: datetime.date
    expiry_date: Optional[datetime.date] = None
    industry_document: Optional[strawberry.ID] = None
    industry_document__details: Optional["IndustryType"] = None
    category: DocumentCategoryEnum
    tags: Optional[str] = None
    original_pdf: strawberry.ID
    status: Optional[DocumentStatusEnum] = None

@strawberry.input
class CreateDocumentInput(BaseType):
    id: Optional[strawberry.ID] = None
    name: str
    report_source: str
    release_date: datetime.date
    expiry_date: Optional[datetime.date] = None
    industry_document: Optional[strawberry.ID] = None
    category: DocumentCategoryEnum
    tags: Optional[str] = None
    original_pdf: strawberry.ID
    status: Optional[DocumentStatusEnum] = None

@strawberry.input
class UpdateDocumentInput(BaseType):
    name: Optional[str] = None
    report_source: Optional[str] = None
    release_date: Optional[datetime.date] = None
    expiry_date: Optional[datetime.date] = None
    industry_document: Optional[strawberry.ID] = None
    category: Optional[DocumentCategoryEnum] = None
    tags: Optional[str] = None
    original_pdf: Optional[strawberry.ID] = None
    status: Optional[DocumentStatusEnum] = None

@strawberry.type
class IndustryType(BaseType):
    id: Optional[strawberry.ID] = None
    created_on: datetime.datetime
    updated_on: datetime.datetime
    created_by: Optional[strawberry.ID] = None
    updated_by: Optional[strawberry.ID] = None
    tenant_id: Optional[strawberry.ID]  = None
    industry_document: Optional[list["DocumentType"]] = None
    industry_name: Optional[str] = None

@strawberry.input
class CreateIndustryInput(BaseType):
    id: Optional[strawberry.ID] = None
    industry_name: Optional[str] = None

@strawberry.input
class UpdateIndustryInput(BaseType):
    industry_name: Optional[str] = None

@strawberry.enum
class SummaryTaskStatusEnum(str, enum.Enum):
    new = "new"
    in_progress = "in_progress"
    completed = "completed"
    failed = "failed"

@strawberry.type
class SummaryTaskType(BaseType):
    id: Optional[strawberry.ID] = None
    created_on: datetime.datetime
    updated_on: datetime.datetime
    created_by: Optional[strawberry.ID] = None
    updated_by: Optional[strawberry.ID] = None
    tenant_id: Optional[strawberry.ID]  = None
    status: SummaryTaskStatusEnum
    questions: List[str]
    min_max: str
    word_count: str
    source: Optional[str] = None
    industry: Optional[List[str]] = None
    category: List[str]
    tags: Optional[List[str]] = None
    release_date: Optional[datetime.date] = None
    expiry_date: Optional[datetime.date] = None
    html: Optional[str] = None
    pdf: Optional[strawberry.ID] = None
    name: Optional[str] = None

@strawberry.input
class CreateSummaryTaskInput(BaseType):
    id: Optional[strawberry.ID] = None
    status: SummaryTaskStatusEnum
    questions: List[str]
    min_max: str
    word_count: str
    source: Optional[str] = None
    industry: Optional[List[str]] = None
    category: List[str]
    tags: Optional[List[str]] = None
    release_date: Optional[datetime.date] = None
    expiry_date: Optional[datetime.date] = None
    html: Optional[str] = None
    pdf: Optional[strawberry.ID] = None
    name: Optional[str] = None

@strawberry.input
class UpdateSummaryTaskInput(BaseType):
    status: Optional[SummaryTaskStatusEnum] = None
    questions: Optional[List[str]] = None
    min_max: Optional[str] = None
    word_count: Optional[str] = None
    source: Optional[str] = None
    industry: Optional[List[str]] = None
    category: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    release_date: Optional[datetime.date] = None
    expiry_date: Optional[datetime.date] = None
    html: Optional[str] = None
    pdf: Optional[strawberry.ID] = None
    name: Optional[str] = None