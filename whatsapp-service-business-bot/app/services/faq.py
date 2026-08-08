from __future__ import annotations
import re
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from ..models import FAQ

_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9\s]", " ", (text or "").lower()).strip()

def match_faq(text: str) -> FAQ | None:
    faqs = FAQ.query.filter_by(is_active=True).all()
    if not faqs:
        return None
    docs = [f"{f.question} {f.answer} {f.category} {f.keywords}" for f in faqs]
    emb = _model.encode([text] + docs, normalize_embeddings=True)
    scores = cosine_similarity([emb[0]], emb[1:])[0]
    idx = scores.argmax()
    score = float(scores[idx])
    return faqs[idx] if score >= 0.45 else None

def faq_categories_summary() -> str:
    categories = sorted({faq.category for faq in FAQ.query.filter_by(is_active=True).all()})
    if not categories:
        return "No FAQs are configured yet."
    return "You can ask me about: " + ", ".join(categories) + "."
