"""LLM Adapter - Standalone model creation"""
from agno.models.google import Gemini
from agno.models.groq import Groq
from agno.models.openai import OpenAIChat
from agno.models.anthropic import Claude
# from agno.models.azure_openai import 
from schemas import ModelConfig


class LLMAdapter:
    """Creates LLM model instances"""

    @staticmethod
    def create_model(config: ModelConfig):
        provider = config.provider
        model_id = config.model_id
        api_key = config.api_key

        if provider == 'gemini':
            return Gemini(
                id=model_id,
                api_key=api_key
            )

        elif provider == 'claude':
            return Claude(
                id=model_id,
                api_key=api_key
            )

        elif provider == 'openai':
            return OpenAIChat(
                id=model_id,
                api_key=api_key
            )
        
        elif provider == 'groq':
            return Groq(
                id=model_id,
                api_key=api_key
            )

        elif provider == 'azure':
            return AzureOpenAIChat(
                id=model_id,
                api_key=api_key,
                azure_endpoint=config.azure_endpoint,
                api_version=config.api_version
            )

        else:
            raise ValueError(f"Unsupported provider: {provider}")
