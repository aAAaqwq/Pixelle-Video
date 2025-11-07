# Copyright (C) 2025 AIDC-AI
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Title generation prompt

For generating video title from content.
"""


TITLE_GENERATION_PROMPT = """Please generate a short, attractive title (within 10 characters) for the following content.

Content:
{content}

Requirements:
1. Brief and concise, within 10 characters
2. Accurately summarize the core content
3. Attractive, suitable as a video title
4. Output only the title text, no other content

Title:"""


def build_title_generation_prompt(content: str, max_length: int = 500) -> str:
    """
    Build title generation prompt
    
    Args:
        content: Content to generate title from
        max_length: Maximum content length to use (default 500 chars)
    
    Returns:
        Formatted prompt
    """
    # Take first max_length chars to avoid overly long prompts
    content_preview = content[:max_length]
    
    return TITLE_GENERATION_PROMPT.format(
        content=content_preview
    )

