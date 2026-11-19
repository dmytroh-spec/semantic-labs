"""FastAPI entry point for the Kyiv Semantic Guide."""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from app.repository import get_attraction, list_attractions, list_routes, load_data

app = FastAPI(
    title="Kyiv Semantic Guide API",
    description="Каталог туристичних місць Києва на основі RDF і семантичного графа.",
    version="1.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["GET"],
    allow_headers=["*"],
)
@app.get("/api/health", tags=["system"])
def health() -> dict:
    data = load_data()
    return {
        "status": "ok",
        "schema_version": data["schema_version"],
        "attractions": len(data["attractions"]),
        "facts": len(data["knowledge_facts"]),
    }


@app.get("/api/categories", tags=["catalog"])
def categories() -> list[dict]:
    return load_data()["categories"]


@app.get("/api/attractions", tags=["catalog"])
def attractions(
    q: str | None = Query(default=None, min_length=2),
    category: str | None = None,
    free_only: bool = False,
    min_rating: float | None = Query(default=None, ge=0, le=5),
) -> dict:
    items = list_attractions(q, category, free_only, min_rating)
    return {"count": len(items), "items": items}


@app.get("/api/attractions/{attraction_id}", tags=["catalog"])
def attraction(attraction_id: str) -> dict:
    item = get_attraction(attraction_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Tourist attraction not found")
    return item


@app.get("/api/routes", tags=["routes"])
def routes() -> dict:
    items = list_routes()
    return {"count": len(items), "items": items}
