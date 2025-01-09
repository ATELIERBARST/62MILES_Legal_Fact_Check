import streamlit as st
import openai
from PyPDF2 import PdfReader

# Introductie van de app.

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
# Rest of your app content
st.title("🛡️ Legal Fact Checker")
st.write(
    "Welcome, colleague! This tool helps you assess whether you can safely use the output  "
    "of an AI tool for commercial purposes. Simply paste a legal text or upload a file, "
    "such as a 'terms of use' document, and receive instant advice!"
)

# Vraag de gebruiker om hun OpenAI API-sleutel.
openai_api_key = st.text_input("OpenAI API Key", type="password")
if not openai_api_key:
    st.info("Voer je OpenAI API-sleutel in om verder te gaan.", icon="🗝️")
else:
    # Stel de API-sleutel in voor de OpenAI-bibliotheek
    openai.api_key = openai_api_key

    # Prompt-template voor juridische analyse.
    prompt_template = """
    Je bent een juridische expert. Analyseer de volgende tekst en bepaal of commerciële bruikbaarheid van de gegenereerde output is toegestaan. Gebruik de volgende indeling:

    - 🟢 Groen licht: Commercieel gebruik is toegestaan zonder beperkingen.
    - 🟠 Oranje licht: Commercieel gebruik is afhankelijk van voorwaarden of vereist extra controle.
    - 🔴 Rood licht: Commercieel gebruik is niet toegestaan.

    Voeg een korte uitleg toe bij je beoordeling.
    Als je het niet weet, antwoord je met 'ik weet het niet'.

    Tekst: {document}
    """

    # Laat de gebruiker een document uploaden of tekst invoeren.
    uploaded_file = st.file_uploader("Upload een juridisch document (PDF of TXT):", type=["pdf", "txt"])
    if uploaded_file is not None:
        # Lees de inhoud van het bestand.
        if uploaded_file.name.endswith(".txt"):
            # Voor .txt-bestanden
            document = uploaded_file.read().decode("utf-8")
        elif uploaded_file.name.endswith(".pdf"):
            # Voor PDF-bestanden
            pdf_reader = PdfReader(uploaded_file)
            document = ""
            for page in pdf_reader.pages:
                document += page.extract_text()
        st.write("**Inhoud van het geüploade document:**")
        st.write(document)
    else:
        # Laat gebruikers tekst handmatig invoeren als er geen bestand is.
        document = st.text_area("Of plak hier de juridische tekst.")

    # Analyseer de tekst/document bij klikken op de knop.
    if st.button("Analyseer tekst"):
        if not document.strip():
            st.warning("Voeg een tekst toe of upload een document voordat je op 'Analyseer tekst' klikt.")
        else:
            # Verwerk de juridische tekst met GPT-3.5.
            prompt = prompt_template.format(document=document)
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "system", "content": prompt}],
                    max_tokens=300
                )

                # Ontvang de response en toon deze in de app.
                output = response['choices'][0]['message']['content']
                st.write("**Resultaat van de analyse:**")
                st.markdown(output)
            except openai.error.OpenAIError as e:
                st.error(f"Er is een fout opgetreden: {str(e)}")

            # Optionele waarschuwing bij grote documenten
            if len(document) > 5000:
                st.warning("Het document is te groot. Probeer een kortere tekst.")