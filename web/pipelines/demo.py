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
Demo Pipeline UI

Implements a custom layout for the Demo Pipeline.
"""

import streamlit as st
from typing import Any
from web.i18n import tr

from web.pipelines.base import PipelineUI, register_pipeline_ui


class DemoPipelineUI(PipelineUI):
    """
    Demo UI to verify the full-page plugin system.
    Uses a completely different layout (2 columns).
    """
    name = "demo"
    icon = "✨"
    
    @property
    def display_name(self):
        return tr("pipeline.demo.name")
        
    @property
    def description(self):
        return tr("pipeline.demo.description")
    
    def render(self, pixelle_video: Any):
        st.markdown("### ✨ Demo Pipeline Custom Layout")
        st.info("This pipeline uses a custom 2-column layout, demonstrating full UI control.")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            with st.container(border=True):
                st.subheader("1. Input")
                topic = st.text_input("Enter Topic", placeholder="e.g. AI News")
                mood = st.selectbox("Mood", ["Happy", "Serious", "Funny"])
                
                st.markdown("---")
                st.subheader("2. Settings")
                # Simplified settings for demo
                n_scenes = st.slider("Scenes", 3, 10, 5)
        
        with col2:
            with st.container(border=True):
                st.subheader("3. Generate")
                if st.button("🚀 Generate Demo Video", type="primary", use_container_width=True):
                    # Mock generation logic or call backend
                    st.success(f"Generating video for '{topic}' ({mood}) with {n_scenes} scenes...")
                    st.balloons()


# Register self
register_pipeline_ui(DemoPipelineUI)
