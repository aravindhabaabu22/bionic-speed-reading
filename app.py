import streamlit as st

import streamlit.components.v1 as components

import pymupdf

import re

import html

import json

st.set_page_config(

    page_title="Bionic Speed Reader",

    page_icon="📖",

    layout="centered"

)

def bionic_word(word):

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

st.title("📖 Bionic Speed Reader")

uploaded_file = st.file_uploader(

    "Upload your textbook PDF",

    type=["pdf"]

)

if uploaded_file:

    text = extract_pdf_text(uploaded_file)

    text = clean_text(text)

    words = text.split()

    st.success(f"Loaded {len(words):,} words")

    col1, col2 = st.columns(2)

    with col1:

        chunk_size = st.slider(

            "Words per subtitle",

            2,

            8,

            4

        )

    with col2:

        wpm = st.slider(

            "Reading speed",

            100,

            1500,

            500,

            50

        )

    chunks = create_chunks(words, chunk_size)

    formatted_chunks = []

    for chunk in chunks:

        formatted = " ".join(

            bionic_word(word)

            for word in chunk

        )

        formatted_chunks.append(formatted)

    chunks_json = json.dumps(formatted_chunks)

    reader_html = f"""

<!DOCTYPE html>

<html>

<head>

<meta name="viewport"

content="width=device-width, initial-scale=1.0">

<style>

body {{

    margin: 0;

    background: #111111;

    color: white;

    font-family: Arial, sans-serif;

}}

.reader {{

    width: 100%;

    text-align: center;

}}

.screen {{

    height: 300px;

    display: flex;

    align-items: center;

    justify-content: center;

    padding: 20px;

    box-sizing: border-box;

}}

#text {{

    font-size: 38px;

    line-height: 1.4;

    max-width: 800px;

}}

strong {{

    font-weight: 900;

}}

.controls {{

    display: flex;

    justify-content: center;

    gap: 8px;

    flex-wrap: wrap;

    margin-top: 10px;

}}

button {{

    border: none;

    border-radius: 10px;

    padding: 12px 18px;

    font-size: 16px;

    background: #333333;

    color: white;

}}

button:active {{

    transform: scale(0.96);

}}

.info {{

    margin-top: 15px;

    font-size: 14px;

    color: #bbbbbb;

}}

input {{

    width: 90%;

}}

</style>

</head>

<body>

<div class="reader">

<div class="screen">

<div id="text">

Press PLAY

</div>

</div>

<div class="controls">

<button onclick="previousChunk()">◀</button>

<button onclick="togglePlay()" id="playButton">

▶ PLAY

</button>

<button onclick="nextChunk()">▶</button>

</div>

<div class="controls">

<label>

Speed:

<select id="speed">

<option value="300">300 WPM</option>

<option value="400">400 WPM</option>

<option value="500" selected>500 WPM</option>

<option value="600">600 WPM</option>

<option value="800">800 WPM</option>

<option value="1000">1000 WPM</option>

</select>

</label>

</div>

<div class="info">

<div id="progress">

0 / {len(formatted_chunks)}

</div>

</div>

</div>

<script>

const chunks = {chunks_json};

let current = 0;

let playing = false;

let timer = null;

function showChunk() {{

    if (chunks.length === 0) return;

    document.getElementById("text").innerHTML =

        chunks[current];

    document.getElementById("progress").innerText =

        (current + 1) + " / " + chunks.length;

}}

function getDelay() {{

    const wpm =

        Number(document.getElementById("speed").value);

    const words =

        chunks[current]

        .replace(/<[^>]*>/g, "")

        .trim()

        .split(/\\s+/)

        .length;

    return (words / wpm) * 60000;

}}

function playNext() {{

    if (!playing) return;

    showChunk();

    timer = setTimeout(() => {{

        if (current < chunks.length - 1) {{

            current++;

            playNext();

        }} else {{

            playing = false;

            document.getElementById("playButton")

                .innerText = "▶ PLAY";

        }}

    }}, getDelay());

}}

function togglePlay() {{

    if (playing) {{

        playing = false;

        clearTimeout(timer);

        document.getElementById("playButton")

            .innerText = "▶ PLAY";

    }} else {{

        playing = true;

        document.getElementById("playButton")

            .innerText = "⏸ PAUSE";

        playNext();

    }}

}}

function nextChunk() {{

    clearTimeout(timer);

    if (current < chunks.length - 1)

        current++;

    showChunk();

}}

function previousChunk() {{

    clearTimeout(timer);

    if (current > 0)

        current--;

    showChunk();

}}

document

    .getElementById("speed")

    .addEventListener("change", function() {{

        if (playing) {{

            clearTimeout(timer);

            playNext();

        }}

    }});

showChunk();

</script>

</body>

</html>

"""

    components.html(

        reader_html,

        height=500,

        scrolling=False

    )
