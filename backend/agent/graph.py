# agent/graph.py
# This file builds the LangGraph AI agent
# Think of it as hiring a smart manager who:
# 1. Reads the user's message
# 2. Decides which tool to use
# 3. Calls the tool
# 4. Returns the result back to the user

from langgraph.prebuilt import create_react_agent
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os

# Import all 5 tools we just defined
from agent.tools import all_tools

load_dotenv()

# Initialize the Groq LLM
# This is the AI model that reads messages and decides what to do
# temperature=0 means the AI gives consistent, predictable responses
# (temperature closer to 1 = more creative but less reliable)
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY")
)

# System prompt = instructions we give the AI about its role
# This is like an employee handbook — the AI reads this before every conversation
SYSTEM_PROMPT = """You are an AI assistant for a pharmaceutical CRM system.
You help field representatives log and manage their interactions with Healthcare Professionals (HCPs).

You have access to these tools:
1. log_interaction - Record a new meeting with a doctor
2. edit_interaction - Update an existing interaction record
3. get_hcp_profile - Look up a doctor's profile and history
4. summarize_interaction - Generate a summary of interaction notes
5. schedule_followup - Set a follow-up date with a doctor

Always be professional and precise. When logging interactions, extract:
- Doctor's name
- Date of interaction
- Products discussed
- Key notes
- Next steps

If the user's message is missing required information, ask for it politely.
Always confirm when an action has been completed successfully.
"""

# create_react_agent() builds a ReAct agent
# ReAct = Reasoning + Acting
# The agent REASONS about what to do, then ACTS by calling a tool
# Then it REASONS again about whether the result is good enough
# This loop continues until it has a final answer
def create_agent():
    agent = create_react_agent(
        model=llm,
        tools=all_tools,
        prompt=SYSTEM_PROMPT
    )
    return agent

# We create one agent instance that gets reused across requests
# Creating it once is faster than creating it fresh for every message
agent_executor = create_agent()


# This is the main function FastAPI will call when a chat message arrives
# messages = the full conversation history (list of user/assistant messages)
async def run_agent(messages: list) -> str:
    try:
        # LangGraph needs messages as (role, content) tuples
        # not as plain dictionaries
        # Think of it like: instead of {role: "user", content: "hi"}
        # LangGraph wants: ("user", "hi")
        formatted_messages = [
            (msg["role"], msg["content"]) 
            for msg in messages
        ]

        result = await agent_executor.ainvoke({
            "messages": formatted_messages
        })

        final_message = result["messages"][-1]
        return final_message.content

    except Exception as e:
        return f"Agent error: {str(e)}"