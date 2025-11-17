"""
Minimal Reproducible Example: LangGraph + New Relic Integration

This demonstrates a simple LangGraph agent with optional New Relic monitoring.

Note: New Relic is initialized via environment variables set in deployment settings.
No direct initialization needed - the agent is activated automatically.
"""

import os
import sys
import asyncio

# ============================================================================
# NEW RELIC - Environment Variable Configuration
# ============================================================================
# New Relic initializes automatically from environment variables:
#   NEW_RELIC_LICENSE_KEY - Required for activation
#   NEW_RELIC_CONFIG_FILE - Path to config file
#   NEW_RELIC_ENVIRONMENT - Deployment environment
#
# No manual initialization is performed to avoid conflicts with LangGraph Platform's
# Uvicorn server management. The agent auto-initializes when these env vars are set.
# ============================================================================

# ============================================================================
# LANGGRAPH AGENT - Minimal Example
# ============================================================================

from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI


class State(TypedDict):
    """Simple state for our agent."""
    messages: Annotated[list, add_messages]


def chatbot(state: State):
    """
    Simple chatbot node that echoes back messages.
    In a real scenario, this would call an LLM.
    """
    messages = state["messages"]
    
    # Use ChatOpenAI if available, otherwise echo
    try:
        llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
        response = llm.invoke(messages)
        return {"messages": [response]}
    except Exception as e:
        print(f"⚠️ LLM not available, using echo mode: {e}")
        # Echo mode for testing without OpenAI API key
        last_message = messages[-1]
        echo_response = {
            "role": "assistant",
            "content": f"Echo: {last_message.content if hasattr(last_message, 'content') else str(last_message)}"
        }
        return {"messages": [echo_response]}


# Build the graph
print("🔨 Building LangGraph...")
graph_builder = StateGraph(State)
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)

# Compile the graph in a thread using async
async def compile_graph():
    def _compile():
        return graph_builder.compile()
    return await asyncio.to_thread(_compile)

graph = asyncio.run(compile_graph())

print("✅ LangGraph compiled successfully")
print("=" * 80)
print("🚀 Ready to deploy!")
print("=" * 80)

# This is what LangSmith/LangGraph Platform will import
__all__ = ["graph"]

