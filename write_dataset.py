from downloading_utils import download_if_not_present, get_id_without_ext
import os
from pdf_processing import PDFProcessor
from data_utils import PDFObject
import joblib
from tqdm import tqdm

"""
This is the main script to create a multimodal dataset from a list of URLs to PDFs
"""

cache_dir = "./paper_cache"
write_path = "output_dataset"

if __name__ == "__main__":
    # Step 1: Iterate through paper_urls and download anything not already present
    with open('paper_urls.txt', 'r') as file:
        for url in file:
            url = url.strip()
            download_if_not_present(url, cache_dir)

    # Step 2: Iterate through the papers in cache dir
    pdf_processor = PDFProcessor()
    for paper in tqdm(os.listdir(cache_dir)):
        output_dir = f"{write_path}/{get_id_without_ext(paper)}"
        if os.path.exists(output_dir) and any(fname.endswith('.txt') for fname in os.listdir(output_dir)):
            continue

        path = os.path.join(cache_dir, paper)
        pdf_obj : PDFObject = pdf_processor(path)
        pdf_obj.save(output_dir)
