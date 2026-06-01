# PDF Parsing with PyMuPDF
import fitz

def extract_text_from_pdf(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        full_text = ""

        for page in doc:
            full_text += page.get_text()

        doc.close()

        if not full_text.strip():
            return "No text found — PDF may be image only"

        return full_text

    except FileNotFoundError:
        return "Error: PDF file not found"
    except Exception as e:
        return f"Error: {e}"


# Test 1 — real PDF
print("--- TEST 1: Real PDF ---")
text = extract_text_from_pdf("test_resume.pdf")
print(text)

# Test 2 — wrong file
print("\n--- TEST 2: Wrong file ---")
print(extract_text_from_pdf("fake.pdf"))

# Test 3 — page count
print("\n--- TEST 3: Page count ---")
doc = fitz.open("test_resume.pdf")
print(f"Total pages: {doc.page_count}")
doc.close()

# Test 4 — page by page
print("\n--- TEST 4: Page by page ---")
doc = fitz.open("test_resume.pdf")
for i, page in enumerate(doc):
    print(f"Page {i+1}:")
    print(page.get_text())
    print("---")
doc.close()