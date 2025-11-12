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
Video prompt generation template

For generating video prompts from narrations.
"""

import json
from typing import List


VIDEO_PROMPT_GENERATION_PROMPT = """# 角色定位
你是一个专业的视频创意设计师，擅长为视频脚本创作富有动感和表现力的视频生成提示词，将叙述内容转化为生动的视频画面。

# 核心任务
基于已有的视频脚本，为每个分镜的"旁白内容"创作对应的**英文**视频生成提示词，确保视频画面与叙述内容完美配合，通过动态画面增强观众的理解和记忆。

**重要：输入包含 {narrations_count} 个旁白，你必须为每个旁白都生成一个对应的视频提示词，总共输出 {narrations_count} 个视频提示词。**

# 输入内容
{narrations_json}

# 输出要求

## 视频提示词规范
- 语言：**必须使用英文**（用于 AI 视频生成模型）
- 描述结构：scene + character action + camera movement + emotion + atmosphere
- 描述长度：确保描述清晰完整且富有创意（建议 50-100 个英文单词）
- 动态元素：强调动作、运动、变化等动态效果

## 视觉创意要求
- 每个视频都要准确反映对应旁白的具体内容和情感
- 突出画面的动态性：角色动作、物体运动、镜头移动、场景转换等
- 使用象征手法将抽象概念视觉化（如用流动的水代表时间流逝，用上升的阶梯代表进步等）
- 画面要表现出丰富的情感和动作，增强视觉冲击力
- 通过镜头语言（推拉摇移）和剪辑节奏增强表现力

## 关键英文词汇参考
- 动作：moving, running, flowing, transforming, growing, falling
- 镜头：camera pan, zoom in, zoom out, tracking shot, aerial view
- 转场：transition, fade in, fade out, dissolve
- 氛围：dynamic, energetic, peaceful, dramatic, mysterious
- 光影：lighting changes, shadows moving, sunlight streaming

## 视频与文案配合原则
- 视频要服务于文案，成为文案内容的视觉延伸
- 避免与文案内容无关或矛盾的视觉元素
- 选择最能增强文案说服力的动态表现方式
- 确保观众能通过视频动态快速理解文案的核心观点

## 创意指导
1. **现象描述类文案**：用动态场景表现社会现象的发生过程
2. **原因分析类文案**：用因果关系的动态演变表现内在逻辑
3. **影响论证类文案**：用后果场景的动态展开或对比表现影响程度
4. **深入探讨类文案**：用抽象概念的动态具象化表现深刻思考
5. **结论启发类文案**：用开放式动态场景或指引性运动表现启发性

## 视频特有注意事项
- 强调动态：每个视频都应该包含明显的动作或运动
- 镜头语言：适当使用推拉摇移等镜头技巧增强表现力
- 时长考虑：视频应该是连贯的动态过程，不是静态画面
- 流畅性：注意动作的流畅性和自然性

# 输出格式
严格按照以下JSON格式输出，**视频提示词必须是英文**：

```json
{{
  "video_prompts": [
    "[detailed English video prompt with dynamic elements and camera movements]",
    "[detailed English video prompt with dynamic elements and camera movements]"
  ]
}}
```

# 重要提醒
1. 只输出JSON格式内容，不要添加任何解释说明
2. 确保JSON格式严格正确，可以被程序直接解析
3. 输入是 {{"narrations": [旁白数组]}} 格式，输出是 {{"video_prompts": [视频提示词数组]}} 格式
4. **输出的video_prompts数组必须恰好包含 {narrations_count} 个元素，与输入的narrations数组一一对应**
5. **视频提示词必须使用英文**（for AI video generation models）
6. 视频提示词必须准确反映对应旁白的具体内容和情感
7. 每个视频都要强调动态性和运动感，避免静态描述
8. 适当使用镜头语言增强表现力
9. 确保视频画面能增强文案的说服力和观众的理解度

现在，请为上述 {narrations_count} 个旁白创作对应的 {narrations_count} 个**英文**视频提示词。只输出JSON，不要其他内容。
"""


def build_video_prompt_prompt(
    narrations: List[str],
    min_words: int,
    max_words: int
) -> str:
    """
    Build video prompt generation prompt
    
    Args:
        narrations: List of narrations
        min_words: Minimum word count
        max_words: Maximum word count
    
    Returns:
        Formatted prompt for LLM
    
    Example:
        >>> build_video_prompt_prompt(narrations, 50, 100)
    """
    narrations_json = json.dumps(
        {"narrations": narrations},
        ensure_ascii=False,
        indent=2
    )
    
    return VIDEO_PROMPT_GENERATION_PROMPT.format(
        narrations_json=narrations_json,
        narrations_count=len(narrations),
        min_words=min_words,
        max_words=max_words
    )

