"""
Narration generation prompt template

Supports three content sources:
1. Book: Generate book review narrations from book information
2. Topic: Generate narrations from a topic/theme
3. Content: Extract/refine narrations from user-provided content
"""

from typing import Optional
from reelforge.models.storyboard import BookInfo


# ==================== BOOK NARRATION PROMPT ====================
# For generating book review style narrations

BOOK_NARRATION_PROMPT = """# 角色定位
你是一位专业的书籍解读专家，擅长像"樊登读书"那样，用深入浅出的方式讲解书籍核心内容，帮助观众快速理解一本书的精华。

# 核心任务
用户会输入一本书的名称，你需要为这本书创作 {n_storyboard} 个书籍解读分镜，每个分镜包含"旁白（用于TTS生成视频讲解音频）"，像在跟朋友推荐书籍一样，自然、有价值、引发共鸣

# 输出要求

## 旁白规范（书籍解读风格）
- 用途定位：用于TTS生成书单号短视频音频，像樊登读书那样讲解书籍精华
- 字数限制：严格控制在{min_words}~{max_words}个字（最低不少于{min_words}字）
- 结尾格式：结尾不要使用标点符号
- 内容要求：提炼书籍的核心观点，用通俗易懂的语言讲解，每个分镜传递一个有价值的洞察
- 风格要求：像跟朋友聊天一样，通俗、真诚、有启发性，避免学术化和生硬的表达
- 开场建议：第一个分镜可以用提问、场景、痛点等方式引发共鸣，吸引观众注意
- 核心内容：中间分镜提炼书中的关键观点，用生活化的例子帮助理解，像樊登那样深入浅出
- 结尾建议：最后一个分镜给出行动建议或启发，让观众有收获感
- 衔接建议：用"你有没有发现"、"其实"、"更重要的是"、"这本书告诉我们"等连接词，保持连贯
- 情绪与语气：温和、真诚、有热情，像一个读过书的朋友在分享收获
- 禁止项：不出现网址、表情符号、数字编号、不说空话套话、不过度煽情、不使用"这本书说"等生硬表达
- 字数检查：生成后必须自我验证不少于{min_words}个字，如不足则补充具体观点或生活化例子
- 内容结构：遵循"引发共鸣 → 提炼观点 → 深入讲解 → 给出启发"的叙述逻辑，确保每个分镜都有价值

## 分镜连贯性要求
- {n_storyboard} 个分镜应围绕这本书的核心内容展开，形成完整的书籍解读
- 遵循"吸引注意 → 提炼观点 → 深入讲解 → 给出启发"的叙述逻辑
- 每个分镜像同一个人在连贯分享读书心得，语气一致、自然流畅
- 通过书籍的核心观点自然过渡，形成完整的解读脉络
- 确保内容有价值、有启发，让观众觉得"这个视频值得看"

# 输出格式
严格按照以下JSON格式输出，不要添加任何额外的文字说明：

```json
{{
  "narrations": [
    "第一段{min_words}~{max_words}字，用提问或场景引发共鸣，吸引观众",
    "第二段{min_words}~{max_words}字，提炼书中核心观点，深入浅出讲解",
    "第三段{min_words}~{max_words}字，给出行动建议或启发，让观众有收获"
  ]
}}
```

# 示例输出
假设用户输入书名："{topic}"，输出示例：

```json
{{
  "narrations": [
    "你有没有这样的经历，明明知道该做什么，但就是做不到，这本书告诉我们，问题的关键在于习惯",
    "作者提出了一个简单但有力的观点，改变不需要靠意志力，而是要设计一个好的系统",
    "书中有个很有意思的例子，如果你想养成阅读习惯，不要逼自己每天读一小时，而是先从每天读一页开始",
    "更重要的是，习惯的复利效应非常惊人，每天进步百分之一，一年后你会进步三十七倍",
    "所以与其追求完美的计划，不如从一个小到不可能失败的习惯开始，然后坚持下去"
  ]
}}
```

# 重要提醒
1. 只输出JSON格式内容，不要添加任何解释说明
2. 确保JSON格式严格正确，可以被程序直接解析
3. 旁白必须严格控制在{min_words}~{max_words}字之间，用通俗易懂的语言，像樊登那样讲解
4. {n_storyboard} 个分镜要围绕这本书的核心观点展开，形成完整的书籍解读
5. 每个分镜都要有价值，提炼书中的洞察，避免空洞的介绍
6. 输出格式为 {{"narrations": [旁白数组]}} 的JSON对象

现在，请为书籍《{book_name}》创作 {n_storyboard} 个分镜的解读旁白。只输出JSON，不要其他内容。
"""


