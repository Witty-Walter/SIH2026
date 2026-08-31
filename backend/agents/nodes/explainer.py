from agents.state import AgentState
from agents.prompts.explainer_prompt import EXPLAINER_SYSTEM
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from config import settings
import json

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0.3, # Slightly more creative for natural language 
    api_key=settings.groq_api_key
)

async def explainer_node(state: AgentState) -> dict:
    risk_result = state.get("risk_result", {})
    ocean_data_raw = state.get("ocean_data", [])
    pfz_data = state.get("pfz_data", {})
    target_lang = state.get("user_language", "en")
    alternative_zones = state.get("alternative_zones", [])
    
    user_question = state.get("messages", [])[-1].content if state.get("messages") else "Assess safety"
    
    # Flatten ocean data for the LLM if it's a list of observations
    ocean_dict = {obs["variable"]: obs["value"] for obs in ocean_data_raw} \
        if isinstance(ocean_data_raw, list) else ocean_data_raw
    
    context_data = {
        "risk": risk_result,
        "ocean": ocean_dict,
        "pfz": pfz_data,
        "alternative_zones": alternative_zones
    }
    
    prompt = [
        SystemMessage(content=EXPLAINER_SYSTEM),
        HumanMessage(content=f"User's Question: {user_question}\n\nExplain this data and answer the user's question directly. Ensure the response is in language code: {target_lang}\n\nData: {json.dumps(context_data, indent=2)}")
    ]
    
    try:
        response = await llm.ainvoke(prompt)
        return {"response_text": response.content}
    except Exception as e:
        print(f"Error in explainer: {e}")
        return {"response_text": "I encountered an error analyzing the data. Please try again."}
