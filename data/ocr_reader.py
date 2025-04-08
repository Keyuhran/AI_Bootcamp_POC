import pathlib
import pymupdf4llm

# Define the data folder path
data_folder = pathlib.Path("data")
output_folder = pathlib.Path("output_markdown")

# Create output folder if not exists
output_folder.mkdir(parents=True, exist_ok=True)

# Loop over all PDF files in the data folder
for pdf_file in data_folder.glob("*.pdf"):
    print(f"Processing: {pdf_file.name}")
    
    # Convert PDF to markdown
    md_text = pymupdf4llm.to_markdown(str(pdf_file))

    # Print markdown text
    print(md_text)

    # Save markdown text to a file with the same name as the PDF
    output_path = output_folder / (pdf_file.stem + ".md")
    output_path.write_text(md_text, encoding="utf-8")

    print(f"Saved markdown to {output_path}\n")
