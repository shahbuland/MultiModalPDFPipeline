from transformers import NougatProcessor, VisionEncoderDecoderModel
from PIL import Image
from typing import Iterable
import ironpdf
from pdf_utils import load_pdf, load_figures
import re
import os

from data_utils import PDFPage, PDFObject

def find_image_identifiers(text : str) -> Iterable[str]:
    """
    Given a passage of text, find all references to figures in the following way:
    - Nougat puts figures and tables at end of a page, in the following form:
        \"Figure X: [caption]\" or \"Table X: [caption]\"
    - The key component here is the word Figure or Table, followed by a space, followed by a number, and then followed by a colon (:)
    - This script finds every such occurence and returns a list of the form [\"FigureX\", \"TableX\", ...]
    - These are used to associate the page with figures or tables found from the overall PDF
    """
    pattern = r"(?:Figure|Table) \d+:"
    identifiers = re.findall(pattern, text)

    # Get rid of spaces, lowercase first letter, and remove colon from end
    identifiers = [identifier.replace(" ", "").lower()[:-1] for identifier in identifiers]
    return identifiers

def extract_from_dict(d : dict, keys : Iterable[str]):
    """
    Given dictionary and keys, extracts those keys and deletes them.
    Crucially, checks for existence of every key and skips keys that weren't in dictionary
    Returns the dictionary elements and the keys for values that were succesfully extracted
    """
    return_keys = []
    return_values = []

    for k in keys:
        if k in d:
            return_keys.append(k)
            return_values.append(d[k])
            del d[k]
    
    return return_keys, return_values

class PDFProcessor:
    """
    Wrapper around Nougat to encapsulate processing a single PDF page into text and images

    :param device: Device to run Nougat on
    :param max_tokens_per_page: How many tokens to attempt to parse from each page. Should normally be set very high to ensure entire page is read.
    """
    def __init__(self, device = 'cuda', max_tokens_per_page = 20000):
        self.device = device
        self.processor = NougatProcessor.from_pretrained("facebook/nougat-base")
        self.model = VisionEncoderDecoderModel.from_pretrained("facebook/nougat-base").to(device)
        self.max_tokens_per_page = max_tokens_per_page

    def call_nougat(self, img : Image.Image):
        pixel_values = self.processor(img, data_format = "channels_first", return_tensors = "pt").pixel_values.to(self.device)
        
        outputs = self.model.generate(
            pixel_values,
            min_length = 1,
            max_new_tokens = self.max_tokens_per_page
        )

        sequence = self.processor.batch_decode(outputs, skip_special_tokens = True)[0]
        sequence = self.processor.post_process_generation(sequence, fix_markdown = False)

        return sequence

    def __call__(self, pdf_path : str) -> PDFObject:
        """
        Given path to PDF file returns PDFObject representation
        """
        # pdf pages as images
        page_imgs : Iterable[Image.Image] = load_pdf(pdf_path)
        # Dictionary of all figures from the PDF 
        figs : dict = load_figures(pdf_path)

        pdf_obj = PDFObject()

        for i, page_img in enumerate(page_imgs):
            raw_text = self.call_nougat(page_img)
            img_ids = find_image_identifiers(raw_text)

            img_ids, imgs = extract_from_dict(figs, img_ids)

            pdf_obj.add_page(
                PDFPage(
                    raw_text,
                    img_ids,
                    imgs
                )
            )

        return pdf_obj
