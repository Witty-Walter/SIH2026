from agents.state import AgentState
from agents.prompts.intent_prompt import INTENT_SYSTEM
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from config import settings
import json

# Initialize LLM, using Groq with JSON mode
llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0, 
    api_key=settings.groq_api_key,
    model_kwargs={"response_format": {"type": "json_object"}}
)

async def intent_node(state: AgentState) -> dict:
    if not state.get("messages"):
        return {}
        
    last_message = state["messages"][-1].content
    
    prompt = [
        SystemMessage(content=INTENT_SYSTEM),
        HumanMessage(content=last_message)
    ]
    
    try:
        response = await llm.ainvoke(prompt)
        content = response.content.strip()
        start = content.find('{')
        end = content.rfind('}')
        if start != -1 and end != -1:
            content = content[start:end+1]
            
        parsed = json.loads(content)
        
        # Persist language if not already set, or update if it changed
        new_lang = parsed.get("language", "en")
        
        return {
            "intent": parsed,
            "user_language": new_lang
        }
    except Exception as e:
        print(f"Error parsing intent: {e}")
        # Fallback
        return {
            "intent": {
                "action": "general_info",
                "entities": {"zone_name": None, "time": "now", "user_wants_alternatives": False},
                "language": "en"
            }
        }
