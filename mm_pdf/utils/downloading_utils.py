import os
import hashlib
import urllib.request

def url_to_filename(url : str):
    """
    Simple way to convert URLs to 1 to 1 file names by hashing into 16 digit numbers
    """
    hash_object = hashlib.sha1(url.encode())
    hex_dig = hash_object.hexdigest()
    return f"{hex_dig[:16]}.pdf"

def get_id_without_ext(path : str):
    """
    Return filename without .pdf extension
    """
    return path[:path.find(".")]

def download_if_not_present(paper_url : str, cache_dir = "./paper_cache"):
    """
    Given paper URL and cache folder checks if paper was already downloaded
    """
    os.makedirs(cache_dir, exist_ok=True)
    fp = url_to_filename(paper_url)
    file_path = os.path.join(cache_dir, fp)

    if not os.path.exists(file_path):
        try:
            urllib.request.urlretrieve(paper_url, file_path)
        except:
            raise Exception(f"Failed to retrieve PDF from URL {paper_url}, check if URL is valid.")
    
    return file_path

