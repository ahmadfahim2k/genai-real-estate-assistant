from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableParallel


_prompt = ChatPromptTemplate.from_template("""
Answer the question based on the context below.
Always cite the sources you used.

Context:
{context}

Question: {question}
""")


def _format_docs_with_sources(docs):
    return "\n\n".join(
        f"Source: {doc.metadata.get('source', 'unknown')}\n{doc.page_content}"
        for doc in docs
    )


def _extract_sources(docs):
    return list({doc.metadata.get('source', 'unknown') for doc in docs})


def RetrievalQAWithSourcesChain(llm, vector_store):
    retriever = vector_store.as_retriever()

    setup = RunnableParallel(docs=retriever, question=RunnablePassthrough())

    return setup | RunnableParallel(
        answer=(
            {"context": lambda x: _format_docs_with_sources(x["docs"]), "question": lambda x: x["question"]}
            | _prompt
            | llm
            | StrOutputParser()
        ),
        sources=lambda x: _extract_sources(x["docs"]),
    )
