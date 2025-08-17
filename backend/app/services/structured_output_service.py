"""
Structured Output Service - Schema-Enforced JSON Responses

Implements Pydantic/Zod schema validation for guaranteed structured outputs.
"""

import json
import time
from typing import Any, Dict, List, Optional, Type, Union
from datetime import datetime
from enum import Enum

import structlog
from pydantic import BaseModel, Field, ValidationError, create_model
from pydantic.json_schema import GenerateJsonSchema

from app.core.config import get_settings
from app.services.ai_providers.openai_provider import OpenAIProvider
from app.services.ai_providers.anthropic_provider import AnthropicProvider
from app.core.exceptions import DigiSetuException

logger = structlog.get_logger(__name__)
settings = get_settings()


class OutputFormat(str, Enum):
    """Supported output formats."""
    JSON_OBJECT = "json_object"
    PYDANTIC_MODEL = "pydantic_model"
    CUSTOM_SCHEMA = "custom_schema"


class StructuredOutputRequest(BaseModel):
    """Request for structured output generation."""
    prompt: str
    schema: Optional[Dict[str, Any]] = None
    model_class: Optional[str] = None
    output_format: OutputFormat = OutputFormat.JSON_OBJECT
    model: str = "gpt-4"
    temperature: float = 0.1
    max_tokens: int = 2000


class StructuredOutputResponse(BaseModel):
    """Response with structured output."""
    data: Dict[str, Any]
    schema_used: Dict[str, Any]
    validation_passed: bool
    model_used: str
    generation_time: float
    token_usage: Optional[Dict[str, int]] = None


# Predefined common schemas
class PersonSchema(BaseModel):
    """Schema for person information."""
    name: str = Field(..., description="Full name of the person")
    age: int = Field(..., ge=0, le=150, description="Age in years")
    email: str = Field(..., description="Email address")
    occupation: str = Field(..., description="Job title or occupation")
    skills: List[str] = Field(default=[], description="List of skills")
    is_active: bool = Field(default=True, description="Whether the person is active")


class ProductSchema(BaseModel):
    """Schema for product information."""
    name: str = Field(..., description="Product name")
    price: float = Field(..., gt=0, description="Price in USD")
    category: str = Field(..., description="Product category")
    description: str = Field(..., description="Product description")
    in_stock: bool = Field(default=True, description="Whether product is in stock")
    tags: List[str] = Field(default=[], description="Product tags")
    rating: float = Field(default=0.0, ge=0, le=5, description="Product rating (0-5)")


class EventSchema(BaseModel):
    """Schema for event information."""
    title: str = Field(..., description="Event title")
    date: str = Field(..., description="Event date (ISO format)")
    location: str = Field(..., description="Event location")
    attendees: int = Field(..., ge=0, description="Number of attendees")
    is_virtual: bool = Field(default=False, description="Whether event is virtual")
    categories: List[str] = Field(default=[], description="Event categories")


class AnalysisSchema(BaseModel):
    """Schema for analysis results."""
    summary: str = Field(..., description="Summary of analysis")
    key_findings: List[str] = Field(..., description="Key findings from analysis")
    confidence_score: float = Field(..., ge=0, le=1, description="Confidence in analysis")
    recommendations: List[str] = Field(default=[], description="Recommendations based on analysis")
    data_quality: str = Field(..., description="Assessment of data quality")
    methodology: str = Field(..., description="Analysis methodology used")


