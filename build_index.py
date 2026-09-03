from rag.pdf_loader import load_cv_text
from rag.chunker import chunk_cv
from rag.embedder import embed_texts
from config import CV_DIR
import os

def main():
    cv_path = os.path.join(CV_DIR, "my_cv.pdf")

    print("1. قراءة الـ CV...")
    text = load_cv_text(cv_path)

    print("2. التقطيع...")
    chunks = chunk_cv(text)
    print(f"   عدد الـ chunks: {len(chunks)}")

    print("3. توليد الـ embeddings...")
    vectors = embed_texts(chunks)
    print(vectors[0])

    [print(chunk + "\n-- New Chunk --\n") for chunk in chunks]
if __name__ == "__main__":
    main()