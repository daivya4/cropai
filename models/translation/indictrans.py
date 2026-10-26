from __future__ import annotations

import os
import re
import threading


MODEL_NAME = os.getenv(
    "CROPAI_TRANSLATION_MODEL",
    "ai4bharat/indictrans2-en-indic-dist-200M",
)
MODEL_REVISION = "2cfd0a20057756d756bf3e53528f492afc52f91a"

TARGET_LANGUAGES = {
    "kn": "kan_Knda",
    "hi": "hin_Deva",
    "pa": "pan_Guru",
    "gu": "guj_Gujr",
    "mr": "mar_Deva",
    "te": "tel_Telu",
    "ta": "tam_Taml",
}


def validate_translation(text: str) -> str:
    translated = text.strip()
    if not translated:
        raise RuntimeError("IndicTrans2 returned an empty translation.")
    if re.search(r"[A-Za-z]", translated):
        raise RuntimeError("IndicTrans2 returned untranslated English text.")
    return translated


class IndicTrans2Translator:
    def __init__(self) -> None:
        import torch
        from indicnlp.tokenize import indic_detokenize
        from indicnlp.transliterate.unicode_transliterate import UnicodeIndicTransliterator
        from sacremoses import MosesPunctNormalizer, MosesTokenizer
        os.environ.setdefault("USE_TF", "0")
        from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = AutoTokenizer.from_pretrained(
            MODEL_NAME,
            revision=MODEL_REVISION,
            trust_remote_code=True,
        )
        self.model = AutoModelForSeq2SeqLM.from_pretrained(
            MODEL_NAME,
            revision=MODEL_REVISION,
            trust_remote_code=True,
        ).to(self.device)
        self.model.eval()
        self.english_tokenizer = MosesTokenizer(lang="en")
        self.english_normalizer = MosesPunctNormalizer()
        self.indic_detokenizer = indic_detokenize
        self.indic_transliterator = UnicodeIndicTransliterator()
        self._inference_lock = threading.Lock()

    def translate(self, text: str, language: str) -> str:
        import torch

        target_language = TARGET_LANGUAGES.get(language)
        if target_language is None:
            raise ValueError(f"Unsupported IndicTrans2 target language: {language}")

        normalized = self.english_normalizer.normalize(text.strip())
        tokens = self.english_tokenizer.tokenize(normalized, escape=False)
        prepared = [f"eng_Latn {target_language} {' '.join(tokens)}"]
        inputs = self.tokenizer(
            prepared,
            truncation=True,
            padding="longest",
            return_tensors="pt",
            return_attention_mask=True,
        ).to(self.device)

        with self._inference_lock, torch.inference_mode():
            generated = self.model.generate(
                **inputs,
                use_cache=False,
                min_length=0,
                max_new_tokens=min(192, max(64, inputs["input_ids"].shape[1] * 2)),
                num_beams=1,
                num_return_sequences=1,
            )

        decoded = self.tokenizer.batch_decode(
            generated,
            skip_special_tokens=True,
            clean_up_tokenization_spaces=True,
        )
        target_script = target_language.split("_", maxsplit=1)[1]
        target_iso = {
            "Knda": "kn",
            "Deva": "hi" if language == "hi" else "mr",
            "Guru": "pa",
            "Gujr": "gu",
            "Telu": "te",
            "Taml": "ta",
        }[target_script]
        indic_text = self.indic_transliterator.transliterate(decoded[0], "hi", target_iso)
        translated = self.indic_detokenizer.trivial_detokenize(indic_text, target_iso)
        return validate_translation(translated)


_translator: IndicTrans2Translator | None = None
_translator_lock = threading.Lock()


def get_translator() -> IndicTrans2Translator:
    global _translator

    if _translator is None:
        with _translator_lock:
            if _translator is None:
                _translator = IndicTrans2Translator()
    return _translator
