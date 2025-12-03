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
Asset-Based Video Pipeline

Generates marketing videos from user-provided assets (images/videos) rather than
AI-generated media. Ideal for small businesses with existing media libraries.

Workflow:
1. Analyze uploaded assets (images/videos)
2. Generate script based on user intent and available assets
3. Match assets to script scenes
4. Compose final video with narrations

Example:
    pipeline = AssetBasedPipeline(pixelle_video)
    result = await pipeline(
        assets=["/path/img1.jpg", "/path/img2.jpg"],
        video_title="Pet Store Year-End Sale",
        style="warm and friendly",
        duration=30
    )
"""

from typing import List, Dict, Any, Optional
from pathlib import Path

from loguru import logger
from pydantic import BaseModel, Field

from pixelle_video.pipelines.linear import LinearVideoPipeline, PipelineContext
from pixelle_video.utils.os_util import (
    create_task_output_dir,
    get_task_final_video_path
)


# ==================== Structured Output Models ====================

class SceneScript(BaseModel):
    """Single scene in the video script"""
    scene_number: int = Field(description="Scene number starting from 1")
    asset_path: str = Field(description="Path to the asset file for this scene")
    narrations: List[str] = Field(description="List of narration sentences for this scene (1-5 sentences)")
    duration: int = Field(description="Estimated duration in seconds for this scene")


class VideoScript(BaseModel):
    """Complete video script with scenes"""
    scenes: List[SceneScript] = Field(description="List of scenes in the video")


class AssetBasedPipeline(LinearVideoPipeline):
    """
    Asset-Based Video Pipeline
    
    Generates videos from user-provided assets instead of AI-generated media.
    """
    
    def __init__(self, core):
        """
        Initialize pipeline
        
        Args:
            core: PixelleVideoCore instance
        """
        super().__init__(core)
        self.asset_index: Dict[str, Any] = {}  # In-memory asset metadata
    
    async def __call__(
        self,
        assets: List[str],
        video_title: str = "",
        intent: Optional[str] = None,
        style: str = "professional and engaging",
        duration: int = 30,
        source: str = "runninghub",
        bgm_path: Optional[str] = None,
        bgm_volume: float = 0.2,
        bgm_mode: str = "loop",
        **kwargs
    ) -> PipelineContext:
        """
        Execute pipeline with user-provided assets
        
        Args:
            assets: List of asset file paths
            video_title: Video title
            intent: Video intent/purpose (defaults to video_title)
            style: Video style
            duration: Target duration in seconds
            source: Workflow source ("runninghub" or "selfhost")
            bgm_path: Path to background music file (optional)
            bgm_volume: BGM volume (0.0-1.0, default 0.2)
            bgm_mode: BGM mode ("loop" or "once", default "loop")
            **kwargs: Additional parameters
        
        Returns:
            Pipeline context with generated video
        """
        from pixelle_video.pipelines.linear import PipelineContext
        
        # Create custom context with asset-specific parameters
        ctx = PipelineContext(
            input_text=intent or video_title,  # Use intent or title as input_text
            params={
                "assets": assets,
                "video_title": video_title,
                "intent": intent or video_title,
                "style": style,
                "duration": duration,
                "source": source,
                "bgm_path": bgm_path,
                "bgm_volume": bgm_volume,
                "bgm_mode": bgm_mode,
                **kwargs
            }
        )
        
        # Store request parameters in context for easy access
        ctx.request = ctx.params
        
        try:
            # Execute pipeline lifecycle
            await self.setup_environment(ctx)
            await self.determine_title(ctx)
            await self.generate_content(ctx)
            await self.plan_visuals(ctx)
            await self.initialize_storyboard(ctx)
            await self.produce_assets(ctx)
            await self.post_production(ctx)
            await self.finalize(ctx)
            
            return ctx
            
        except Exception as e:
            await self.handle_exception(ctx, e)
            raise
    
    async def setup_environment(self, context: PipelineContext) -> PipelineContext:
        """
        Analyze uploaded assets and build asset index
        
        Args:
            context: Pipeline context with assets list
        
        Returns:
            Updated context with asset_index
        """
        # Create isolated task directory
        task_dir, task_id = create_task_output_dir()
        context.task_id = task_id
        context.task_dir = Path(task_dir)  # Convert to Path for easier usage
        
        # Determine final video path
        context.final_video_path = get_task_final_video_path(task_id)
        
        logger.info(f"📁 Task directory created: {task_dir}")
        logger.info("🔍 Analyzing uploaded assets...")
        
        assets: List[str] = context.request.get("assets", [])
        if not assets:
            raise ValueError("No assets provided. Please upload at least one image or video.")
        
        logger.info(f"Found {len(assets)} assets to analyze")
        
        self.asset_index = {}
        
        for i, asset_path in enumerate(assets, 1):
            asset_path_obj = Path(asset_path)
            
            if not asset_path_obj.exists():
                logger.warning(f"Asset not found: {asset_path}")
                continue
            
            logger.info(f"Analyzing asset {i}/{len(assets)}: {asset_path_obj.name}")
            
            # Determine asset type
            asset_type = self._get_asset_type(asset_path_obj)
            
            if asset_type == "image":
                # Analyze image using ImageAnalysisService
                analysis_source = context.request.get("source", "runninghub")
                description = await self.core.image_analysis(asset_path, source=analysis_source)
                
                self.asset_index[asset_path] = {
                    "path": asset_path,
                    "type": "image",
                    "name": asset_path_obj.name,
                    "description": description
                }
                
                logger.info(f"✅ Image analyzed: {description[:50]}...")
            
            elif asset_type == "video":
                # TODO: Extract keyframes and analyze
                # For MVP, we'll skip video analysis and just record metadata
                self.asset_index[asset_path] = {
                    "path": asset_path,
                    "type": "video",
                    "name": asset_path_obj.name,
                    "description": "Video asset"
                }
                
                logger.info(f"⏭️ Video registered (analysis not yet implemented)")
            
            else:
                logger.warning(f"Unknown asset type: {asset_path}")
        
        logger.success(f"✅ Asset analysis complete: {len(self.asset_index)} assets indexed")
        
        # Store asset index in context
        context.asset_index = self.asset_index
        
        return context
    
    async def determine_title(self, context: PipelineContext) -> PipelineContext:
        """
        Use user-provided title or generate one via LLM
        
        Args:
            context: Pipeline context
        
        Returns:
            Updated context with title
        """
        from pixelle_video.utils.content_generators import generate_title
        
        title = context.request.get("video_title")
        
        if title:
            context.title = title
            logger.info(f"📝 Video title: {title} (user-specified)")
        else:
            # Generate title from intent using LLM
            intent = context.request.get("intent", context.input_text)
            context.title = await generate_title(
                self.core.llm,
                content=intent,
                strategy="llm"
            )
            logger.info(f"📝 Video title: {context.title} (LLM-generated)")
        
        return context
    
    async def generate_content(self, context: PipelineContext) -> PipelineContext:
        """
        Generate video script using LLM with structured output
        
        LLM directly assigns assets to scenes - no complex matching logic needed.
        
        Args:
            context: Pipeline context
        
        Returns:
            Updated context with generated script (scenes already have asset_path assigned)
        """
        logger.info("🤖 Generating video script with LLM...")
        
        # Build prompt for LLM
        intent = context.request.get("intent", context.title)
        style = context.request.get("style", "professional and engaging")
        duration = context.request.get("duration", 30)
        
        # Prepare asset descriptions with full paths for LLM to reference
        asset_info = []
        for asset_path, metadata in self.asset_index.items():
            asset_info.append(f"- Path: {asset_path}\n  Description: {metadata['description']}")
        
        assets_text = "\n".join(asset_info)
        
        prompt = f"""You are a video script writer. Generate a {duration}-second video script.

