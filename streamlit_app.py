import streamlit as st
import openai
from PyPDF2 import PdfReader

# Fetch the OpenAI API key from Streamlit secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]

# CSS to adjust padding and ensure the logo is left-aligned at the top
st.markdown(
    """
    <style>
        /* Remove padding from the main container */
        .main {
            padding-top: 0px !important;
            padding-bottom: 0px !important;
        }
        .block-container {
            padding-top: 80px !important; /* Space below the logo */
        }
        /* Logo container styles */
        #logo-container {
            text-align: left; /* Left-align the logo */
            margin-top: 0px !important; /* No margin above the logo */
            padding: 0px !important; /* Remove padding */
        }
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

# Allow the user to upload a document or input text
uploaded_file = st.file_uploader("Upload a legal document (PDF or TXT):", type=["pdf", "txt"])
document = ""  # Initialize the document variable

if uploaded_file is not None:
    # Read the content of the uploaded file
    if uploaded_file.name.endswith(".txt"):
        # For .txt files
        document = uploaded_file.read().decode("utf-8")
    elif uploaded_file.name.endswith(".pdf"):
        # For PDF files
        pdf_reader = PdfReader(uploaded_file)
        document = ""
        for page in pdf_reader.pages:
            document += page.extract_text()
    st.write("**Content of the uploaded document:**")
    st.write(document)
else:
    # Allow users to input text manually if no file is uploaded
    document = st.text_area("Or paste the legal text here.")

# Analyze the text/document on button click
if st.button("Analyze text"):
    if not document.strip():
        st.warning("Please add text or upload a document before clicking 'Analyze text'.")
    else:
        # Define the prompt template in English
        prompt_template = """
        You are a legal expert. Analyze the following text and determine whether the generated output can be used for commercial purposes. Use the following format:

        - 🟢 Green light: Commercial use is allowed without restrictions.
        - 🟠 Orange light: Commercial use is conditional or requires additional review.
        - 🔴 Red light: Commercial use is not allowed.

        Provide a brief explanation for your assessment. 
        If you are unsure, respond with 'I don't know.'

        Text: {document}
        """

        # Check document length and warn the user if it exceeds 5000 characters
        if len(document) > 5000:
            st.warning(
                "The document exceeds 5000 characters. The analysis might be incomplete or inaccurate. "
                "Proceeding with the analysis anyway."
            )

        try:
            # Prepare and send the request to OpenAI
            prompt = prompt_template.format(document=document)
            with st.spinner("Analyzing..."):
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=300
                )

            # Get the response and display it in the app
            output = response['choices'][0]['message']['content']
            st.write("**Analysis Result:**")
            st.markdown(output)

        except openai.error.OpenAIError as e:
            st.error(f"An OpenAI error occurred: {str(e)}")
        except Exception as e:
            st.error(f"An unexpected error occurred: {str(e)}")