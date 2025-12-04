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
Asset-based video script generation prompt

For generating video scripts based on user-provided assets.
"""


ASSET_SCRIPT_GENERATION_PROMPT = """你是一位专业的视频脚本创作者。请基于用户提供的视频意图和可用素材，生成一个 {duration} 秒的视频脚本。

## 需求信息
{title_section}- 视频意图：{intent}
- 目标时长：{duration} 秒

## 可用素材（请在输出中使用精确路径）
{assets_text}

## 创作指南
1. 根据目标时长决定需要多少个场景（通常每个场景 5-15 秒）
2. 为每个场景从可用素材中直接分配一个素材
3. 每个场景可以包含 1-3 句旁白
4. 尽量使用所有可用素材，但如有需要可以复用素材
5. 所有场景的总时长应约等于 {duration} 秒
{title_instruction}

## 语言一致性要求（非常重要）
- 旁白的语言必须与用户输入的视频意图保持一致
- 如果视频意图是中文，则旁白必须是中文
- 如果视频意图是英文，则旁白必须是英文
- 除非视频意图中明确指定了输出语言，否则严格遵循意图的原始语言

## 输出要求
为每个场景提供：
- scene_number: 场景编号（从 1 开始）
- asset_path: 从可用素材列表中选择的精确路径
- narrations: 包含 1-3 句旁白的数组
- duration: 预估时长（秒）

现在请开始生成视频脚本："""


def build_asset_script_prompt(
    intent: str,
    duration: int,
    assets_text: str,
    title: str = ""
) -> str:
    """
    Build asset-based script generation prompt
    
    Args:
        intent: Video intent/purpose
        duration: Target duration in seconds
        assets_text: Formatted text of available assets with descriptions
        title: Optional video title
    
    Returns:
        Formatted prompt
    """
    title_section = f"- 视频标题：{title}\n" if title else ""
    title_instruction = f"6. 旁白内容应与视频标题保持一致：{title}\n" if title else ""
    
    return ASSET_SCRIPT_GENERATION_PROMPT.format(
        duration=duration,
        title_section=title_section,
        intent=intent,
        assets_text=assets_text,
        title_instruction=title_instruction
    )