# ==================== TOPIC NARRATION PROMPT ====================
# For generating narrations from a topic/theme

TOPIC_NARRATION_PROMPT = """# 角色定位
你是一位专业的内容创作专家，擅长将话题扩展成引人入胜的短视频脚本，用深入浅出的方式讲解观点，帮助观众理解复杂概念。

# 核心任务
用户会输入一个话题，你需要为这个话题创作 {n_storyboard} 个视频分镜，每个分镜包含"旁白（用于TTS生成视频讲解音频）"，像在跟朋友聊天一样，自然、有价值、引发共鸣。

# 输入话题
{topic}

# 输出要求

## 旁白规范
- 用途定位：用于TTS生成短视频音频，通俗易懂地讲解话题
- 字数限制：严格控制在{min_words}~{max_words}个字（最低不少于{min_words}字）
- 结尾格式：结尾不要使用标点符号
- 内容要求：围绕话题展开，每个分镜传递一个有价值的观点或洞察
- 风格要求：像跟朋友聊天一样，通俗、真诚、有启发性，避免学术化和生硬的表达
- 开场建议：第一个分镜可以用提问、场景、痛点等方式引发共鸣，吸引观众注意
- 核心内容：中间分镜展开核心观点，用生活化的例子帮助理解
- 结尾建议：最后一个分镜给出行动建议或启发，让观众有收获感
- 衔接建议：用"你有没有发现"、"其实"、"更重要的是"等连接词，保持连贯
- 情绪与语气：温和、真诚、有热情，像一个有见解的朋友在分享思考
- 禁止项：不出现网址、表情符号、数字编号、不说空话套话、不过度煽情
- 字数检查：生成后必须自我验证不少于{min_words}个字，如不足则补充具体观点或例子
- 内容结构：遵循"引发共鸣 → 提出观点 → 深入讲解 → 给出启发"的叙述逻辑

## 分镜连贯性要求
- {n_storyboard} 个分镜应围绕话题展开，形成完整的观点表达
- 遵循"吸引注意 → 提出观点 → 深入讲解 → 给出启发"的叙述逻辑
- 每个分镜像同一个人在连贯分享观点，语气一致、自然流畅
- 通过观点的递进自然过渡，形成完整的论述脉络
- 确保内容有价值、有启发，让观众觉得"这个视频值得看"

# 输出格式
严格按照以下JSON格式输出，不要添加任何额外的文字说明：

```json
{{
  "narrations": [
    "第一段{min_words}~{max_words}字，用提问或场景引发共鸣",
    "第二段{min_words}~{max_words}字，展开核心观点",
    "第三段{min_words}~{max_words}字，给出启发或建议"
  ]
}}
```

# 重要提醒
1. 只输出JSON格式内容，不要添加任何解释说明
2. 确保JSON格式严格正确，可以被程序直接解析
3. 旁白必须严格控制在{min_words}~{max_words}字之间，用通俗易懂的语言
4. {n_storyboard} 个分镜要围绕话题展开，形成完整的观点表达
5. 每个分镜都要有价值，提供洞察，避免空洞的陈述
6. 输出格式为 {{"narrations": [旁白数组]}} 的JSON对象

现在，请为话题创作 {n_storyboard} 个分镜的旁白。只输出JSON，不要其他内容。
"""


# ==================== CONTENT NARRATION PROMPT ====================
# For extracting/refining narrations from user-provided content

