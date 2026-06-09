# -*- coding: utf-8 -*-
"""
LawPal - T5-small Fine-Tuning Script
Model  : google/t5-small
Data   : lawpal_training_data.json  (input -> output pairs)
Run    : python train_lawpal.py
"""

import json, os, time, torch
from torch.utils.data import Dataset, DataLoader, random_split
from transformers import T5Tokenizer, T5ForConditionalGeneration, get_linear_schedule_with_warmup
from torch.optim import AdamW

# ─────────────────────────────────────────────
#  CONFIG
# ─────────────────────────────────────────────
DATA_FILE   = "lawpal_training_data.json"
MODEL_NAME  = "t5-small"
OUTPUT_DIR  = "lawpal_model"
EPOCHS      = 15
BATCH_SIZE  = 4
MAX_INPUT   = 128
MAX_OUTPUT  = 256
LR          = 3e-4
VAL_SPLIT   = 0.1        # 10% for validation
TASK_PREFIX = "answer legal question: "

# ─────────────────────────────────────────────
#  DATASET
# ─────────────────────────────────────────────
class LawPalDataset(Dataset):
    def __init__(self, data, tokenizer):
        self.data      = data
        self.tokenizer = tokenizer

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        item        = self.data[idx]
        input_text  = TASK_PREFIX + item["input"]
        output_text = item["output"]

        inp = self.tokenizer(
            input_text, max_length=MAX_INPUT,
            padding="max_length", truncation=True, return_tensors="pt"
        )
        out = self.tokenizer(
            output_text, max_length=MAX_OUTPUT,
            padding="max_length", truncation=True, return_tensors="pt"
        )

        labels = out["input_ids"].squeeze()
        labels[labels == self.tokenizer.pad_token_id] = -100   # ignore padding in loss

        return {
            "input_ids":      inp["input_ids"].squeeze(),
            "attention_mask": inp["attention_mask"].squeeze(),
            "labels":         labels
        }

# ─────────────────────────────────────────────
#  PROGRESS BAR HELPER
# ─────────────────────────────────────────────
def progress(current, total, loss, width=30):
    filled = int(width * current / total)
    bar    = "█" * filled + "░" * (width - filled)
    print(f"\r  [{bar}] {current}/{total}  loss: {loss:.4f}", end="", flush=True)

# ─────────────────────────────────────────────
#  TRAIN
# ─────────────────────────────────────────────
def train():
    print("\n" + "="*55)
    print("   ⚖  LawPal  —  T5-small Fine-Tuning")
    print("="*55)

    # Load data
    with open(DATA_FILE, encoding="utf-8") as f:
        raw = json.load(f)
    print(f"  Dataset     : {len(raw)} examples")

    # Tokenizer + model
    print(f"  Model       : {MODEL_NAME}")
    tokenizer = T5Tokenizer.from_pretrained(MODEL_NAME)
    model     = T5ForConditionalGeneration.from_pretrained(MODEL_NAME)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"  Device      : {device}")
    model.to(device)

    # Train / val split
    full_ds  = LawPalDataset(raw, tokenizer)
    val_size = max(1, int(len(full_ds) * VAL_SPLIT))
    trn_size = len(full_ds) - val_size
    train_ds, val_ds = random_split(full_ds, [trn_size, val_size])
    print(f"  Train/Val   : {trn_size} / {val_size}")

    train_dl = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True)
    val_dl   = DataLoader(val_ds,   batch_size=BATCH_SIZE)

    # Optimizer + scheduler
    optimizer = AdamW(model.parameters(), lr=LR, weight_decay=0.01)
    total_steps = len(train_dl) * EPOCHS
    scheduler = get_linear_schedule_with_warmup(
        optimizer,
        num_warmup_steps=int(0.1 * total_steps),
        num_training_steps=total_steps
    )

    print(f"  Epochs      : {EPOCHS}")
    print(f"  Batch size  : {BATCH_SIZE}")
    print(f"  LR          : {LR}")
    print("="*55 + "\n")

    best_val_loss = float("inf")
    start_time    = time.time()

    for epoch in range(1, EPOCHS + 1):
        # ── Training ──
        model.train()
        train_loss = 0
        for i, batch in enumerate(train_dl, 1):
            ids   = batch["input_ids"].to(device)
            mask  = batch["attention_mask"].to(device)
            lbls  = batch["labels"].to(device)

            optimizer.zero_grad()
            loss = model(input_ids=ids, attention_mask=mask, labels=lbls).loss
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            scheduler.step()

            train_loss += loss.item()
            progress(i, len(train_dl), train_loss / i)

        avg_train = train_loss / len(train_dl)

        # ── Validation ──
        model.eval()
        val_loss = 0
        with torch.no_grad():
            for batch in val_dl:
                ids  = batch["input_ids"].to(device)
                mask = batch["attention_mask"].to(device)
                lbls = batch["labels"].to(device)
                val_loss += model(input_ids=ids, attention_mask=mask, labels=lbls).loss.item()
        avg_val = val_loss / len(val_dl)

        elapsed = time.time() - start_time
        print(f"\n  Epoch {epoch:02d}/{EPOCHS}  |  "
              f"train loss: {avg_train:.4f}  |  "
              f"val loss: {avg_val:.4f}  |  "
              f"time: {elapsed:.1f}s")

        # Save best model
        if avg_val < best_val_loss:
            best_val_loss = avg_val
            os.makedirs(OUTPUT_DIR, exist_ok=True)
            model.save_pretrained(OUTPUT_DIR)
            tokenizer.save_pretrained(OUTPUT_DIR)
            print(f"  ✔  Best model saved  (val loss: {best_val_loss:.4f})")

    total = time.time() - start_time
    print(f"\n{'='*55}")
    print(f"  Training complete in {total:.1f}s")
    print(f"  Best val loss : {best_val_loss:.4f}")
    print(f"  Model saved to: {OUTPUT_DIR}/")
    print("="*55)

# ─────────────────────────────────────────────
#  INFERENCE
# ─────────────────────────────────────────────
def ask(question, model_dir=OUTPUT_DIR):
    tokenizer = T5Tokenizer.from_pretrained(model_dir)
    model     = T5ForConditionalGeneration.from_pretrained(model_dir)
    model.eval()

    inp = tokenizer(
        TASK_PREFIX + question,
        return_tensors="pt", max_length=MAX_INPUT, truncation=True
    )
    with torch.no_grad():
        out = model.generate(
            inp["input_ids"],
            max_length=MAX_OUTPUT,
            num_beams=4,
            no_repeat_ngram_size=2,
            early_stopping=True
        )
    return tokenizer.decode(out[0], skip_special_tokens=True)

# ─────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────
if __name__ == "__main__":
    train()

    print("\n--- Testing trained model ---\n")
    tests = [
        "Can my landlord enter my room without permission?",
        "What does indemnify mean in a contract?",
        "What are my rights if I am arrested?",
        "Can a university suspend a student without a hearing?",
        "What happens if I default on a loan?",
    ]
    for q in tests:
        print(f"Q: {q}")
        print(f"A: {ask(q)}\n")
