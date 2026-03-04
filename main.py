import streamlit as st
import subprocess
import sys
import os

# Install whisper at runtime if not available (fallback method)
try:
    import whisper
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "openai-whisper"])
    import whisper

import tempfile
from moviepy.editor import VideoFileClip
import time

# Page configuration
st.set_page_config(
    page_title="Video to Text Converter",
    page_icon="🎥",
    layout="centered"
)

# Custom CSS
st.markdown("""
    <style>
    .stApp {
        max-width: 800px;
        margin: 0 auto;
    }
    .main-title {
        text-align: center;
        color: #4CAF50;
        font-size: 2.5rem;
        margin-bottom: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.markdown("<h1 class='main-title'>🎥 Video to Text Converter</h1>", unsafe_allow_html=True)
st.markdown("Upload any video file and get instant text transcription!")

# Sidebar settings
with st.sidebar:
    st.header("⚙️ Settings")
    model_size = st.selectbox(
        "Model Size",
        ["tiny", "base", "small", "medium"],
        index=1,
        help="Larger models = better accuracy but slower"
    )
    
    st.markdown("---")
    st.markdown("### 📊 Model Info")
    model_info = {
        "tiny": "Fastest, least accurate (39 MB)",
        "base": "Fast, good accuracy (74 MB) ✓ Recommended",
        "small": "Balanced speed/accuracy (244 MB)",
        "medium": "Slower, high accuracy (769 MB)"
    }
    st.info(model_info[model_size])
    
    st.markdown("---")
    st.markdown("### 📝 Instructions")
    st.markdown("""
    1. Upload video (MP4, AVI, MOV, MKV)
    2. Click 'Start Transcription'
    3. Wait for processing
    4. Download transcript
    """)

# Main content
uploaded_file = st.file_uploader(
    "Choose a video file",
    type=['mp4', 'avi', 'mov', 'mkv', 'webm', 'm4v'],
    help="Maximum file size: 200MB"
)

if uploaded_file is not None:
    # Display video info
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.video(uploaded_file)
    
    with col2:
        file_size = len(uploaded_file.getvalue()) / (1024 * 1024)
        st.markdown("**📁 File Details:**")
        st.markdown(f"- **Name:** {uploaded_file.name}")
        st.markdown(f"- **Size:** {file_size:.2f} MB")
        st.markdown(f"- **Type:** {uploaded_file.type}")
        
        if file_size > 100:
            st.warning("⚠️ Large file may take longer to process")
    
    # Transcription button
    if st.button("🚀 Start Transcription", type="primary", use_container_width=True):
        try:
            # Progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Save uploaded file
            status_text.text("📁 Saving video...")
            progress_bar.progress(10)
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                video_path = tmp_file.name
            
            # Extract audio
            status_text.text("🎵 Extracting audio...")
            progress_bar.progress(30)
            
            audio_path = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3').name
            video = VideoFileClip(video_path)
            video.audio.write_audiofile(audio_path, logger=None, verbose=False)
            video.close()
            
            # Load Whisper model
            status_text.text(f"🤖 Loading {model_size} model...")
            progress_bar.progress(50)
            
            # Load model with progress indication
            model = whisper.load_model(model_size)
            
            # Transcribe
            status_text.text("📝 Transcribing audio... This may take a few minutes")
            progress_bar.progress(70)
            
            result = model.transcribe(audio_path)
            transcribed_text = result["text"]
            
            # Clean up temporary files
            status_text.text("🧹 Cleaning up...")
            os.unlink(video_path)
            os.unlink(audio_path)
            
            # Complete
            progress_bar.progress(100)
            status_text.text("✅ Transcription complete!")
            
            # Display results
            st.success("✅ Transcription completed successfully!")
            
            # Show transcript in expander
            with st.expander("📄 View Transcript", expanded=True):
                st.text_area("Transcript Text", transcribed_text, height=300)
            
            # Download button
            st.download_button(
                label="⬇️ Download Transcript (TXT)",
                data=transcribed_text,
                file_name=f"{uploaded_file.name.split('.')[0]}_transcript.txt",
                mime="text/plain",
                use_container_width=True
            )
            
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.info("Try a different video format or smaller file size")
            
            # Clean up if files exist
            try:
                if 'video_path' in locals():
                    os.unlink(video_path)
                if 'audio_path' in locals():
                    os.unlink(audio_path)
            except:
                pass

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>"
    "Made with ❤️ using AI | Files are processed temporarily and deleted"
    "</div>", 
    unsafe_allow_html=True
)
