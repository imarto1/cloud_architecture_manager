from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class AWSTagDTO(BaseModel):
    key: str
    value: str

class AWSResourceDTO(BaseModel):
    id: str = Field(..., description="The unique identifier of the AWS resource (e.g., ARN or InstanceId)")
    name: Optional[str] = None
    type: str = Field(..., description="The type of AWS resource (e.g., aws_instance, aws_s3_bucket)")
    region: str
    account_id: str
    tags: List[AWSTagDTO] = []
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional AWS-specific metadata from describe calls")

class ResourceRelationshipDTO(BaseModel):
    source_id: str
    target_id: str
    relationship_type: str = Field(..., description="Type of connection (e.g., contains, triggers, routes_to)")
    metadata: Dict[str, Any] = Field(default_factory=dict)

class CloudArchitectureDTO(BaseModel):
    version: str = "1.0"
    name: str
    description: Optional[str] = None
    resources: List[AWSResourceDTO] = []
    relationships: List[ResourceRelationshipDTO] = []
    metadata: Dict[str, Any] = Field(default_factory=dict)

