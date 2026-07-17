import requests
from pathlib import Path


def main():
    p = Path("tmp_test.pdf")
    # minimal pdf bytes
    pdf_bytes = b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n1 0 obj<</Type/Catalog>>endobj\ntrailer\n<<>>\n%%EOF\n"
    p.write_bytes(pdf_bytes)

    headers = {"Origin": "http://localhost:3000"}
    try:
        with p.open("rb") as pdf_file:
            files = {"file": ("tmp_test.pdf", pdf_file, "application/pdf")}
            r = requests.post("http://127.0.0.1:8000/api/v1/content/upload", files=files, headers=headers)

        print("STATUS", r.status_code)
        try:
            print(r.text)
        except Exception:
            print("No text")
    finally:
        p.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
