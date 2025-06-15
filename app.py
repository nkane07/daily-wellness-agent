import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os
import pandas as pd
import altair as alt
from datetime import datetime

# Load environment variables
load_dotenv()

# Create OpenAI client
client = OpenAI()

# Page config
st.set_page_config(page_title="Daily Wellness Agent", page_icon="🌸", layout="centered")

# Load custom CSS
with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# --- DARK MODE TOGGLE ---
dark_mode = st.sidebar.toggle("🌙 Dark Mode")
if dark_mode:
    st.markdown("<style>body { background: #121212 !important; color: #e0e0e0 !important; }</style>", unsafe_allow_html=True)

# --- PERSONALISATION SIDEBAR ---
st.sidebar.markdown("## 🧑‍💻 Personalise Your Agent")

if st.sidebar.button("🔄 Reset Agent"):
    st.session_state.clear()
    st.rerun()

# Name input + save
with st.sidebar.form("name_form"):
    name_input = st.text_input("Enter your name:", value=st.session_state.get("username", ""))
    save_name = st.form_submit_button("✅ Save")
    if save_name:
        if name_input.strip():
            st.session_state["username"] = name_input.strip()
            st.success("Name saved!")
            st.rerun()
        else:
            st.warning("Please enter a name before saving.")

# Use stored name or fallback
user = st.session_state.get("username", "").strip()
display_name = user if user else "Friend"

# --- HEADER ---
st.markdown(f"<h1 class='title'>🌸 Welcome back, {display_name} 👋</h1>", unsafe_allow_html=True)
st.markdown("<h4 class='subtitle'>Start your day with a personalised mental boost 💡</h4>", unsafe_allow_html=True)
st.markdown("### &nbsp;")

# --- INPUT SECTION ---
st.markdown("### 🧘 How are you feeling today?")

with st.form("mood_form"):
    col1, col2 = st.columns([4, 1])
    with col1:
        user_mood = st.text_input("Your mood (e.g., tired, anxious, motivated)...", label_visibility="collapsed")
    with col2:
        submitted = st.form_submit_button("Get Guidance")

# --- RESPONSE GENERATION ---
if submitted and user_mood:
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

        st.session_state["last_output"] = response.choices[0].message.content
        st.session_state["last_mood"] = user_mood
        st.rerun()

# --- DISPLAY RESPONSE + SAVE TO JOURNAL ---
if "last_output" in st.session_state and "last_mood" in st.session_state:
    output = st.session_state["last_output"]
    user_mood = st.session_state["last_mood"]

    st.markdown("---")
    st.markdown("<div class='card fade-in'>", unsafe_allow_html=True)
    st.markdown("### 🌿 Your Wellness Plan for Today")
    st.markdown(f"<p>{output.replace(chr(10), '<br>')}</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    if st.button("💾 Save to Journal"):
        if not user:
            st.warning("Please enter and save your name before saving to the journal.")
            st.stop()

        entry = {
            "timestamp": datetime.now().isoformat(),
            "user": user,
            "mood": user_mood,
            "summary": output.splitlines()[0] if output else "",
            "full_response": output
        }

        os.makedirs("journal", exist_ok=True)
        csv_path = "journal/journal.csv"

        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            df = pd.concat([df, pd.DataFrame([entry])], ignore_index=True)
        else:
            df = pd.DataFrame([entry])

        df.to_csv(csv_path, index=False)
        st.success("Entry saved to journal!")

        del st.session_state["last_output"]
        del st.session_state["last_mood"]
        st.rerun()

# --- MOOD HISTORY ---
st.markdown("### 📖 Mood History")

csv_path = "journal/journal.csv"
if os.path.exists(csv_path):
    df = pd.read_csv(csv_path)
    if user:
        recent = df[df["user"] == user].tail(5)
    else:
        recent = pd.DataFrame()

    if not recent.empty:
        for _, row in recent[::-1].iterrows():
            st.markdown(f"""
                <div class='card'>
                <strong>{row['timestamp']}</strong><br>
                <em>Mood:</em> {row['mood']}<br>
                <em>Summary:</em> {row['summary']}
                </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No entries found for this user yet. Try saving your first mood.")
else:
    st.info("Your mood journal will appear here after saving your first entry.")

# --- MOOD ANALYTICS ---
st.markdown("### 📊 Mood Analytics")

if os.path.exists(csv_path):
    df = pd.read_csv(csv_path)
    if user:
        user_df = df[df["user"] == user].copy()

        if not user_df.empty:
            user_df["timestamp"] = pd.to_datetime(user_df["timestamp"])
            user_df = user_df.sort_values("timestamp")

            # --- Mood Over Time Chart (Altair) ---
            st.markdown("#### Mood Over Time")

            mood_over_time_data = user_df[["timestamp", "mood"]]
            mood_chart = alt.Chart(mood_over_time_data).mark_line(point=True).encode(
                x=alt.X("timestamp:T", title="Date"),
                y=alt.Y("mood:N", title="Mood"),
                color=alt.Color("mood:N", title="Mood"),
                tooltip=["timestamp:T", "mood:N"]
            ).properties(
                width=700,
                height=300
            )

            st.altair_chart(mood_chart, use_container_width=True)

            # --- Most Frequent Moods Chart (Altair) ---
            st.markdown("#### Most Frequent Moods")

            bar_data = user_df["mood"].value_counts().reset_index()
            bar_data.columns = ["mood", "count"]

            bar_chart = alt.Chart(bar_data).mark_bar().encode(
                x=alt.X("mood:N", title="Mood"),
                y=alt.Y("count:Q", title="Frequency"),
                color=alt.Color("mood:N", title="Mood"),
                tooltip=["mood:N", "count:Q"]
            ).properties(
                width=700,
                height=300
            )

            st.altair_chart(bar_chart, use_container_width=True)
        else:
            st.info("No mood data found for this user yet.")
    else:
        st.info("Please enter and save your name in the sidebar to view your analytics.")
else:
    st.info("Your analytics will appear once you start saving mood entries.")

# --- FOOTER ---
st.markdown("### &nbsp;")
st.markdown("""
    <hr style="margin-top: 3em;">
    <div class='footer'>
        Built with ❤️ by Niamh Kane · 
        <a href='https://github.com/nkane07' target='_blank'>View on GitHub</a>
    </div>
""", unsafe_allow_html=True)
