from strawberry.tools import merge_types





from .documents import DocumentQuery
from .industries import IndustryQuery
from .summary_tasks import SummaryTaskQuery

Query = merge_types('Query', (
    DocumentQuery,
    IndustryQuery,
    SummaryTaskQuery,
))