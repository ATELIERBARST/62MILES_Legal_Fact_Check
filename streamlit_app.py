import streamlit as st
import openai
from PyPDF2 import PdfReader

# Fetch the OpenAI API key from Streamlit secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]

# CSS for styling
st.markdown(
    """
    <style>
        .main { padding-top: 0px !important; padding-bottom: 0px !important; }
        .block-container { padding-top: 80px !important; }
        #logo-container { text-align: left; margin-top: 0px !important; padding: 0px !important; }
    </style>
    <div id="logo-container">
        <img src="https://img.freesvglogo.com/upload/r/rT7/62miles.svg.@ERESIZE@.preview.png" alt="62 Miles Logo" style="width: 300px; margin: 0;">
    </div>
    """,
    unsafe_allow_html=True,
)

# App Title and Description
st.title("🛡️ Legal Fact Checker")
st.write(
    "Welcome, colleague! This tool helps you assess whether you can safely use the output "
    "of an AI tool for commercial purposes. Simply paste a legal text or upload a file, "
    "such as a 'terms of use' document, and receive instant advice!"
)

# File upload and text input
uploaded_file = st.file_uploader("Upload a legal document (PDF or TXT):", type=["pdf", "txt"])
document = ""  # Initialize the document variable

if uploaded_file:
    if uploaded_file.name.endswith(".txt"):
        document = uploaded_file.read().decode("utf-8")
    elif uploaded_file.name.endswith(".pdf"):
        pdf_reader = PdfReader(uploaded_file)
        document = "".join(page.extract_text() for page in pdf_reader.pages)
    st.write("**Content of the uploaded document:**")
    st.write(document)
else:
    document = st.text_area("Or paste the legal text here.")

# Analyze button
if st.button("Analyze text"):
    if not document.strip():
        st.warning("Please add text or upload a document before clicking 'Analyze text'.")
    else:
        # Prompt template
        prompt_template = """
        You are a legal expert. Analyze the following text and determine whether the generated output can be used for commercial purposes. Use the following format:

        - 🟢 Green light: Commercial use is allowed without restrictions.
        - 🟠 Orange light: Commercial use is conditional or requires additional review.
        - 🔴 Red light: Commercial use is not allowed.

        Provide a brief explanation for your assessment. 
        If you are unsure, respond with 'I don't know.'

        Text: {document}
        """

        # Warn about long documents
        if len(document) > 5000:
            st.warning(
                "The document exceeds 5000 characters. The analysis might be incomplete or inaccurate. Proceeding with the analysis anyway."
            )

        try:
            # OpenAI API request
            prompt = prompt_template.format(document=document)
            with st.spinner("Analyzing..."):
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=300
                )

            # Display result
            output = response['choices'][0]['message']['content']
            st.write("**Analysis Result:**")
            st.markdown(output)

        except Exception as e:
            st.error(f"An unexpected error occurred: {str(e)}")