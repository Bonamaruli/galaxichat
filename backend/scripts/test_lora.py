"""Membandingkan jawaban model dasar dan model hasil fine-tuning.

Kedua model menjawab pertanyaan yang sama agar perbedaannya terlihat.
"""

from pathlib import Path

import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

BASE_DIR = Path(__file__).resolve().parent.parent
ADAPTER_DIR = BASE_DIR / "data" / "models" / "lora-astronomi"

BASE_MODEL = "Qwen/Qwen2.5-1.5B-Instruct"
SYSTEM_LINE = "Kamu adalah asisten astronomi berbahasa Indonesia."

QUESTIONS = [
    "Tata Surya dibagi menjadi berapa daerah?",
    "Apa yang membuat cahaya tidak bisa lepas dari lubang hitam?",
    "Bagaimana bintang terbentuk?",
    "Kenapa langit malam gelap padahal ada banyak bintang?",
    "Bagaimana cara memasak rendang padang?",
]

MAX_NEW_TOKENS = 200


def build_prompt(tokenizer, question: str) -> str:
    messages = [
        {"role": "system", "content": SYSTEM_LINE},
        {"role": "user", "content": question},
    ]
    return tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )


def generate(model, tokenizer, question: str) -> str:
    prompt = build_prompt(tokenizer, question)
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

    with torch.no_grad():
        output = model.generate(
            **inputs,
            max_new_tokens=MAX_NEW_TOKENS,
            temperature=0.3,
            do_sample=True,
            pad_token_id=tokenizer.pad_token_id or tokenizer.eos_token_id,
        )

    generated = output[0][inputs["input_ids"].shape[1]:]
    return tokenizer.decode(generated, skip_special_tokens=True).strip()


def main() -> None:
    quant_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
        bnb_4bit_use_double_quant=True,
    )

    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    print("Memuat model dasar...")
    base = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        quantization_config=quant_config,
        device_map={"": 0},
    )
    base.eval()

    print("Memuat adapter LoRA...")
    tuned = PeftModel.from_pretrained(base, str(ADAPTER_DIR))
    tuned.eval()

    for index, question in enumerate(QUESTIONS, start=1):
        print("\n" + "=" * 78)
        print(f"[{index}] {question}")
        print("=" * 78)

        # Adapter dinonaktifkan sementara agar model kembali ke perilaku dasar.
        with tuned.disable_adapter():
            base_answer = generate(tuned, tokenizer, question)

        tuned_answer = generate(tuned, tokenizer, question)

        print("\n--- SEBELUM fine-tuning ---")
        print(base_answer)
        print("\n--- SESUDAH fine-tuning ---")
        print(tuned_answer)


if __name__ == "__main__":
    main()