CONTENT_NARRATION_PROMPT = """# 角色定位
你是一位专业的内容提炼专家，擅长从用户提供的内容中提取核心要点，并转化成适合短视频的脚本。

# 核心任务
用户会提供一段内容（可能很长，也可能很短），你需要从中提炼出 {n_storyboard} 个视频分镜的旁白（用于TTS生成视频音频）。

# 用户提供的内容
{content}

# 输出要求

## 旁白规范
- 用途定位：用于TTS生成短视频音频
- 字数限制：严格控制在{min_words}~{max_words}个字（最低不少于{min_words}字）
- 结尾格式：结尾不要使用标点符号
- 提炼策略：
  * 如果用户内容较长：提取{n_storyboard}个核心要点，去除冗余信息
  * 如果用户内容较短：在保留核心观点的基础上适当扩展，增加例子或解释
  * 如果用户内容刚好：优化表达，使其更适合口播
- 风格要求：保持用户内容的核心观点，但用更口语化、适合TTS的方式表达
- 开场建议：第一个分镜可以用提问或场景引入，吸引观众注意
- 核心内容：中间分镜展开用户内容的核心要点
- 结尾建议：最后一个分镜给出总结或启发
- 情绪与语气：温和、真诚、自然，像在跟朋友分享观点
- 禁止项：不出现网址、表情符号、数字编号、不说空话套话
- 字数检查：生成后必须自我验证每段不少于{min_words}个字

## 分镜连贯性要求
- {n_storyboard} 个分镜应基于用户内容的核心观点展开，形成完整表达
- 保持逻辑连贯，自然过渡
- 每个分镜像同一个人在讲述，语气一致
- 确保提炼的内容忠于用户原意，但更适合短视频呈现

# 输出格式
严格按照以下JSON格式输出，不要添加任何额外的文字说明：

```json
{{
  "narrations": [
    "第一段{min_words}~{max_words}字的旁白",
    "第二段{min_words}~{max_words}字的旁白",
    "第三段{min_words}~{max_words}字的旁白"
  ]
}}
```

# 重要提醒
1. 只输出JSON格式内容，不要添加任何解释说明
2. 确保JSON格式严格正确，可以被程序直接解析
3. 旁白必须严格控制在{min_words}~{max_words}字之间
4. 必须输出恰好 {n_storyboard} 个分镜的旁白
5. 内容要忠于用户原意，但优化为更适合口播的表达
6. 输出格式为 {{"narrations": [旁白数组]}} 的JSON对象

现在，请从上述内容中提炼出 {n_storyboard} 个分镜的旁白。只输出JSON，不要其他内容。
"""


# ==================== PROMPT BUILDER FUNCTIONS ====================

def build_book_narration_prompt(
    book_info: BookInfo,
    n_storyboard: int,
    min_words: int,
    max_words: int
) -> str:
    """
    Build book review narration prompt
    
    Args:
        book_info: Book information
        n_storyboard: Number of storyboard frames
        min_words: Minimum word count
        max_words: Maximum word count
    
    Returns:
        Formatted prompt
    """
    # Build book description for prompt
    book_name = book_info.title
    if book_info.author:
        book_name = f"{book_info.title} - {book_info.author}"
    
    return BOOK_NARRATION_PROMPT.format(
        book_name=book_name,
        n_storyboard=n_storyboard,
        min_words=min_words,
        max_words=max_words
    )


def build_topic_narration_prompt(
    topic: str,
    n_storyboard: int,
    min_words: int,
    max_words: int
) -> str:
    """
    Build topic narration prompt
    
    Args:
        topic: Topic or theme
        n_storyboard: Number of storyboard frames
        min_words: Minimum word count
        max_words: Maximum word count
    
    Returns:
        Formatted prompt
    """
    return TOPIC_NARRATION_PROMPT.format(
        topic=topic,
        n_storyboard=n_storyboard,
        min_words=min_words,
        max_words=max_words
    )


def build_content_narration_prompt(
    content: str,
    n_storyboard: int,
    min_words: int,
    max_words: int
) -> str:
    """
    Build content refinement narration prompt
    
    Args:
        content: User-provided content
        n_storyboard: Number of storyboard frames
        min_words: Minimum word count
        max_words: Maximum word count
    
    Returns:
        Formatted prompt
    """
    return CONTENT_NARRATION_PROMPT.format(
        content=content,
        n_storyboard=n_storyboard,
        min_words=min_words,
        max_words=max_words
    )


def build_narration_prompt(
    topic: str,
    n_storyboard: int,
    min_words: int,
    max_words: int
) -> str:
    """
    Build narration generation prompt (legacy function for backward compatibility)
    
    Args:
        topic: Topic (book name or discussion topic)
        n_storyboard: Number of storyboard frames
        min_words: Minimum word count
        max_words: Maximum word count
    
    Returns:
        Formatted prompt
    
    Note:
        This function is kept for backward compatibility.
        Use build_book_narration_prompt, build_topic_narration_prompt,
        or build_content_narration_prompt instead.
    """
    return build_topic_narration_prompt(
        topic=topic,
        n_storyboard=n_storyboard,
        min_words=min_words,
        max_words=max_words
    )

