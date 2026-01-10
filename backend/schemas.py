
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any

class RiskAnalysisRequest(BaseModel):
    reserves: float = Field(..., ge=0, description="Current total reserves")
    supply: float = Field(..., ge=0, description="Current circulating supply")
    whales: float = Field(0.0, ge=0, description="Supply held by whales")
    price: float = Field(1.0, gt=0, description="Current market price")
    
    prev_reserves: Optional[float] = Field(None, ge=0)
    prev_supply: Optional[float] = Field(None, ge=0)
    custodians: Optional[List[Dict[str, Any]]] = Field(default_factory=list)

    @field_validator('price')
    def price_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Price must be positive')
        return v
