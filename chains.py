from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableParallel

from prompt import PROMPT, EXAMPLE_PROMPT


def _format_docs_with_sources(docs):
    return "\n\n".join(
        EXAMPLE_PROMPT.format(
            page_content=doc.page_content,
            source=doc.metadata.get('source', 'unknown'),
        )
        for doc in docs
    )


def _extract_sources(docs):
    return list({doc.metadata.get('source', 'unknown') for doc in docs})


def RetrievalQAWithSourcesChain(llm, vector_store, prompt=PROMPT):
    retriever = vector_store.as_retriever()

    setup = RunnableParallel(docs=retriever, question=RunnablePassthrough())

    return setup | RunnableParallel(
        answer=(
            {"summaries": lambda x: _format_docs_with_sources(x["docs"]), "question": lambda x: x["question"]}
            | prompt
            | llm
            | StrOutputParser()
        ),
        sources=lambda x: _extract_sources(x["docs"]),
    )
