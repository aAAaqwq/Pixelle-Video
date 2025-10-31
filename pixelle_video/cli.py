"""
Pixelle-Video CLI
"""

import asyncio

from loguru import logger

from pixelle_video.service import pixelle_video


async def test_llm():
    """Test LLM capability"""
    # Initialize pixelle_video
    await pixelle_video.initialize()
    
    # Test prompt
    prompt = "Explain the concept of atomic habits in 3 sentences."
    
    logger.info(f"\n📝 Test Prompt: {prompt}\n")
    
    # Call LLM
    result = await pixelle_video.llm(prompt)
    
    logger.info(f"\n✨ Result:\n{result}\n")


def main():
    """Main CLI entry point"""
    logger.info("🚀 Pixelle-Video CLI\n")
    
    # Run test
    asyncio.run(test_llm())


if __name__ == "__main__":
    main()

