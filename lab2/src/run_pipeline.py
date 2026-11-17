"""Run the complete Lab 2 pipeline in dependency order."""

from config import EMBEDDING_BACKEND, LLM_BACKEND
from corpus import build_chunks
from extract_facts import extract_facts
from knowledge_graph import run_graph_pipeline
from rag import compare_rag
from validate_lab2 import main as validate
from vector_search import run_search_demo


def main() -> None:
    # Stages run in dependency order because later artifacts consume outputs
    # created by extraction, retrieval, and graph construction.
    chunks = build_chunks()
    facts = extract_facts()
    search = run_search_demo()
    graph, communities = run_graph_pipeline()
    compare_rag()
    validate()
    print("\nPipeline complete")
    print(f"LLM backend: {LLM_BACKEND}; embedding backend: {EMBEDDING_BACKEND}")
    print(f"Chunks: {len(chunks)}; facts: {len(facts.facts)}")
    print(f"Graph: {graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges")
    print(f"Communities: {len(communities)}; search queries: {len(search)}")


if __name__ == "__main__":
    main()

