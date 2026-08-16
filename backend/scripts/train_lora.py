"""Melatih adapter LoRA pada model kecil dengan dataset instruksi astronomi.

Model dasar dibekukan dan dikompresi ke 4-bit; hanya lapisan adapter
yang dilatih. Hasilnya file adapter berukuran puluhan MB.
"""

import json
import time
from pathlib import Path

import torch
from datasets import Dataset
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
)
from trl import SFTConfig, SFTTrainer

BASE_DIR = Path(__file__).resolve().parent.parent
DATASET_FILE = BASE_DIR / "data" / "instruction_dataset_clean.jsonl"
OUTPUT_DIR = BASE_DIR / "data" / "models" / "lora-astronomi"

BASE_MODEL = "Qwen/Qwen2.5-1.5B-Instruct"

# Hyperparameter pelatihan
EPOCHS = 3
BATCH_SIZE = 1
GRAD_ACCUM = 8
LEARNING_RATE = 2e-4
MAX_LENGTH = 512

# Konfigurasi LoRA
LORA_RANK = 16
LORA_ALPHA = 32
LORA_DROPOUT = 0.05

SYSTEM_LINE = "Kamu adalah asisten astronomi berbahasa Indonesia."


def load_dataset() -> Dataset:
    rows = []
    with DATASET_FILE.open(encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if line:
                rows.append(json.loads(line))

    print(f"Dataset dimuat: {len(rows)} pasangan")
    return Dataset.from_list(rows)


def format_example(example: dict, tokenizer) -> dict:
    """Menyusun percakapan sesuai template chat model."""
    messages = [
        {"role": "system", "content": SYSTEM_LINE},
        {"role": "user", "content": example["instruction"]},
        {"role": "assistant", "content": example["output"]},
    ]
    text = tokenizer.apply_chat_template(messages, tokenize=False)
    return {"text": text}


def main() -> None:
    if not DATASET_FILE.exists():
        raise SystemExit(f"Dataset tidak ditemukan: {DATASET_FILE}")

    dataset = load_dataset()

    print(f"\nMemuat model: {BASE_MODEL}")
    start = time.perf_counter()

    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # Kuantisasi 4-bit: inilah yang membuat model muat di VRAM terbatas.
    quant_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
        bnb_4bit_use_double_quant=True,
    )

    model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        quantization_config=quant_config,
        device_map={"": 0},
    )
    model.config.use_cache = False

    print(f"Model siap dalam {time.perf_counter() - start:.1f} detik")

    model = prepare_model_for_kbit_training(model)

    lora_config = LoraConfig(
        r=LORA_RANK,
        lora_alpha=LORA_ALPHA,
        lora_dropout=LORA_DROPOUT,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=[
            "q_proj", "k_proj", "v_proj", "o_proj",
            "gate_proj", "up_proj", "down_proj",
        ],
    )

    model = get_peft_model(model, lora_config)

    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total = sum(p.numel() for p in model.parameters())
    print(f"\nParameter total     : {total:,}")
    print(f"Parameter dilatih   : {trainable:,} ({trainable / total * 100:.3f}%)")

    formatted = dataset.map(
        lambda example: format_example(example, tokenizer),
        remove_columns=dataset.column_names,
    )

    config = SFTConfig(
        output_dir=str(OUTPUT_DIR),
        num_train_epochs=EPOCHS,
        per_device_train_batch_size=BATCH_SIZE,
        gradient_accumulation_steps=GRAD_ACCUM,
        learning_rate=LEARNING_RATE,
        max_length=MAX_LENGTH,
        logging_steps=5,
        save_strategy="epoch",
        optim="paged_adamw_8bit",
        bf16=True,
        gradient_checkpointing=True,
        report_to="none",
        dataset_text_field="text",
    )

    trainer = SFTTrainer(
        model=model,
        train_dataset=formatted,
        args=config,
    )

    print("\nMulai pelatihan...\n")
    start = time.perf_counter()
    trainer.train()
    elapsed = time.perf_counter() - start

    trainer.save_model(str(OUTPUT_DIR))
    tokenizer.save_pretrained(str(OUTPUT_DIR))

    print(f"\nPelatihan selesai dalam {elapsed / 60:.1f} menit")
    print(f"Adapter tersimpan: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()