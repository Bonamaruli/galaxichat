import os
from dotenv import load_dotenv
from google import genai

# Membaca file .env dan memasukkan isinya ke environment variable
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
model_name = os.getenv("GEMINI_MODEL")

# Selalu periksa dulu, jangan langsung pakai
if not api_key:
    raise SystemExit("GEMINI_API_KEY tidak ditemukan. Cek file .env kamu.")

print(f"Key terbaca (5 karakter awal): {api_key[:5]}...")
print(f"Model yang dipakai: {model_name}")

client = genai.Client(api_key=api_key)

response = client.models.generate_content(
    model=model_name,
    contents="Jelaskan dalam 2 kalimat kenapa langit malam terlihat gelap."
)

print("\n--- Jawaban dari Gemini ---")
print(response.text)