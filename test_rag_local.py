import pypdf
print("PyPDF is successfully installed and imported!")

def chunk_text(text: str, chunk_size: int = 800, overlap: int = 150):
    chunks = []
    if not text:
        return chunks
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        if end == len(text):
            break
        start += chunk_size - overlap
    return chunks

test_text = "Google Antigravity adalah platform kecerdasan buatan enterprise premium. Platform ini dirancang untuk memberdayakan Account Manager (AM) agar dapat mengelola portofolio korporasi mereka secara dinamis, reaktif, dan cerdas. Dengan arsitektur agen otonom, sistem ini terus-menerus memindai berita industri, mendeteksi sinyal pembelian, dan menyuplai asisten kueri RAG yang andal."
chunks = chunk_text(test_text, chunk_size=150, overlap=30)
print(f"Original length: {len(test_text)} characters")
print(f"Generated {len(chunks)} chunks:")
for idx, chunk in enumerate(chunks):
    print(f"  Chunk #{idx + 1}: '{chunk}'")
