import os
import io
from dotenv import load_dotenv
import streamlit as st
import fitz  # PyMuPDF
from PIL import Image
import google.generativeai as genai

# --- Configuration ---
load_dotenv()  # Load environment variables from .env
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

MODEL_NAME = "gemini-2.5-flash"

st.set_page_config(page_title="StudentAid AI", layout="centered")
st.title("StudentAid AI – Homework Solver")

# --- Functions ---
def extract_text_from_pdf(uploaded_pdf):
    """Extract text from a PDF file using PyMuPDF"""
    try:
        file_bytes = uploaded_pdf.read()
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text("text")
        return text.strip(), file_bytes
    except Exception as e:
        st.error(f"PDF extraction error: {e}")
        return "", None

def load_image_bytes(uploaded_img):
    """Read image bytes for vision model"""
    try:
        return uploaded_img.read()
    except Exception as e:
        st.error(f"Image loading error: {e}")
        return None

def solve_with_gemini_text(text):
    """Send text to Gemini for step-by-step solution"""
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        prompt = (
            "You are an expert tutor. Analyze the following homework question and "
            "provide a clear, step-by-step solution that a student can understand.\n\n"
            f"Homework:\n{text}"
        )
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Gemini Text Model Error: {e}")
        return None

def solve_with_gemini_vision(image_bytes):
    """Send image bytes to Gemini for step-by-step solution"""
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        image = Image.open(io.BytesIO(image_bytes))  # Convert bytes to PIL Image
        response = model.generate_content([
            "You are an expert tutor. Analyze this homework image and provide a "
            "clear, step-by-step solution.",
            image
        ])
        return response.text
    except Exception as e:
        st.error(f"Gemini Vision Model Error: {e}")
        return None

# --- Streamlit UI ---
uploaded_file = st.file_uploader(
    "📄 Upload a homework file (PDF or Image)",
    type=["pdf", "png", "jpg", "jpeg"]
)

if uploaded_file and st.button("Solve Homework"):
    ext = uploaded_file.name.split(".")[-1].lower()
    with st.spinner("Analyzing your file..."):
        if ext == "pdf":
            extracted_text, file_bytes = extract_text_from_pdf(uploaded_file)
            if extracted_text:
                solution = solve_with_gemini_text(extracted_text)
            else:
                st.warning("No readable text detected → using Vision model.")
                solution = solve_with_gemini_vision(file_bytes)
        else:
            img_bytes = load_image_bytes(uploaded_file)
            solution = solve_with_gemini_vision(img_bytes)
    
    if solution:
        st.subheader("📘 Step-by-Step Solution:")
        st.markdown(solution)
    else:
        st.error("⚠ No solution was generated. Please try again.")
