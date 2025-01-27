import pymupdf4llm
import pathlib
from src.utils.logger import BaseLogger

logger = BaseLogger(__name__)


class MarkdownConvertor:
    def __init__(
        self,
        input_path: str = "src/data/.pdfs",
        output_path: str = "src/data/.markdowns",
    ):
        self.input_path = input_path
        self.output_path = output_path

    def run(self):
        logger.info(f"Converting PDFs in {self.input_path} to markdown in {self.output_path}")

        for f in pathlib.Path(self.input_path).iterdir():
            if f.suffix.lower() == ".pdf":  # Ensure case insensitivity for suffix
                try:
                    logger.info(f"Converting {f.name} to markdown")

                    # Convert PDF to markdown
                    md_text = pymupdf4llm.to_markdown(str(f))  # Ensure f is passed as a string

                    # Define the output markdown file path
                    md_output_path = pathlib.Path(self.output_path, f.stem + ".md")

                    # Write the markdown content to the file
                    md_output_path.write_text(md_text, encoding="utf-8")
                    
                    logger.info(f"Markdown file saved to {md_output_path}")
                except Exception as e:
                    logger.error(f"Failed to convert {f.name}: {e}")

# Example usage
if __name__ == "__main__":
    converter = MarkdownConvertor()
    converter.run()