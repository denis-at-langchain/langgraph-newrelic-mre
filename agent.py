"""
Minimal Reproducible Example: LangGraph + New Relic Integration Issue

This demonstrates the conflict between LangGraph Platform's ASGI server lifecycle
and New Relic's automatic instrumentation hooks.

Problem: LangGraph Platform controls how Uvicorn is initialized, causing direct
conflicts with New Relic's automatic instrumentation hooks.
"""

import os
import sys

# ============================================================================
# NEW RELIC INITIALIZATION - This is where the issue occurs
# ============================================================================

print("=" * 80)
print("🔧 Attempting New Relic initialization...")
print("=" * 80)

try:
    import newrelic.agent
    
    # Method 1: Try to initialize from newrelic.ini file
    config_file = None
    possible_locations = [
        "./newrelic.ini",
        "../newrelic.ini",
        "newrelic.ini",
        os.path.join(os.getcwd(), "newrelic.ini")
    ]
    
    for location in possible_locations:
        if os.path.exists(location):
            config_file = location
            print(f"📄 Found New Relic config at: {config_file}")
            break
    
    if config_file:
        newrelic.agent.initialize(config_file)
        print(f"✅ New Relic agent initialized with config: {config_file}")
    else:
        # Method 2: Initialize with environment variables only
        newrelic.agent.initialize()
        print("✅ New Relic agent initialized with environment variables")
        
    print(f"📊 New Relic App Name: {os.environ.get('NEW_RELIC_APP_NAME', 'Not Set')}")
    print(f"🔑 New Relic License Key: {'Set' if os.environ.get('NEW_RELIC_LICENSE_KEY') else 'Not Set'}")
    
except ImportError as e:
    print(f"⚠️ New Relic not available: {e}")
except Exception as e:
    print(f"❌ Error initializing New Relic: {e}")
    print(f"   Error type: {type(e).__name__}")
    import traceback
    traceback.print_exc()

print("=" * 80)

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

# Compile the graph
graph = graph_builder.compile()

print("✅ LangGraph compiled successfully")
print("=" * 80)
print("🚀 Ready to deploy!")
print("=" * 80)

# This is what LangSmith/LangGraph Platform will import
__all__ = ["graph"]

