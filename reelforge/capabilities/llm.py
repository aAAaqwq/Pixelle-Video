"""
LLM Capabilities using OpenAI SDK

All LLM providers that follow OpenAI SDK protocol are supported:
- OpenAI (gpt-4o, gpt-4o-mini, gpt-3.5-turbo)
- Alibaba Qwen (qwen-max, qwen-plus, qwen-turbo)
- Anthropic Claude (claude-sonnet-4-5, claude-opus-4, claude-haiku-4)
- DeepSeek (deepseek-chat)
- Moonshot Kimi (moonshot-v1-8k, moonshot-v1-32k, moonshot-v1-128k)
- Ollama (llama3.2, qwen2.5, mistral, codellama) - FREE & LOCAL!
- Any custom provider with OpenAI-compatible API

Convention: Unified llm_call tool for all providers
"""

from openai import AsyncOpenAI
from loguru import logger
from pydantic import Field

from reelforge.core.mcp_server import reelforge_mcp


@reelforge_mcp.tool(
    description="Generate text using any OpenAI SDK compatible LLM",
    meta={
        "reelforge": {
            "display_name": "LLM (OpenAI SDK)",
            "description": "Unified interface for all OpenAI SDK compatible LLMs",
            "is_default": True,
        }
    },
)
async def llm_call(
    prompt: str = Field(description="The prompt to generate from"),
    api_key: str = Field(description="API key for the LLM provider"),
    base_url: str = Field(description="Base URL for the LLM API"),
    model: str = Field(description="Model name to use"),
    temperature: float = Field(default=0.7, description="Sampling temperature"),
    max_tokens: int = Field(default=2000, description="Maximum tokens to generate"),
) -> str:
    """
    Generate text using any OpenAI SDK compatible LLM
    
    This is a unified interface that works with any LLM provider
    following the OpenAI SDK protocol.
    
    Example:
        # OpenAI
        result = await llm_call(
            prompt="Explain quantum physics",
            api_key="sk-xxx",
            base_url="https://api.openai.com/v1",
            model="gpt-4o"
        )
        
        # Qwen
        result = await llm_call(
            prompt="解释量子物理",
            api_key="sk-xxx",
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            model="qwen-max"
        )
        
        # Anthropic Claude
        result = await llm_call(
            prompt="Explain reasoning step by step",
            api_key="sk-ant-xxx",
            base_url="https://api.anthropic.com/v1/",
            model="claude-sonnet-4-5"
        )
        
        # DeepSeek
        result = await llm_call(
            prompt="Explain AI",
            api_key="sk-xxx",
            base_url="https://api.deepseek.com",
            model="deepseek-chat"
        )
        
        # Ollama (Local - FREE & PRIVATE!)
        result = await llm_call(
            prompt="Write a Python function to sort a list",
            api_key="ollama",  # Required but unused
            base_url="http://localhost:11434/v1",
            model="llama3.2"
        )
    """
    logger.debug(f"LLM call: model={model}, base_url={base_url}")
    
    try:
        client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url,
        )
        
        response = await client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        
        result = response.choices[0].message.content
        logger.debug(f"LLM response length: {len(result)} chars")
        
        return result
    
    except Exception as e:
        logger.error(f"LLM call error (model={model}, base_url={base_url}): {e}")
        raise

