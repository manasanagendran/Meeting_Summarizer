# This app helps in summarizing the meeting transript either in the form of text file or audio file

import streamlit as st
from openai import OpenAI
#from pydub import AudioSegment
import os
import config

client = OpenAI(api_key=config.API_KEY)

#Helper function to transcribe audio
def transcribe_audio(audio_file_path):
    with open(audio_file_path, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(model="whisper-1",file=audio_file)
    return transcript.text

# Helper function to generate meeting summary from transcript
def extract_meeting_summary(transcript_text):
    prompt = f"""
You are a professional meeting summarizer. Extract the following from the meeting transcript:

1. Action Items: Include a clear description, the responsible person, and due date if available.
2. Decisions: Clearly state decisions made.
3. Key Takeaways: Summarize the main points discussed.

Output format:

**Action Items:**
- [Action Item 1: Description - Responsible Person - Due Date]
- [Action Item 2: Description - Responsible Person - Due Date]

**Decisions:**
- [Decision 1: Description]
- [Decision 2: Description]

**Key Takeaways:**
- [Key Point 1]
- [Key Point 2]

Only reflect what's in the transcript. Be objective. Do not add opinions or commentary.

Transcript:
\"\"\"
{transcript_text}
\"\"\"
"""
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    return response.choices[0].message.content.strip()


# Streamlit UI
st.title("Meeting Summary Extractor")

uploaded_file = st.file_uploader("Upload Transcript (TXT) or Audio File (MP3/WAV)", type=["txt", "mp3", "wav"])

if uploaded_file is not None:
    file_extension = uploaded_file.name.split(".")[-1].lower()
    transcript_text = ""

    if file_extension == "txt":
        transcript_text = uploaded_file.read().decode("utf-8")

    elif file_extension in ["mp3", "wav"]:
        with open("temp_audio." + file_extension, "wb") as f:
            f.write(uploaded_file.read())
        transcript_text = transcribe_audio("temp_audio." + file_extension)
        os.remove("temp_audio." + file_extension)

    if transcript_text:
        st.subheader("Transcript Preview:")
        st.text_area("", transcript_text, height=200)

        with st.spinner("Analyzing meeting content..."):
            summary = extract_meeting_summary(transcript_text)

        st.subheader("📝 Structured Meeting Summary")
        st.markdown(summary)
