from pathlib import Path

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from backend.ai.preprocessor import preprocess
from backend.ingest.json_loader import KnowledgeEntry, entry_to_document

MODEL_DIR = Path(__file__).resolve().parents[2] / "data" / "model"
VECTORIZER_PATH = MODEL_DIR / "vectorizer.joblib"
KNOWLEDGE_PATH = MODEL_DIR / "knowledge.joblib"
MATRIX_PATH = MODEL_DIR / "matrix.joblib"


class ChatbotModel:
    def __init__(self) -> None:
        self.vectorizer: TfidfVectorizer | None = None
        self.entries: list[KnowledgeEntry] = []
        self.matrix = None
        self.threshold = 0.25

    def is_ready(self) -> bool:
        return self.vectorizer is not None and len(self.entries) > 0

    def train(self, entries: list[KnowledgeEntry], threshold: float = 0.25) -> int:
        if not entries:
            raise ValueError("Không có dữ liệu để train.")

        documents = [entry_to_document(e) for e in entries]
        self.vectorizer = TfidfVectorizer(
            analyzer="word",
            ngram_range=(1, 2),
            min_df=1,
        )
        self.matrix = self.vectorizer.fit_transform(documents)
        self.entries = entries
        self.threshold = threshold
        self._save()
        return len(entries)

    def predict(self, question: str) -> dict:
        if not self.is_ready():
            return {
                "answer": "Hệ thống chưa được train. Vui lòng liên hệ quản trị viên.",
                "confidence": 0.0,
                "matched_question": None,
            }

        query = preprocess(question)
        query_vec = self.vectorizer.transform([query])
        scores = cosine_similarity(query_vec, self.matrix).flatten()
        best_idx = int(scores.argmax())
        best_score = float(scores[best_idx])

        if best_score < self.threshold:
            return {
                "answer": (
                    "Xin lỗi, em chưa có thông tin cho câu hỏi này. "
                    "Bạn có thể hỏi về giá xe, mẫu xe, dịch vụ hoặc địa chỉ cửa hàng."
                ),
                "confidence": best_score,
                "matched_question": None,
            }

        entry = self.entries[best_idx]
        return {
            "answer": entry.answer,
            "confidence": best_score,
            "matched_question": entry.question,
        }

    def _save(self) -> None:
        MODEL_DIR.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.vectorizer, VECTORIZER_PATH)
        joblib.dump(self.entries, KNOWLEDGE_PATH)
        joblib.dump(self.matrix, MATRIX_PATH)

    def load(self) -> bool:
        if not VECTORIZER_PATH.exists() or not KNOWLEDGE_PATH.exists():
            return False
        self.vectorizer = joblib.load(VECTORIZER_PATH)
        self.entries = joblib.load(KNOWLEDGE_PATH)
        if MATRIX_PATH.exists():
            self.matrix = joblib.load(MATRIX_PATH)
        elif self.vectorizer and self.entries:
            documents = [entry_to_document(e) for e in self.entries]
            self.matrix = self.vectorizer.transform(documents)
        return self.is_ready()


model = ChatbotModel()
