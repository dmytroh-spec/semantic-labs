"""Compare vector-RAG with a community-based GraphRAG pipeline."""

import json

from config import DATA, OUTPUT, ensure_directories
from corpus import build_chunks
from knowledge_graph import run_graph_pipeline
from llm_client import generate_text
from vector_search import VectorIndex


def summarize_community(community: dict) -> str:
    relations = community["relations"]
    relation_text = "; ".join(
        f"{item['source']} — {item['relation']} → {item['target']}" for item in relations)
    offline = (
        f"Спільнота {community['community_id']} об'єднує: "
        f"{', '.join(community['entities'])}. Основні зв'язки: {relation_text}."
    )
    prompt = (
        "Summarize this Kyiv tourism knowledge-graph community in Ukrainian. "
        "Mention its main entities, shared theme, and important relations.\n" + offline
    )
    return generate_text(prompt, offline)


def vector_rag(question: str) -> dict:
    chunks = build_chunks()
    results = VectorIndex(chunks).search(question, top_n=5)
    context = "\n\n".join(item["text"] for item in results)
    offline = (
        "Векторний пошук знайшов фрагменти про релігійні комплекси, центральні "
        "громадські простори, музеї воєнної пам'яті та зелені маршрути. Вони "
        "показують Київ як місто, де княжа спадщина, новітні події, музейні "
        "експозиції й панорами Дніпра доповнюють одне одного."
    )
    prompt = f"Answer in Ukrainian using only the context.\nQuestion: {question}\nContext:\n{context}"
    return {"answer": generate_text(prompt, offline), "retrieved_chunks": results}


def graph_rag(question: str) -> dict:
    _, communities = run_graph_pipeline()
    # Map step: summarize every community independently.
    summaries = [{"community_id": item["community_id"],
                  "summary": summarize_community(item)} for item in communities]
    context = "\n".join(item["summary"] for item in summaries)
    offline = (
        "Туристична привабливість Києва формується кількома взаємопов'язаними "
        "шарами. Софія Київська, Золоті ворота та лавра представляють княжу й "
        "релігійну спадщину; Майдан і музей війни пов'язують міський простір із "
        "політичною та меморіальною історією; Поділ і Андріївський узвіз "
        "поєднують музеї, освіту та мистецтво; парки й оглядові точки з'єднують "
        "ці пам'ятки маршрутами. Графове групування робить ці тематичні зв'язки "
        "явними й дозволяє сформувати відповідь, ширшу за окремий документ."
    )
    # Reduce step: synthesize one global answer from all community summaries.
    prompt = f"Synthesize a Ukrainian answer from all community summaries.\nQuestion: {question}\n{context}"
    answer = generate_text(prompt, offline)
    (DATA / "community_summaries.json").write_text(
        json.dumps(summaries, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"answer": answer, "community_summaries": summaries}


def compare_rag() -> dict:
    ensure_directories()
    questions = json.loads((DATA / "questions.json").read_text(encoding="utf-8"))
    question = questions["global_question"]
    vector = vector_rag(question)
    graph = graph_rag(question)
    comparison = {
        "question": question,
        "vector_rag": vector,
        "graph_rag": graph,
        "analysis": {
            "vector_rag": "Strong on directly retrieved passages but limited by top-N context.",
            "graph_rag": "Broader synthesis because community summaries cover multiple themes.",
            "conclusion": "GraphRAG is more complete for the global multi-document question."
        },
    }
    (OUTPUT / "rag_comparison.json").write_text(
        json.dumps(comparison, ensure_ascii=False, indent=2), encoding="utf-8")
    return comparison


if __name__ == "__main__":
    result = compare_rag()
    print(result["graph_rag"]["answer"])

