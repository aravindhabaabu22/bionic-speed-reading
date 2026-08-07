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

# ---------------------------------------------------------

# BIONIC FORMATTING

# ---------------------------------------------------------

def bionic_word(word):

    """

    Highlights the beginning of each word using colour

    instead of bold.

    """

    match = re.match(

        r"^([^A-Za-z]*)([A-Za-z]+)(.*)$",

        word

    )

    if not match:

        return html.escape(word)

    prefix, letters, suffix = match.groups()

    # Percentage of word emphasized

    n = max(1, round(len(letters) * 0.4))

    emphasized = letters[:n]

    normal = letters[n:]

    return (

        html.escape(prefix)

        + '<span class="bionic">'

        + html.escape(emphasized)

        + '</span>'

        + html.escape(normal + suffix)

    )

# ---------------------------------------------------------

# PDF EXTRACTION

# ---------------------------------------------------------

def extract_pdf_pages(uploaded_file):

    data = uploaded_file.read()

    document = pymupdf.open(

        stream=data,

        filetype="pdf"

    )

    pages = []

    for page in document:

        text = page.get_text()

        # Remove broken hyphenation

        text = re.sub(

            r"-\n",

            "",

            text

        )

        # Replace line breaks with spaces

        text = re.sub(

            r"\n+",

            " ",

            text

        )

        # Remove repeated whitespace

        text = re.sub(

            r"\s+",

            " ",

            text

        )

        text = text.strip()

        pages.append(text)

    document.close()

    return pages

# ---------------------------------------------------------

# CREATE WORD CHUNKS

# ---------------------------------------------------------

def create_chunks(words, chunk_size=4):

    chunks = []

    for i in range(

        0,

        len(words),

        chunk_size

    ):

        chunks.append(

            words[i:i + chunk_size]

        )

    return chunks

# ---------------------------------------------------------

# APP TITLE

# ---------------------------------------------------------

st.markdown(

    """

    <h1 style="

        text-align:center;

        color:#222222;

        margin-bottom:5px;

    ">

    📖 Bionic Speed Reader

    </h1>

    """,

    unsafe_allow_html=True

)

# ---------------------------------------------------------

# PDF UPLOAD

# ---------------------------------------------------------

uploaded_file = st.file_uploader(

    "Upload your textbook PDF",

    type=["pdf"]

)

