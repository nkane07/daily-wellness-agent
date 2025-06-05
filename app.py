import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os

# Load the OpenAI API key from the .env file
load_dotenv()

# Create the OpenAI client
client = OpenAI()

# Set up your Streamlit app
st.set_page_config(page_title="Daily Wellness Agent", page_icon="🌿", layout="centered")

# Load external CSS
with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Title and intro
st.markdown("<h1 style='text-align: center;'>🌞 Daily Wellness Agent</h1>", unsafe_allow_html=True)
st.markdown("### 🧘 How are you feeling today?")
user_mood = st.text_input("Your mood (e.g., tired, anxious, motivated)...")

# Generate guidance
if st.button("Get Guidance") and user_mood:
    with st.spinner("Thinking..."):
        prompt = f"""
        You're a kind and empathetic AI wellness assistant.
        The user is feeling: "{user_mood}"

        Give them:
        1. A helpful daily goal (1 line)
        2. A short motivational quote
        3. A journaling or self-care prompt

        Use emoji icons: ✅ for goal, 💬 for quote, and ✍️ for journaling.
        Keep it warm, supportive, and encouraging.
        """

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.8
        )

        output = response.choices[0].message.content

        # Display with animation
        st.markdown("---")
        st.markdown("### 🌿 Your Wellness Plan for Today")
        st.markdown(f"<div class='fade-in'><p>{output.replace(chr(10), '<br>')}</p></div>", unsafe_allow_html=True)
        st.markdown("---")

# Footer
st.markdown("""
    <hr style="margin-top: 3em;">
    <div style='text-align: center; font-size: 14px; color: #666;'>
        Built with ❤️ by Niamh Kane · 
        <a href='https://github.com/nkane07' target='_blank'>View on GitHub</a>
    </div>
""", unsafe_allow_html=True)
