import streamlit as st

import pymupdf

import re

import html

st.set_page_config(

    page_title="Bionic Speed Reader",

    page_icon="📖",

    layout="centered"

)

st.title("📖 Bionic Speed Reader")

def bionic_word(word):

    """

    Bold the first ~40% of alphabetic characters.

    Keeps punctuation outside the bold section.

    """

    match = re.match(r"^([^A-Za-z]*)([A-Za-z]+)(.*)$", word)

    if not match:

        return html.escape(word)

    prefix, letters, suffix = match.groups()

    n = max(1, round(len(letters) * 0.4))

    bold_part = letters[:n]

    normal_part = letters[n:]

    return (

        html.escape(prefix)

        + "<strong>"

        + html.escape(bold_part)

        + "</strong>"

        + html.escape(normal_part + suffix)

    )

def extract_pdf_text(uploaded_file):

    data = uploaded_file.read()

    with pymupdf.open(stream=data, filetype="pdf") as doc:

        pages = []

        for page in doc:

            pages.append(page.get_text())

    return "\n".join(pages)

def clean_text(text):

    text = re.sub(r"-\n", "", text)

    text = re.sub(r"\n+", " ", text)

    text = re.sub(r"\s+", " ", text)

    return text.strip()

def create_chunks(words, chunk_size):

    return [

        words[i:i + chunk_size]

        for i in range(0, len(words), chunk_size)

    ]

uploaded_file = st.file_uploader(

    "Upload your textbook PDF",

    type=["pdf"]

)

if uploaded_file:

    text = extract_pdf_text(uploaded_file)

    text = clean_text(text)

    words = text.split()

    st.success(f"Loaded {len(words):,} words.")

    chunk_size = st.slider(

        "Words per chunk",

        min_value=1,

        max_value=8,

        value=4

    )

    wpm = st.slider(

        "Reading speed (WPM)",

        min_value=100,

        max_value=1500,

        value=500,

        step=50

    )

    chunks = create_chunks(words, chunk_size)

    st.write(f"Total chunks: {len(chunks):,}")

    if chunks:

        chunk_number = st.number_input(

            "Preview chunk",

            min_value=1,

            max_value=len(chunks),

            value=1

        )

        current_chunk = chunks[chunk_number - 1]

        formatted = " ".join(

            bionic_word(word)

            for word in current_chunk

        )

        st.markdown(

            f"""

            <div style="

                min-height: 300px;

                display: flex;

                align-items: center;

                justify-content: center;

                text-align: center;

                font-size: 42px;

                line-height: 1.4;

                padding: 30px;

            ">

                {formatted}

            </div>

            """,

            unsafe_allow_html=True

        )

        st.info(

            f"Chunk {chunk_number} of {len(chunks)}"
        )
