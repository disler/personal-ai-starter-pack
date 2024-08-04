from pydantic import BaseModel
from typing import Any, Dict, List, Optional, Union

import warnings

# Suppress specific warnings
warnings.filterwarnings("ignore", message="Valid config keys have changed in V2:")
warnings.filterwarnings(
    "ignore", message='Field "model_id" has conflict with protected namespace "model_".'
)


class Interaction(BaseModel):
    role: str
    content: str