class StructuredOutputService:
    """Service for generating schema-enforced structured outputs."""
    
    def __init__(self):
        """Initialize structured output service."""
        self.openai_provider = OpenAIProvider()
        self.anthropic_provider = AnthropicProvider()
        
        # Registry of predefined schemas
        self.schema_registry = {
            "person": PersonSchema,
            "product": ProductSchema,
            "event": EventSchema,
            "analysis": AnalysisSchema
        }
    
    async def generate_structured_output(
        self,
        request: StructuredOutputRequest
    ) -> StructuredOutputResponse:
        """
        Generate structured output with schema validation.
        
        Args:
            request: Structured output request with prompt and schema
            
        Returns:
            Validated structured output response
        """
        try:
            start_time = time.time()
            
            logger.info(
                "Generating structured output",
                prompt_length=len(request.prompt),
                output_format=request.output_format,
                model=request.model
            )
            
            # Get or create schema
            schema_dict, model_class = self._get_schema(request)
            
            # Generate output based on model
            if request.model.startswith('gpt'):
                raw_output, token_usage = await self._generate_openai_structured(
                    request, schema_dict
                )
            elif request.model.startswith('claude'):
                raw_output, token_usage = await self._generate_anthropic_structured(
                    request, schema_dict
                )
            else:
                # Default to OpenAI
                raw_output, token_usage = await self._generate_openai_structured(
                    request, schema_dict
                )
            
            # Validate output against schema
            validated_data, validation_passed = self._validate_output(
                raw_output, model_class, schema_dict
            )
            
            generation_time = time.time() - start_time
            
            logger.info(
                "Structured output generated",
                validation_passed=validation_passed,
                generation_time=generation_time,
                data_keys=list(validated_data.keys()) if isinstance(validated_data, dict) else []
            )
            
            return StructuredOutputResponse(
                data=validated_data,
                schema_used=schema_dict,
                validation_passed=validation_passed,
                model_used=request.model,
                generation_time=generation_time,
                token_usage=token_usage
            )
            
        except Exception as e:
            logger.error("Structured output generation failed", error=str(e), exc_info=True)
            raise DigiSetuException(
                "STRUCTURED_OUTPUT_FAILED",
                f"Structured output generation failed: {str(e)}",
                500,
                {"prompt": request.prompt[:100], "model": request.model}
            )
    
    def _get_schema(self, request: StructuredOutputRequest) -> tuple[Dict[str, Any], Optional[Type[BaseModel]]]:
        """Get schema dictionary and model class."""
        
        if request.model_class and request.model_class in self.schema_registry:
            # Use predefined schema
            model_class = self.schema_registry[request.model_class]
            schema_dict = model_class.model_json_schema()
            return schema_dict, model_class
        
        elif request.schema:
            # Use custom schema
            return request.schema, None
        
        else:
            # Default to flexible object schema
            default_schema = {
                "type": "object",
                "properties": {
                    "result": {"type": "string", "description": "The main result"},
                    "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                    "metadata": {"type": "object", "description": "Additional metadata"}
                },
                "required": ["result"]
            }
            return default_schema, None
    
    async def _generate_openai_structured(
        self,
        request: StructuredOutputRequest,
        schema: Dict[str, Any]
    ) -> tuple[Dict[str, Any], Dict[str, int]]:
        """Generate structured output using OpenAI with JSON schema."""
        
        system_prompt = f"""You are a structured data generator. Generate a JSON response that strictly follows the provided schema.

Schema:
{json.dumps(schema, indent=2)}

Requirements:
1. Follow the schema exactly
2. Include all required fields
3. Use appropriate data types
4. Provide meaningful, realistic data
5. Return only valid JSON"""

        try:
            response = await self.openai_provider.client.chat.completions.create(
                model=request.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": request.prompt}
                ],
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            token_usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
            
            return json.loads(content), token_usage
            
        except Exception as e:
            logger.error("OpenAI structured generation failed", error=str(e))
            raise
    
    async def _generate_anthropic_structured(
        self,
        request: StructuredOutputRequest,
        schema: Dict[str, Any]
    ) -> tuple[Dict[str, Any], Dict[str, int]]:
        """Generate structured output using Anthropic with tool forcing."""
        
        # Create a tool that enforces the schema
        tool_definition = {
            "name": "generate_structured_data",
            "description": "Generate structured data according to the specified schema",
            "input_schema": schema
        }
        
        system_prompt = f"""You are a structured data generator. Use the generate_structured_data tool to create data that follows the schema exactly.

Requirements:
1. Follow the schema precisely
2. Include all required fields
3. Use appropriate data types
4. Provide meaningful, realistic data"""

        try:
            response = await self.anthropic_provider.client.messages.create(
                model=request.model,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": request.prompt}
                ],
                tools=[tool_definition],
                tool_choice={"type": "tool", "name": "generate_structured_data"}
            )
            
            # Extract tool use result
            tool_use = None
            for content_block in response.content:
                if content_block.type == "tool_use":
                    tool_use = content_block
                    break
            
            if tool_use:
                structured_data = tool_use.input
            else:
                # Fallback: try to parse JSON from text
                text_content = ""
                for content_block in response.content:
                    if content_block.type == "text":
                        text_content += content_block.text
                
                # Try to extract JSON
                json_start = text_content.find('{')
                json_end = text_content.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    structured_data = json.loads(text_content[json_start:json_end])
                else:
                    structured_data = {"result": text_content}
            
            token_usage = {
                "prompt_tokens": response.usage.input_tokens,
                "completion_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens + response.usage.output_tokens
            }
            
            return structured_data, token_usage
            
        except Exception as e:
            logger.error("Anthropic structured generation failed", error=str(e))
            raise
    
    def _validate_output(
        self,
        raw_output: Dict[str, Any],
        model_class: Optional[Type[BaseModel]],
        schema: Dict[str, Any]
    ) -> tuple[Dict[str, Any], bool]:
        """Validate output against schema."""
        
        try:
            if model_class:
                # Validate using Pydantic model
                validated_instance = model_class(**raw_output)
                return validated_instance.model_dump(), True
            else:
                # Basic schema validation (simplified)
                # In a full implementation, you'd use jsonschema library
                required_fields = schema.get("required", [])
                for field in required_fields:
                    if field not in raw_output:
                        logger.warning(f"Missing required field: {field}")
                        return raw_output, False
                
                return raw_output, True
                
        except ValidationError as e:
            logger.warning("Validation failed", error=str(e))
            return raw_output, False
        except Exception as e:
            logger.error("Validation error", error=str(e))
            return raw_output, False
    
    def get_available_schemas(self) -> Dict[str, Dict[str, Any]]:
        """Get all available predefined schemas."""
        
        schemas = {}
        for name, model_class in self.schema_registry.items():
            schemas[name] = {
                "name": name,
                "description": model_class.__doc__ or f"Schema for {name}",
                "schema": model_class.model_json_schema(),
                "example": self._generate_example_data(model_class)
            }
        
        return schemas
    
    def _generate_example_data(self, model_class: Type[BaseModel]) -> Dict[str, Any]:
        """Generate example data for a schema."""
        
        try:
            # Create example instances
            if model_class == PersonSchema:
                example = PersonSchema(
                    name="John Doe",
                    age=30,
                    email="john.doe@example.com",
                    occupation="Software Engineer",
                    skills=["Python", "JavaScript", "AI"],
                    is_active=True
                )
            elif model_class == ProductSchema:
                example = ProductSchema(
                    name="Wireless Headphones",
                    price=199.99,
                    category="Electronics",
                    description="High-quality wireless headphones with noise cancellation",
                    in_stock=True,
                    tags=["audio", "wireless", "premium"],
                    rating=4.5
                )
            elif model_class == EventSchema:
                example = EventSchema(
                    title="AI Conference 2024",
                    date="2024-09-15T09:00:00Z",
                    location="San Francisco, CA",
                    attendees=500,
                    is_virtual=False,
                    categories=["technology", "AI", "conference"]
                )
            elif model_class == AnalysisSchema:
                example = AnalysisSchema(
                    summary="Comprehensive data analysis reveals positive trends",
                    key_findings=["Growth rate increased by 15%", "Customer satisfaction improved"],
                    confidence_score=0.85,
                    recommendations=["Continue current strategy", "Expand to new markets"],
                    data_quality="High quality with minimal missing values",
                    methodology="Statistical analysis with machine learning validation"
                )
            else:
                # Generic example
                return {"example": "data"}
            
            return example.model_dump()
            
        except Exception as e:
            logger.error("Example generation failed", error=str(e))
            return {"example": "data"}
    
    def create_custom_schema(
        self,
        name: str,
        fields: Dict[str, Dict[str, Any]]
    ) -> Type[BaseModel]:
        """Create a custom Pydantic model dynamically."""
        
        try:
            # Convert field definitions to Pydantic fields
            pydantic_fields = {}
            for field_name, field_config in fields.items():
                field_type = field_config.get("type", str)
                field_description = field_config.get("description", "")
                field_default = field_config.get("default", ...)
                
                if field_default == ...:
                    pydantic_fields[field_name] = (field_type, Field(description=field_description))
                else:
                    pydantic_fields[field_name] = (field_type, Field(default=field_default, description=field_description))
            
            # Create dynamic model
            custom_model = create_model(name, **pydantic_fields)
            
            # Add to registry
            self.schema_registry[name.lower()] = custom_model
            
            return custom_model
            
        except Exception as e:
            logger.error("Custom schema creation failed", error=str(e))
            raise

