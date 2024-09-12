from strawberry.tools import merge_types





from .documents import DocumentMutation
from .industries import IndustryMutation
from .summary_tasks import SummaryTaskMutation

Mutation = merge_types('Mutation', (
    DocumentMutation,
    IndustryMutation,
    SummaryTaskMutation,
))