import streamlit as st
import whisper
from moviepy.editor import VideoFileClip
import tempfile
import os

# -----------------------------
# Page Configuration
# -----------------------------
st.set_page_config(
    page_title="Video to Text Converter",
    page_icon="🎥",
    layout="centered"
)

# -----------------------------
# Custom Styling
# -----------------------------
st.markdown("""
    <style>
    .stApp {
        max-width: 800px;
        margin: auto;
    }
    .title {
        text-align: center;
        color: #4CAF50;
        font-size: 2.5rem;
        margin-bottom: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='title'>🎥 Video to Text Converter</div>", unsafe_allow_html=True)
st.write("Upload a video and get instant transcription using Whisper AI.")

# -----------------------------
# Sidebar Settings
# -----------------------------
with st.sidebar:
    st.header("⚙️ Settings")

    model_size = st.selectbox(
        "Model Size",
        ["tiny", "base", "small", "medium"],
        index=1
    )

    st.markdown("---")
    st.info({
        "tiny": "Fastest, least accurate",
        "base": "Fast, good accuracy (Recommended)",
        "small": "Balanced speed/accuracy",
        "medium": "High accuracy, slower"
    }[model_size])

# -----------------------------
# Cache Model (IMPORTANT)
# -----------------------------
@st.cache_resource
def load_model(size):
    return whisper.load_model(size, device="cpu")  # CPU safe for cloud

# -----------------------------
# File Upload
# -----------------------------
uploaded_file = st.file_uploader(
    "Upload Video",
    type=["mp4", "avi", "mov", "mkv", "webm", "m4v"]
)

if uploaded_file is not None:

    file_size = len(uploaded_file.getvalue()) / (1024 * 1024)

    col1, col2 = st.columns(2)

    with col1:
        st.video(uploaded_file)

    with col2:
        st.write("**File Details:**")
        st.write(f"Name: {uploaded_file.name}")
        st.write(f"Size: {file_size:.2f} MB")

    if st.button("🚀 Start Transcription", type="primary", use_container_width=True):

        video_path = None
        audio_path = None

        try:
            progress = st.progress(0)
            status = st.empty()

            # -----------------------------
            # Save Uploaded Video
            # -----------------------------
            status.text("Saving video...")
            progress.progress(10)

            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_video:
                tmp_video.write(uploaded_file.read())
                video_path = tmp_video.name

            # -----------------------------
            # Extract Audio
            # -----------------------------
            status.text("Extracting audio...")
            progress.progress(30)

            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_audio:
                audio_path = tmp_audio.name

            video = VideoFileClip(video_path)

            if video.audio is None:
                raise Exception("This video has no audio track.")

            video.audio.write_audiofile(audio_path, logger=None)
            video.close()

            # -----------------------------
            # Load Model
            # -----------------------------
            status.text("Loading Whisper model...")
            progress.progress(50)

            model = load_model(model_size)

            # -----------------------------
            # Transcribe
            # -----------------------------
            status.text("Transcribing... Please wait")
            progress.progress(70)

            result = model.transcribe(audio_path)
            transcript = result["text"]

            progress.progress(100)
            status.text("Transcription complete!")

            st.success("✅ Transcription completed successfully!")

            with st.expander("📄 View Transcript", expanded=True):
                st.text_area("Transcript", transcript, height=300)

            st.download_button(
                "⬇️ Download Transcript",
                transcript,
                file_name=f"{uploaded_file.name.rsplit('.',1)[0]}_transcript.txt",
                mime="text/plain",
                use_container_width=True
            )

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

        finally:
            # -----------------------------
            # Cleanup
            # -----------------------------
            if video_path and os.path.exists(video_path):
                os.remove(video_path)

            if audio_path and os.path.exists(audio_path):
                os.remove(audio_path)

# -----------------------------
# Footer
# -----------------------------
st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:gray;'>"
    "Files are processed temporarily and deleted automatically."
    "</div>",
    unsafe_allow_html=True
)
