from pydantic import BaseModel
from typing import Any, Dict, List, Optional, Union


class Interaction(BaseModel):
    role: str
    content: str


class FusionChainResult(BaseModel):
    top_response: Union[str, Dict[str, Any]]
    all_prompt_responses: List[List[Any]]
    all_context_filled_prompts: List[List[str]]
    performance_scores: List[float]
    chain_model_names: List[str]
