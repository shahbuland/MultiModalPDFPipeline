from typing import Iterable
import os
from PIL import Image

class PDFPage:
    """
    Object to represent a single page from any PDF

    :param text: The text on the page (MD format)
    :param image_identifiers: List of identifiers for the image (i.e. figure1, table1, etc.)
    :param images: The images on that page
    """
    def __init__(self, text : str, image_identifiers : Iterable[str], images : Iterable[Image.Image]):
        self.text = text
        self.image_identifiers = image_identifiers
        self.images = images
        
class PDFObject:
    """
    Object to represent a PDF file with figure locations and images embedded appropriately
    """
    def __init__(self, pages = []):
        self.pages = pages

    def add_page(self, page : PDFPage):
        self.pages.append(page)
    
    def save(self, path : str):
        """
        Saves to path given in the following manner: 
        - each page is given an 8-digit ID
        - The text from the page is saved as [id].txt
        - each image is saved as [id]-[photoid].txt 
        """
        os.makedirs(path, exist_ok=True)
        for i, page in enumerate(self.pages):
            page_id = str(i).zfill(8)
            with open(f"{path}/{page_id}.txt", "w", errors = "ignore") as text_file:
                text_file.write(page.text)
            for (id, img) in zip(page.image_identifiers, page.images):
                img.save(f"{path}/{page_id}-{id}.png")

def join_pdf_objects(ls : Iterable[PDFObject]) -> PDFObject:
    """
    Join multiple PDF objects by appending pages. May not account for multiple figures
    having the same identifiers.
    """
    return PDFObject([page for obj in ls for page in obj.pages])


