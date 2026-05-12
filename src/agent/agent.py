
from google.adk import Agent

from .tools import search_company_knowledge

root_agent = Agent(
    model="gemini-3.1-flash-lite",
    name="knowledge_assistant",
    description="Enterprise knowledge assistant that helps employees find information.",
    instruction="""You are a helpful enterprise knowledge assistant.

    Your role:
    - Answer questions about company policies, procedures, and knowledge base
    - ALWAYS use the search_company_knowledge tool before answering policy questions
    - Be concise and accurate
    - Cite the source document when using retrieved information
    - If the search returns no results, say you don't have that information
    """,
    tools=[search_company_knowledge],
)