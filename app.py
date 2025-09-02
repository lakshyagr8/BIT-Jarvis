import streamlit as st
import asyncio
import groq
import tempfile
import os
import time
from utils import initialize_vectorstore, format_docs, rag_prompt
from tavily_integration import web_response
from sklearn.feature_extraction.text import TfidfVectorizer

from dotenv import load_dotenv
load_dotenv()

# Set page configuration
st.set_page_config(
    page_title="ABC - Chatbot",
    page_icon="🔤",
    layout="wide"
)

if "page" not in st.session_state:
    st.session_state.page = None


suggested_questions = [
    "What micro-specializations can I do at BIT Mesra?",
    "What are the hostel facilities like at BIT Mesra?",
    "Where can I find the academic calendar?",
    "How do I apply for a minor degree?",
    "How does the placement process work?"
]
# Custom CSS for styling
st.markdown("""
    <style>
    @keyframes shake {
        0% { transform: translateX(0); }
        25% { transform: translateX(-5px); }
        50% { transform: translateX(5px); }
        75% { transform: translateX(-5px); }
        100% { transform: translateX(0); }
    }
    @keyframes textShine {
        0% { background-position: 0% 50%;}
        100% { background-position: 100% 50%;}
    }
    .shake {
        animation: shake 0.3s ease-in-out 2;
        background-color: #ffcccc !important;
        border: 2px solid red !important;
        border-radius: 5px;
        padding: 5px;
    }
    body { 
        background-color: #18191A; 
        color: white; 
    }
    .stApp { background-color: #18191A; }
    .chat-row { display: flex; margin: 5px; width: 100%; }
    .row-reverse {flex-direction: row-reverse;}
    .chat-bubble {
        padding: 12px 18px;
        border-radius: 20px;
        max-width: 70%;
        box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
        word-wrap: break-word;
        margin-bottom: 5px; /* Added margin for padding between messages */
    }   
    .user { 
        background-color: #0093E9; 
        background-image: linear-gradient(160deg, #0093E9 0%, #80D0C7 100%); 
        color: white; font-size: 1.25em
    }
    .assistant { 
        background-color: transparent; 
        color: white; font-size: 1.25em
    }
    .thinking { 
        background-color: #3A3B3C; color: white; 
        padding: 10px; border-radius: 10px; 
        font-style: italic; max-width: 70%; 
        font-size: 1.25em
    }
    .response { 
        background-color: transparent; 
        color: white; padding: 10px; 
        border-radius: 10px; 
        margin-top: 5px; 
        max-width: 70%; 
        font-size: 1.25em
    }
    .temp { 
        background: linear-gradient(90deg, rgba(138,137,137,1) 0%, rgba(255,255,255,1) 86%);
        background-clip: text;
        background-size: 500% auto;
        -webkit-background-clip: text; 
        -webkit-text-fill-color: transparent;
        text-fill-color: transparent; 
        animation: textShine 1s ease-in-out infinite alternate;
        background-color: #3A3B3C; 
        color: white; padding: 10px; 
        border-radius: 10px; 
        font-style: italic; 
        max-width: 70%; 
        font-size: 1.25em; 
        opacity: 1;
        will-change: background-position;
    }
    div[data-testid="stBottomBlockContainer"] {
        background-color: #18191A !important;
    }
    input[type="text"] { background-color: #242526; color: white; border-radius: 10px; padding: 10px; border: none; width: 100%; font-size: 1.25em}
    
    div[data-testid="stChatInput"] textarea {
        background-color: #242526;
        color: white;
        border-radius: 16px;
        padding: 15px;
        font-size: 1.25em;
        box-shadow: 0 0 8px rgba(84, 192, 255, 0.5);
    }
    div[data-testid="stChatInput"] button {
        position: absolute;
        right: 12px;
        top: 50%;
        transform: translateY(-50%);
        background-color: transparent;
        color: #ccc;
    }
        </style>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.title("🤖 Query LLM App")
st.sidebar.markdown('<h2 style="color: #54c0ff;">About</h2>', unsafe_allow_html=True)
st.sidebar.write("An AI-powered chatbot for BITians 🎓")

col1, col2 = st.sidebar.columns(2)
with col1:
    if st.button("How to Use", key="how_to_use_btn"):
        st.session_state.page = 'how_to_use'



if st.session_state.page == "how_to_use":
    from how_to_use import how_to_use
    how_to_use()
    st.stop()

if st.session_state.page == "about_us":
    from about_us import about_us
    about_us()
    st.stop()


# Upload file section in sidebar
st.sidebar.markdown('<h2 style="color: #54c0ff;">Upload a File</h2>', unsafe_allow_html=True)
uploaded_file = st.sidebar.file_uploader("", type=["txt", "pdf", "docx"])


# Toggle button in sidebar
toggle = st.sidebar.toggle("Document-only Mode")

st.sidebar.markdown("---")
st.sidebar.markdown("#### Technologies:")
st.sidebar.write("- Streamlit 🌐")
st.sidebar.write("- Open-Source LLM 🧠")
st.sidebar.write("- Groq ⚙️")
st.sidebar.write("- Tavily 🔍")



# Cache vector store initialization
# @st.cache_resource
# def get_vectorstore():
#     with st.spinner("Loading vector store... ⏳"):
#         return initialize_vectorstore()

@st.cache_resource
def get_vectorstore(files=None):
    with st.spinner("Loading vector store... ⏳"):
        return initialize_vectorstore(files=files)

vectorstore, retriever = get_vectorstore()

# Main app title
st.markdown('<h2 class="main-title">Hi There! 👋 How Can I Help You Today? 🚀</h2>', unsafe_allow_html=True)
if "messages" not in st.session_state:
    st.session_state.messages = []

cols = st.columns(len(suggested_questions))
for i, question in enumerate(suggested_questions):
    if cols[i].button(question, key=f"question_{i}"):
        st.session_state["selected_question"] = question



for message in st.session_state.messages:
    role_class = "user" if message["role"] == "user" else "assistant"
    content = message["content"]
    div = f"""
<div class="chat-row 
    {'' if role_class == 'assistant' else 'row-reverse'}">
    <div class="chat-bubble
    {'assistant' if role_class == 'assistant' else 'user'}">
        &#8203;{content}
    </div>
</div>
        """
    st.markdown(div, unsafe_allow_html=True)           

# Handle toggle behavior
if toggle:
    if uploaded_file is None:
        # Apply shake effect using HTML
        st.sidebar.markdown('<div class="shake">⚠️ File required for Document-only mode!</div>', unsafe_allow_html=True)
        time.sleep(0.5)  # Brief delay for animation
    else:
        # Show success notification (pops up briefly)
        st.toast("Document-only mode activated!", icon="✅")
        time.sleep(0.5)  # Short visibility time
else:
    if "file_upload" in st.session_state:
        st.toast("⚠️ Document-only mode deactivated!", icon="⚠️")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")# Replace with your actual Groq API key
# Groq client
client = groq.Groq(api_key=GROQ_API_KEY)

async def process_input(prompt):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    div = f"""
<div class="chat-row row-reverse">
    <div class="chat-bubble user">
        &#8203;{prompt}
    </div>
</div>
        """
    st.markdown(div, unsafe_allow_html=True)

    #Loading Screen
    thinking_container = st.empty()
    thinking_container.markdown('<div class="temp"> Processing your query ....</div>', unsafe_allow_html=True)

    # st.markdown(f'<div class="chat-bubble user">{prompt}</div>', unsafe_allow_html=True)

    # Initialize variables for document processing
    docs_txt = ""
    temp_file_path = None
    document_vectorstore = None
    document_retriever = None
    
    # Process uploaded document if available and toggle is on
    if uploaded_file is not None and toggle:
        # Create a temporary file to store the uploaded content
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as temp_file:
            temp_file.write(uploaded_file.getbuffer())
            temp_file_path = temp_file.name
        
        try:
            # Create a separate vector store for the uploaded document
            thinking_container.markdown('<div class="temp"> Finding answers for the query in the document....</div>', unsafe_allow_html=True)
            document_vectorstore, document_retriever = initialize_vectorstore(files=[temp_file_path])
        except Exception as e:
            st.error(f"Error processing document: {str(e)}")
            if temp_file_path and os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
            return
    
    # Decide sources based on toggle state
    if toggle and uploaded_file is not None and document_retriever:
        try:
            # Document-only mode: use only the uploaded document
            document_docs = await asyncio.to_thread(document_retriever.invoke, prompt)
            docs_txt = format_docs(document_docs)
        finally:
            # Clean up the temporary file
            if temp_file_path and os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
    else:
        # Standard mode: use only knowledge base and web search (no uploaded document)
        # Retrieve relevant documents from general knowledge base
        docs = await asyncio.to_thread(retriever.invoke, prompt)
        docs_re = format_docs(docs)

        # Perform web search
        web_search_results = await asyncio.to_thread(web_response, prompt)
        docs_txt = docs_re + "\n\n" + web_search_results
        
        # Apply TF-IDF filtering
        vectorizer = TfidfVectorizer()
        vectorizer.fit_transform([prompt, docs_txt])
        feature_names = vectorizer.get_feature_names_out()

        filtered_docs = []
        web_results_filtered = ""

        for doc in docs:
            for word in feature_names:
                if word in doc.page_content:
                    filtered_docs.append(doc)
                    break
        
        sentences = web_search_results.split(".")
        for sentence in sentences:
            for word in feature_names:
                if word in sentence:
                    web_results_filtered += sentence + "."
                    break

        docs_txt = format_docs(filtered_docs) + "\n\n" + web_results_filtered

    # Format the prompt for the model (request JSON response)
    rag_prompt_formatted = rag_prompt.format(context=docs_txt, question=prompt)
    
    # Add source indicators for clarity
    if toggle and uploaded_file is not None:
        rag_prompt_formatted += "\n\nNOTE: Please answer based ONLY on the content from the uploaded document."
    
    rag_prompt_formatted += "\n\nRespond with a JSON object containing 'thought' and 'answer' fields."

    # Groq API call
    chat_completion = client.chat.completions.create(
        model="llama3-70b-8192",  # Use a supported Groq model
        messages=[
            {
                "role": "user",
                "content": rag_prompt_formatted,
            }
        ],
        response_format={"type": "json_object"}
    )

    response_content = chat_completion.choices[0].message.content

    # Parse JSON response
    try:
        import json
        response_json = json.loads(response_content)
        thinking = response_json.get("thought", "No thought provided.")
        response_text = response_json.get("answer", "No answer provided.")

    except (json.JSONDecodeError, AttributeError):
        thinking = "Error parsing response."
        response_text = response_content  # Fallback to raw response, if json fails

    # Initialize containers for dynamic updates
    response_container = st.empty()

    # Function to stream thinking dynamically
    async def stream_thinking():
        full_thinking = ""
        words = thinking.split()
        for word in words:
            full_thinking += word + " "
            thinking_container.markdown(f'<div class="thinking">🤔 Thinking: {full_thinking}</div>', unsafe_allow_html=True)
            await asyncio.sleep(0.05)

    # Function to stream response dynamically
    async def stream_response():
        full_response = ""
        words = str(response_text).split()
        for word in words:
            full_response += word + " "
            response_container.markdown(f'<div class="response">{full_response}</div>', unsafe_allow_html=True)
            await asyncio.sleep(0.05)

    # Run both thinking and response streams asynchronously
    await stream_thinking()
    await stream_response()

    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response_text})


            
# Handle user input asynchronously
if prompt := st.chat_input("Ask me anything about KGP! 🤔") or "selected_question" in st.session_state:
    asyncio.run(process_input(st.session_state.pop("selected_question", prompt)))