if uploaded_file:

    pages = extract_pdf_pages(

        uploaded_file

    )

    total_pages = len(pages)

    # -----------------------------------------------------

    # PAGE SELECTION

    # -----------------------------------------------------

    st.markdown(

        "<h4 style='color:#333333;'>Start from page</h4>",

        unsafe_allow_html=True

    )

    selected_page = st.number_input(

        f"Page number (1 - {total_pages})",

        min_value=1,

        max_value=total_pages,

        value=1,

        step=1

    )

    # -----------------------------------------------------

    # READING SETTINGS

    # -----------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:

        wpm = st.select_slider(

            "Reading speed",

            options=[

                200,

                300,

                400,

                500,

                600,

                700,

                800,

                1000,

                1200

            ],

            value=500

        )

    with col2:

        chunk_size = st.select_slider(

            "Words on screen",

            options=[

                2,

                3,

                4

            ],

            value=3

        )

    # -----------------------------------------------------

    # COLLECT TEXT FROM SELECTED PAGE ONWARD

    # -----------------------------------------------------

    all_chunks = []

    chunk_page_numbers = []

    for page_number in range(

        selected_page - 1,

        total_pages

    ):

        page_text = pages[page_number]

        if not page_text:

            continue

        words = page_text.split()

        page_chunks = create_chunks(

            words,

            chunk_size

        )

        for chunk in page_chunks:

            all_chunks.append(

                " ".join(chunk)

            )

            chunk_page_numbers.append(

                page_number + 1

            )

    # -----------------------------------------------------

    # BIONIC HTML

    # -----------------------------------------------------

    formatted_chunks = []

    for chunk in all_chunks:

        words = chunk.split()

        formatted = " ".join(

            bionic_word(word)

            for word in words

        )

        formatted_chunks.append(

            formatted

        )

    if not formatted_chunks:

        st.error(

            "No readable text was found on this page."

        )

    else:

        chunks_json = json.dumps(

            formatted_chunks

        )

        page_numbers_json = json.dumps(

            chunk_page_numbers

        )

        # -------------------------------------------------

        # READER

        # -------------------------------------------------

        reader_html = f"""

<!DOCTYPE html>

<html>

<head>

<meta

name="viewport"

content="width=device-width, initial-scale=1.0"

>

<style>

html,

body {{

    margin: 0;

    padding: 0;

    background: #ffffff;

    font-family:

        -apple-system,

        BlinkMacSystemFont,

        "Segoe UI",

        sans-serif;

}}

.reader {{

    width: 100%;

    background: #ffffff;

    color: #222222;

}}

.screen {{

    height: 330px;

    display: flex;

    align-items: center;

    justify-content: center;

    text-align: center;

    padding: 25px;

    box-sizing: border-box;

}}

#text {{

    font-size: 58px;

    font-weight: 400;

    line-height: 1.25;

    letter-spacing: -0.5px;

    max-width: 950px;

    color: #222222;

    word-wrap: break-word;

}}

.bionic {{

    color: #1677ff;

    font-weight: 500;

}}

.controls {{

    display: flex;

    justify-content: center;

    align-items: center;

    gap: 10px;

    flex-wrap: wrap;

    margin-top: 10px;

}}

button {{

    border: 1px solid #dddddd;

    border-radius: 12px;

    padding: 12px 18px;

    font-size: 16px;

    background: #f5f5f5;

    color: #222222;

}}

button:active {{

    background: #e8e8e8;

    transform: scale(0.97);

}}

#playButton {{

    min-width: 105px;

}}

.info {{

    text-align: center;

    margin-top: 15px;

    font-size: 15px;

    color: #666666;

}}

.progress-container {{

    width: 90%;

    height: 6px;

    background: #eeeeee;

    border-radius: 10px;

    margin: 15px auto;

    overflow: hidden;

}}

#progressBar {{

    height: 100%;

    width: 0%;

    background: #1677ff;

    transition: width 0.1s linear;

}}

.speed-control {{

    text-align: center;

    margin-top: 10px;

    color: #444444;

}}

select {{

    padding: 8px 12px;

    border-radius: 8px;

    border: 1px solid #dddddd;

    background: white;

    font-size: 15px;

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

<button onclick="previousChunk()">

◀

</button>

<button

onclick="togglePlay()"

id="playButton"

>

▶ PLAY

</button>

<button onclick="nextChunk()">

▶

</button>

</div>

<div class="speed-control">

Speed:

<select id="speed">

<option value="200">

200 WPM

</option>

<option value="300">

300 WPM

</option>

<option value="400">

400 WPM

</option>

<option value="500"

selected>

500 WPM

</option>

<option value="600">

600 WPM

</option>

<option value="700">

700 WPM

</option>

<option value="800">

800 WPM

</option>

<option value="1000">

1000 WPM

</option>

<option value="1200">

1200 WPM

</option>

</select>

</div>

<div class="info">

<div id="pageInfo">

Page 1 / {total_pages}

</div>

<div id="chunkInfo">

Chunk 1 / {len(formatted_chunks)}

</div>

</div>

<div class="progress-container">

<div id="progressBar">

</div>

</div>

</div>

<script>

const chunks =

{chunks_json};

const pageNumbers =

{page_numbers_json};

let current = 0;

let playing = false;

let timer = null;

function showChunk() {{

    if (

        chunks.length === 0

    )

        return;

    document

        .getElementById("text")

        .innerHTML =

        chunks[current];

    document

        .getElementById("pageInfo")

        .innerText =

        "Page "

        + pageNumbers[current]

        + " / {total_pages}";

    document

        .getElementById("chunkInfo")

        .innerText =

        "Chunk "

        + (current + 1)

        + " / "

        + chunks.length;

    const progress =

        ((current + 1)

        / chunks.length)

        * 100;

    document

        .getElementById("progressBar")

        .style

        .width =

        progress + "%";

}}

function getDelay() {{

    const wpm =

        Number(

            document

                .getElementById("speed")

                .value

        );

    const plainText =

        chunks[current]

            .replace(

                /<[^>]*>/g,

                ""

            )

            .trim();

    const wordCount =

        plainText

            .split(/\s+/)

            .length;

    return (

        wordCount

        / wpm

    ) * 60000;

}}

function playNext() {{

    if (!playing)

        return;

    showChunk();

    timer =

        setTimeout(

            function() {{

                if (

                    current

                    <

                    chunks.length - 1

                ) {{

                    current++;

                    playNext();

                }}

                else {{

                    playing = false;

                    document

                        .getElementById(

                            "playButton"

                        )

                        .innerText =

                        "▶ PLAY";

                }}

            }},

            getDelay()

        );

}}

function togglePlay() {{

    if (playing) {{

        playing = false;

        clearTimeout(timer);

        document

            .getElementById(

                "playButton"

            )

            .innerText =

            "▶ PLAY";

    }}

    else {{

        playing = true;

        document

            .getElementById(

                "playButton"

            )

            .innerText =

            "⏸ PAUSE";

        playNext();

    }}

}}

function nextChunk() {{

    clearTimeout(timer);

    if (

        current

        <

        chunks.length - 1

    )

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

    .addEventListener(

        "change",

        function() {{

            if (playing) {{

                clearTimeout(timer);

                playNext();

            }}

        }}

    );

showChunk();

</script>

</body>

</html>

"""

        components.html(

            reader_html,

            height=560,

            scrolling=False

        )