## Requirements
- Intent: {intent}
- Style: {style}
- Target Duration: {duration} seconds

## Available Assets (use the exact path in your response)
{assets_text}

## Instructions
1. Decide how many scenes are needed based on the target duration (typically 5-15 seconds per scene)
2. For each scene, directly assign ONE asset from the available assets above
3. Each scene can have 1-5 narration sentences
4. Try to use all available assets, but it's OK to reuse if needed
5. Total duration of all scenes should be approximately {duration} seconds

## Output Requirements
For each scene, provide:
- scene_number: Sequential number starting from 1
- asset_path: The EXACT path from the available assets list
- narrations: Array of 1-5 narration sentences
- duration: Estimated duration in seconds

Generate the video script now:"""
        
        # Call LLM with structured output
        script: VideoScript = await self.core.llm(
            prompt=prompt,
            response_type=VideoScript,
            temperature=0.8,
            max_tokens=4000
        )
        
        # Convert to dict format for compatibility with downstream code
        context.script = [scene.model_dump() for scene in script.scenes]
        
        # Validate asset paths exist
        for scene in context.script:
            asset_path = scene.get("asset_path")
            if asset_path not in self.asset_index:
                # Find closest match (in case LLM slightly modified the path)
                matched = False
                for known_path in self.asset_index.keys():
                    if Path(known_path).name == Path(asset_path).name:
                        scene["asset_path"] = known_path
                        matched = True
                        logger.warning(f"Corrected asset path: {asset_path} -> {known_path}")
                        break
                
                if not matched:
                    # Fallback to first available asset
                    fallback_path = list(self.asset_index.keys())[0]
                    logger.warning(f"Unknown asset path '{asset_path}', using fallback: {fallback_path}")
                    scene["asset_path"] = fallback_path
        
        logger.success(f"✅ Generated script with {len(context.script)} scenes")
        
        # Log script preview
        for scene in context.script:
            narrations = scene.get("narrations", [])
            if isinstance(narrations, str):
                narrations = [narrations]
            narration_preview = " | ".join([n[:30] + "..." if len(n) > 30 else n for n in narrations[:2]])
            asset_name = Path(scene.get("asset_path", "unknown")).name
            logger.info(f"Scene {scene['scene_number']} [{asset_name}]: {narration_preview}")
        
        return context
    
    async def plan_visuals(self, context: PipelineContext) -> PipelineContext:
        """
        Prepare matched scenes from LLM-generated script
        
        Since LLM already assigned asset_path in generate_content, this method
        simply converts the script format to matched_scenes format.
        
        Args:
            context: Pipeline context
        
        Returns:
            Updated context with matched_scenes
        """
        logger.info("🎯 Preparing scene-asset mapping...")
        
        # LLM already assigned asset_path to each scene in generate_content
        # Just convert to matched_scenes format for downstream compatibility
        context.matched_scenes = [
            {
                **scene,
                "matched_asset": scene["asset_path"]  # Alias for compatibility
            }
            for scene in context.script
        ]
        
        # Log asset usage summary
        asset_usage = {}
        for scene in context.matched_scenes:
            asset = scene["matched_asset"]
            asset_usage[asset] = asset_usage.get(asset, 0) + 1
        
        logger.info(f"📊 Asset usage summary:")
        for asset_path, count in asset_usage.items():
            logger.info(f"   {Path(asset_path).name}: {count} scene(s)")
        
        return context
    
    async def initialize_storyboard(self, context: PipelineContext) -> PipelineContext:
        """
        Initialize storyboard from matched scenes
        
        Args:
            context: Pipeline context
        
        Returns:
            Updated context with storyboard
        """
        from pixelle_video.models.storyboard import (
            Storyboard,
            StoryboardFrame, 
            StoryboardConfig
        )
        from datetime import datetime
        
        # Extract all narrations in order for compatibility
        all_narrations = []
        for scene in context.matched_scenes:
            narrations = scene.get("narrations", [scene.get("narration", "")])
            if isinstance(narrations, str):
                narrations = [narrations]
            all_narrations.extend(narrations)
        
        context.narrations = all_narrations
        
        # Get template dimensions
        template_name = context.params.get("frame_template", "1080x1920/image_default.html")
        # Extract dimensions from template name (e.g., "1080x1920")
        try:
            dims = template_name.split("/")[0].split("x")
            media_width = int(dims[0])
            media_height = int(dims[1])
        except:
            # Default to 1080x1920
            media_width = 1080
            media_height = 1920
        
        # Create StoryboardConfig
        context.config = StoryboardConfig(
            task_id=context.task_id,
            n_storyboard=len(context.matched_scenes),  # Number of scenes
            min_narration_words=5,
            max_narration_words=50,
            video_fps=30,
            tts_inference_mode="local",
            voice_id=context.params.get("voice_id", "zh-CN-YunjianNeural"),
            tts_speed=context.params.get("tts_speed", 1.2),
            media_width=media_width,
            media_height=media_height,
            frame_template=template_name,
            template_params=context.params.get("template_params")
        )
        
        # Create Storyboard
        context.storyboard = Storyboard(
            title=context.title,
            config=context.config,
            created_at=datetime.now()
        )
        
        # Create StoryboardFrames - one per scene
        for i, scene in enumerate(context.matched_scenes):
            # Get first narration for the frame (we'll combine audios later)
            narrations = scene.get("narrations", [scene.get("narration", "")])
            if isinstance(narrations, str):
                narrations = [narrations]
            
            # Use first narration as the main text (for subtitle)
            # We'll combine all narrations in the audio
            main_narration = " ".join(narrations)  # Combine for subtitle display
            
            frame = StoryboardFrame(
                index=i,
                narration=main_narration,
                image_prompt=None,  # We're using user assets, not generating images
                created_at=datetime.now()
            )
            
            # Store matched asset path in the frame
            frame.image_path = scene["matched_asset"]
            frame.media_type = "image"
            
            # Store scene info for later audio generation
            frame._scene_data = scene  # Temporary storage for multi-narration
            
            context.storyboard.frames.append(frame)
        
        logger.info(f"✅ Created storyboard with {len(context.storyboard.frames)} scenes")
        
        return context
    
    async def produce_assets(self, context: PipelineContext) -> PipelineContext:
        """
        Generate scene videos using FrameProcessor (asset + multiple narrations + template)
        
        Args:
            context: Pipeline context
        
        Returns:
            Updated context with processed frames
        """
        logger.info("🎬 Producing scene videos...")
        
        storyboard = context.storyboard
        config = context.config
        
        for i, frame in enumerate(storyboard.frames, 1):
            logger.info(f"Producing scene {i}/{len(storyboard.frames)}...")
            
            # Get scene data with narrations
            scene = frame._scene_data
            narrations = scene.get("narrations", [scene.get("narration", "")])
            if isinstance(narrations, str):
                narrations = [narrations]
            
            logger.info(f"Scene {i} has {len(narrations)} narration(s)")
            
            # Step 1: Generate audio for each narration and combine
            narration_audios = []
            for j, narration_text in enumerate(narrations, 1):
                audio_path = Path(context.task_dir) / "frames" / f"{i:02d}_narration_{j}.mp3"
                audio_path.parent.mkdir(parents=True, exist_ok=True)
                
                await self.core.tts(
                    text=narration_text,
                    output_path=str(audio_path),
                    voice_id=config.voice_id,
                    speed=config.tts_speed
                )
                
                narration_audios.append(str(audio_path))
                logger.debug(f"  Narration {j}/{len(narrations)}: {narration_text[:30]}...")
            
            # Concatenate all narration audios for this scene
            if len(narration_audios) > 1:
                from pixelle_video.utils.os_util import get_task_frame_path
                
                combined_audio_path = Path(context.task_dir) / "frames" / f"{i:02d}_audio.mp3"
                
                # Use FFmpeg to concatenate audio files
                import subprocess
                
                # Create a file list for FFmpeg concat
                filelist_path = Path(context.task_dir) / "frames" / f"{i:02d}_audiolist.txt"
                with open(filelist_path, 'w') as f:
                    for audio_file in narration_audios:
                        escaped_path = str(Path(audio_file).absolute()).replace("'", "'\\''")
                        f.write(f"file '{escaped_path}'\n")
                
                # Concatenate audio files
                concat_cmd = [
                    'ffmpeg',
                    '-f', 'concat',
                    '-safe', '0',
                    '-i', str(filelist_path),
                    '-c', 'copy',
                    '-y',
                    str(combined_audio_path)
                ]
                
                subprocess.run(concat_cmd, check=True, capture_output=True)
                frame.audio_path = str(combined_audio_path)
                
                logger.info(f"✅ Combined {len(narration_audios)} narrations into one audio")
            else:
                frame.audio_path = narration_audios[0]
            
            # Step 2: Use FrameProcessor to generate composed frame and video
            # FrameProcessor will handle:
            # - Template rendering (with proper dimensions)
            # - Subtitle composition
            # - Video segment creation
            # - Proper file naming in frames/
            
            # Since we already have the audio and image, we bypass some steps
            # by manually calling the composition steps
            
            # Get audio duration for frame duration
            import subprocess
            duration_cmd = [
                'ffprobe',
                '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                frame.audio_path
            ]
            duration_result = subprocess.run(duration_cmd, capture_output=True, text=True, check=True)
            frame.duration = float(duration_result.stdout.strip())
            
            # Use FrameProcessor for proper composition
            processed_frame = await self.core.frame_processor(
                frame=frame,
                storyboard=storyboard,
                config=config,
                total_frames=len(storyboard.frames)
            )
            
            logger.success(f"✅ Scene {i} complete")
        
        return context
    
    async def post_production(self, context: PipelineContext) -> PipelineContext:
        """
        Concatenate scene videos and add BGM
        
        Args:
            context: Pipeline context
        
        Returns:
            Updated context with final video path
        """
        logger.info("🎞️ Concatenating scenes...")
        
        # Collect video segments from storyboard frames
        scene_videos = [frame.video_segment_path for frame in context.storyboard.frames]
        
        final_video_path = Path(context.task_dir) / f"{context.title}.mp4"
        
        # Get BGM parameters
        bgm_path = context.request.get("bgm_path")
        bgm_volume = context.request.get("bgm_volume", 0.2)
        bgm_mode = context.request.get("bgm_mode", "loop")
        
        if bgm_path:
            logger.info(f"🎵 Adding BGM: {bgm_path} (volume={bgm_volume}, mode={bgm_mode})")
        
        self.core.video.concat_videos(
            videos=scene_videos,
            output=str(final_video_path),
            bgm_path=bgm_path,
            bgm_volume=bgm_volume,
            bgm_mode=bgm_mode
        )
        
        context.final_video_path = str(final_video_path)
        context.storyboard.final_video_path = str(final_video_path)
        
        logger.success(f"✅ Final video: {final_video_path}")
        
        return context
    
    async def finalize(self, context: PipelineContext) -> PipelineContext:
        """
        Finalize and return result
        
        Args:
            context: Pipeline context
        
        Returns:
            Final context
        """
        logger.success(f"🎉 Asset-based video generation complete!")
        logger.info(f"Video: {context.final_video_path}")
        
        return context
    
    # Helper methods
    
    def _get_asset_type(self, path: Path) -> str:
        """Determine asset type from file extension"""
        image_exts = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
        video_exts = {".mp4", ".mov", ".avi", ".mkv", ".webm"}
        
        ext = path.suffix.lower()
        
        if ext in image_exts:
            return "image"
        elif ext in video_exts:
            return "video"
        else:
            return "unknown"
    
