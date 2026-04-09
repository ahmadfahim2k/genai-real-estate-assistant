from langchain.prompts import PromptTemplate
from langchain.chains.qa_with_sources.stuff_prompt import template

new_template = "YOUR PROMPT" + template
PROMPT = PromptTemplate(template=new_template, input_variables=["summaries", "question"])

EXAMPLE_PROMPT = PromptTemplate(
    template="Content: {page_content}\nSource: {source}",
    input_variables=["page_content", "source"],
)