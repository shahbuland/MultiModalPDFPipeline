from downloading_utils import download_if_not_present, get_id_without_ext
import os
from pdf_processing import PDFProcessor
import pdf_utils
from data_utils import PDFObject, join_pdf_objects
import joblib
from tqdm import tqdm
import shutil

"""
This is the main script to create a multimodal dataset from a list of URLs to PDFs
1. PDFs are downloaded into the cache directory from a file with URLs. 
2. During processing, memory overflows are possible, so the papers are chunked in order to only scan 
certain numbers of pages at once.
3. Output goes into write path with a different folder for every PDF. Each folder has text files
for each page in the PDF independently (numbered accordingly). Figures and tables have a naming
convention to match them with the pages they are from.
"""


cache_dir = "./paper_cache"
write_path = "output_dataset"
chunk_size = 50 # For PDFs with many pages like books, split into this size

if __name__ == "__main__":
    # Step 1: Iterate through paper_urls and download anything not already present
    with open('paper_urls.txt', 'r') as file:
        for url in file:
            url = url.strip()
            download_if_not_present(url, cache_dir)

    # Step 2: Iterate through the papers in cache dir
    pdf_processor = PDFProcessor()
    for paper in tqdm(os.listdir(cache_dir)):
        # Skip non-pdf files (i.e. skip tmp folders)
        if not paper.endswith(".pdf"):
            continue

        output_dir = f"{write_path}/{get_id_without_ext(paper)}"
        if os.path.exists(output_dir) and any(fname.endswith('.txt') for fname in os.listdir(output_dir)):
            continue
        path = os.path.join(cache_dir, paper)

        # Check if it's too large
        if pdf_utils.get_pdf_page_length(path) <= chunk_size:
            pdf_obj : PDFObject = pdf_processor(path)
            pdf_obj.save(output_dir)
        else:
            # Create a tmp directory that chunks the PDF into chunk_size PDFs
            tmp_path = f"{cache_dir}/pdf_chunks"
            pdf_utils.create_tmp_path(tmp_path)
            pdf_utils.split_pdf(path, tmp_path, chunk_size)

            pdf_objs = []
            for chunk in os.listdir(tmp_path):
                chunk_path = os.path.join(tmp_path, chunk)
                pdf_objs.append(pdf_processor(chunk_path))

            # Join then save
            pdf_obj = join_pdf_objects(pdf_objs)
            pdf_obj.save(output_dir)

            # Remove the temp dir
            shutil.rmtree(tmp_path)
            







