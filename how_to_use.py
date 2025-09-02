import streamlit as st

def how_to_use():
    # st.set_page_config(page_title="How to Use", page_icon="📖", layout="wide")
    st.title("📖 How to Use the Chatbot")

    st.markdown(
        """
        Welcome to the **Jarvis**! Here’s how you can make the most of it:
        """
    )

    st.divider()

    # Step 1: Asking a question
    st.subheader("📝 Step 1: Ask a Question")
    st.markdown(
        """
        - Type your question in the input box at the bottom.
        - You can ask about **BIT rules, hostel life, placements, academics,** and more!
        - Click **Enter** or **Submit** to get an answer.
        """
    )

    st.info("💡 Tip: You can also click on suggested questions for quick queries!")

    st.divider()

    # Step 2: Uploading Documents
    st.subheader("📂 Step 2: Upload Documents (Optional)")
    st.markdown(
        """
        - Need document-based responses? Use the **Upload a File** section in the sidebar.
        - Supported formats: **PDF, TXT, DOCX**
        - Toggle **Document-only Mode** to focus on your uploaded files.
        """
    )

    st.warning("⚠️ Ensure the document contains clear, structured information for best results.")

    st.divider()

    # Step 3: Understanding Responses
    st.subheader("🤖 Step 3: Getting Answers")
    st.markdown(
        """
        - The AI will analyze your query and provide an accurate response.
        - If the response seems unclear, **rephrase** your question.
        - You can also **ask follow-up questions** for more details.
        """
    )

    st.success("✅ Responses are AI-generated using real-time retrieval techniques!")

    st.divider()

    # Back button
    st.button("🏠 Back to Home", on_click=lambda: st.session_state.update(page=None))
