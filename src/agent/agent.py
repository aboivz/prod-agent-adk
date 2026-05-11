from google.adk import Agent

root_agent = Agent(
    model="gemini-3.1-flash-lite",
    name="knowledge_assistant",
    description="Enterprise knowledge assistant that helps employees find information.",
    instruction="""You are a helpful enterprise knowledge assistant.

    Your role:
    - Answer questions about company policies, procedures, and knowledge base
    - Be concise and accurate
    - If you don't know something, say so clearly
    - Always cite the source when using retrieved information
    """,
)