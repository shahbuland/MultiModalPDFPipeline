from ironpdf import PdfDocument
from PyPDF2 import PdfReader, PdfWriter
import os
from PIL import Image
import requests
import subprocess
import shutil
import numpy as np

def create_tmp_path(path):
    """
    Create tmp folder. If it exists already, delete contents and folder.
    """
    if os.path.isdir(path):
        for sub_path in os.listdir(path):
            os.remove(os.path.join(path, sub_path))
    os.makedirs(path, exist_ok = True)

def img_tmp_copy(img):
    """
    Creates a tmp copy of an img so that the original file can be deleted/cleared while
    the image itself persists
    """
    return Image.fromarray(np.asarray(img))

def load_pdf(pdf_path_or_url : str, tmp_path = "./tmp_pdf_images"):
    create_tmp_path(tmp_path)

    if not os.path.isfile(pdf_path_or_url):
        # Download the pdf file from the given URL
        response = requests.get(pdf_path_or_url)
        pdf_path = os.path.join(tmp_path, "downloaded.pdf")
        with open(pdf_path, 'wb') as f:
            f.write(response.content)
    else:
        pdf_path = pdf_path_or_url

    pdf = PdfDocument.FromFile(pdf_path)
    pdf.RasterizeToImageFiles(f"{tmp_path}/*.png",DPI=96)

    # Get every file ending with .png then sort by number (otherwise it'd be 1, 10, ... instead of 1, 2, ...)
    img_paths = os.listdir(tmp_path)
    img_paths = [path for path in img_paths if path.endswith(".png")]
    img_paths.sort(key=lambda x: int(x.split('.')[0]))
    img_paths = [os.path.join(tmp_path, path) for path in img_paths]

    imgs = [Image.open(path).convert("RGB") for path in img_paths]
    for img in imgs:
        img.load()

    shutil.rmtree(tmp_path)
    return imgs

# ==== FIGURE EXTRACTION ====

# Uses Allenai PDFfigure2, refer to repository to get that setup
def load_figures(pdf_path_or_url, tmp_path = "./tmp_pdf_figures"):
    """
    Given a PDF file, extracts all tables and figures and returns a dictionary
    - The dictionary contains labels for the tables/figures of form "figure1" or "table2" as keys
    - The values are np arrays (not PIL images, so that we can delete temp files without errors)
    """
    create_tmp_path(tmp_path)

    if not os.path.isfile(pdf_path_or_url):
        # Download the pdf file from the given URL
        response = requests.get(pdf_path_or_url)
        pdf_path = os.path.join(tmp_path, "downloaded.pdf")
        with open(pdf_path, 'wb') as f:
            f.write(response.content)
    else:
        pdf_path = pdf_path_or_url

    tmp_pdf_path = "./tmp_pdf"
    create_tmp_path(tmp_pdf_path)
    shutil.copy(pdf_path, tmp_pdf_path)

    pdf_path = f"../{tmp_pdf_path}/"
    out_path = f"../{tmp_path}/"
    wd = "./pdffigures2"

    sbt_command = f"sbt \"runMain org.allenai.pdffigures2.FigureExtractorBatchCli {pdf_path} -m {out_path}\""
    process = subprocess.Popen(sbt_command,
                                      shell=True,
                                      universal_newlines=True,
                                      cwd=wd)
    stdout, stderr = process.communicate()

    # Delete tmp_pdf folder and its contents
    shutil.rmtree(tmp_pdf_path)

    # Create a dictionary to store the images
    images_dict = {}

    # Iterate over the files in the tmp_path
    for file in os.listdir(tmp_path):
        # Check if the file is a png image
        if file.endswith(".png"):
            # Extract the figure/table name from the file name
            fig_table_name = file.split('-')[1]
            # Open the image file
            img = Image.open(os.path.join(tmp_path, file))
            # Add the image to the dictionary
            images_dict[fig_table_name.lower()] = img_tmp_copy(img)
            img.close()

    shutil.rmtree(tmp_path)
    return images_dict

def get_pdf_page_length(path : str):
    """
    Get PDF page length from path
    """
    def get_number_of_pages(file_path):
        with open(file_path, "rb") as file:
            pdf = PdfReader(file)
            total_pages = len(pdf.pages)
        return total_pages

    return get_number_of_pages(path)

def split_pdf(input_path, output_dir, chunk_size):
    """
    Splits a PDF into multiple files each containing chunk_size pages, and places them into output_dir
    """

    # Open the PDF file
    with open(input_path, "rb") as file:
        file = open(input_path, "rb")
        pdf = PdfReader(file)

        # Get the total number of pages in the PDF
        total_pages = len(pdf.pages)

        # Calculate the number of chunks
        num_chunks = total_pages // chunk_size
        if total_pages % chunk_size:
            num_chunks += 1

        # Split the PDF into chunks
        for i in range(num_chunks):
            output_path = os.path.join(output_dir, f"chunk_{i+1}.pdf")
            with open(output_path, "wb") as output_file:
                pdf_writer = PdfWriter()

                # Add pages to the chunk
                for j in range(chunk_size):
                    page_num = i * chunk_size + j
                    if page_num >= total_pages:
                        break
                    page = pdf.pages[page_num]
                    pdf_writer.add_page(page)

                # Write the chunk to a file
                pdf_writer.write(output_file)

if __name__ == "__main__":
    split_pdf("paper_cache/mltextbook.pdf", "paper_cache", 100)