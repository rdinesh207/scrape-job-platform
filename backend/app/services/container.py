from functools import lru_cache

from app.services.embedding_service import EmbeddingService
from app.services.graphs import WorkflowService
from app.services.llm_service import LLMService
from app.services.scrapegraph_service import ScrapeGraphService
from app.services.supabase_service import SupabaseService


@lru_cache
def get_workflow_service() -> WorkflowService:
    llm = LLMService()
    scraper = ScrapeGraphService(llm)
    embeddings = EmbeddingService()
    db = SupabaseService()
    return WorkflowService(
        llm_service=llm,
        scrape_service=scraper,
        embedding_service=embeddings,
        supabase_service=db,
    )
