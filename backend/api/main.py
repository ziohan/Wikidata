from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.functions.services.new_query import router as new_query_router
from backend.functions.services.query_generated import router as query_generated_router
from backend.functions.services.last_queries import router as last_queries_router
from backend.functions.services.search_entities import router as search_entities_router
from backend.functions.services.top_queries import router as top_queries_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(new_query_router)
app.include_router(query_generated_router)
app.include_router(last_queries_router)
app.include_router(search_entities_router)
app.include_router(top_queries_router)