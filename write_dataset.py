from downloading_utils import download_if_not_present
import os
from pdf_processing import PDFProcessor, PDFObject
import joblib

"""
This is the main script to create a multimodal dataset from a list of URLs to PDFs
"""

cache_dir = "./paper_cache"
if __name__ == "__main__":
    # Step 1: Iterate through paper_urls and download anything not already present
    with open('paper_urls.txt', 'r') as file:
        for url in file:
            url = url.strip()
            download_if_not_present(url, cache_dir)

    # Step 2: Iterate through the papers in cache dir
    pdf_processor = PDFProcessor()
    for paper in os.listdir(cache_dir):
        path = os.path.join(cache_dir, paper)
        pdf_obj : PDFObject = pdf_processor(path)
        joblib.dump(pdf_obj, "pdf.joblib")
