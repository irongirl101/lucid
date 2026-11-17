from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
from fastapi import FastAPI, Query, HTTPException
from app.search_engine import SearchEngine
from app.sample_data import SAMPLE_DOCUMENTS
from app.ranking import combine_scores

app = FastAPI(
    title="Distributed Search Engine",
    description="Node 4 - Search Service and UI",
    version="1.0.0"
)

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


@app.get("/ui", response_class=HTMLResponse)
def search_ui(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )

# Initialize the search engine
search_engine = SearchEngine(SAMPLE_DOCUMENTS)


@app.get("/")
def home():
    return {
        "message": "Welcome to the Distributed Search Engine",
        "node": "Node 4",
        "service": "Search Service",
        "status": "running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "node": 4
    }


@app.get("/search")
def search(
    q: str = Query(..., min_length=1, description="Search query"),
    top_k: int = Query(10, ge=1, le=50)
):
    try:
        bm25_results = search_engine.search(q, top_k=top_k)

        final_results = combine_scores(
            bm25_results,
            bm25_weight=0.7,
            pagerank_weight=0.3
        )

        return {
            "query": q,
            "total_results": len(final_results),
            "results": final_results
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error)
        )
