import streamlit as st
import whisper
import tempfile
import os
from moviepy.editor import VideoFileClip
import time

# Page config
st.set_page_config(
    page_title="Video to Text Converter",
    page_icon="🎥",
    layout="centered"
)

# Custom CSS for better look
st.markdown("""
    <style>
    .stApp {
        max-width: 800px;
        margin: 0 auto;
    }
    .upload-box {
        border: 2px dashed #4CAF50;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# Title and description
st.title("🎥 Video to Text Converter")
st.markdown("Upload any video and get instant text transcription!")

# Sidebar for settings
with st.sidebar:
    st.header("⚙️ Settings")
    model_size = st.selectbox(
        "Select Model Size",
        ["tiny", "base", "small", "medium"],
        index=1,
        help="Larger models = better accuracy but slower"
    )
    st.markdown("---")
    st.markdown("### How it works:")
    st.markdown("1. Upload video file")
    st.markdown("2. Wait for processing")
    st.markdown("3. Download transcript")
    st.markdown("---")
    st.markdown("Made with ❤️ using AI")

# Main content
uploaded_file = st.file_uploader(
    "Choose a video file",
    type=['mp4', 'avi', 'mov', 'mkv', 'webm'],
    help="Maximum file size: 200MB"
)

if uploaded_file is not None:
    # Create columns for better layout
    col1, col2 = st.columns(2)

    with col1:
        st.video(uploaded_file)

    with col2:
        st.write("**File details:**")
        st.write(f"📁 Name: {uploaded_file.name}")
        st.write(f"📊 Size: {len(uploaded_file.getvalue()) / (1024 * 1024):.2f} MB")

        if st.button("🚀 Start Transcription", type="primary", use_container_width=True):
            # Progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()

            try:
                # Save uploaded file temporarily
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

                # Load model
                status_text.text(f"🤖 Loading AI model ({model_size})...")
                progress_bar.progress(50)
                model = whisper.load_model(model_size)

                # Transcribe
                status_text.text("📝 Transcribing... This may take a few minutes...")
                progress_bar.progress(70)

                result = model.transcribe(audio_path)
                text = result["text"]

                # Save text
                status_text.text("💾 Preparing download...")
                progress_bar.progress(90)

                text_path = tempfile.NamedTemporaryFile(delete=False, suffix='.txt', mode='w', encoding='utf-8').name
                with open(text_path, 'w', encoding='utf-8') as f:
                    f.write(text)

                # Clean up temp files
                os.unlink(video_path)
                os.unlink(audio_path)

                # Complete
                progress_bar.progress(100)
                status_text.text("✅ Complete!")

                # Show results
                st.success("Transcription completed successfully!")

                # Display transcript
                with st.expander("📄 View Transcript", expanded=True):
                    st.write(text)

                # Download button
                with open(text_path, 'r', encoding='utf-8') as f:
                    st.download_button(
                        label="⬇️ Download Transcript (TXT)",
                        data=f,
                        file_name=f"{uploaded_file.name.split('.')[0]}_transcript.txt",
                        mime="text/plain",
                        use_container_width=True
                    )

                # Clean up text file
                os.unlink(text_path)

            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                progress_bar.empty()
                status_text.empty()

# Footer
st.markdown("---")
st.markdown("⚠️ **Note:** Processing time depends on video length and model size.")