from ironpdf import *
import os
from PIL import Image
import requests
import subprocess
import shutil

def load_pdf(pdf_path_or_url : str, tmp_path = "./tmp_pdf_images"):

    os.makedirs(tmp_path, exist_ok=True)

    #Empty pre-emptively
    for file in os.listdir(tmp_path):
        os.remove(os.path.join(tmp_path, file))

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
    return imgs

# Should be deprecated, keeping while testing above code further
"""
def load_pdf_url(pdf_url : str, tmp_path = "./tmp_pdf_images"):
    
    #Empty pre-emptively
    for file in os.listdir(tmp_path):
        os.remove(os.path.join(tmp_path, file))

    # Download the pdf file from the given URL
    response = requests.get(pdf_url)
    pdf_path = os.path.join(tmp_path, "downloaded.pdf")
    with open(pdf_path, 'wb') as f:
        f.write(response.content)

    pdf = PdfDocument.FromFile(pdf_path)
    os.makedirs(tmp_path, exist_ok=True)
    pdf.RasterizeToImageFiles(f"{tmp_path}/*.png",DPI=96)

    img_paths = os.listdir(tmp_path)
    img_paths = [path for path in img_paths if path.endswith(".png")]
    img_paths.sort(key=lambda x: int(x.split('.')[0]))
    img_paths = [os.path.join(tmp_path, path) for path in img_paths]

    imgs = [Image.open(path).convert("RGB") for path in img_paths]
    
    return imgs
"""

# ==== FIGURE EXTRACTION ====

PDFFIGURES2_PATH = "../pdffigures2"
SBT_PATH = "C:\\Users\\smati\\AppData\\Local\\Coursier\\data\\bin"
os.environ["PATH"] += os.pathsep + SBT_PATH

# Uses Allenai PDFfigure2, refer to repository to get that setup
def load_figures(pdf_path_or_url, tmp_path = "./tmp_pdf_figures"):
    #Empty pre-emptively

    if os.path.isdir(tmp_path):
        shutil.rmtree(tmp_path)
    os.makedirs(tmp_path, exist_ok=True)
    

    for file in os.listdir(tmp_path):
        os.remove(os.path.join(tmp_path, file))

    if not os.path.isfile(pdf_path_or_url):
        # Download the pdf file from the given URL
        response = requests.get(pdf_path_or_url)
        pdf_path = os.path.join(tmp_path, "downloaded.pdf")
        with open(pdf_path, 'wb') as f:
            f.write(response.content)
    else:
        pdf_path = pdf_path_or_url

    tmp_pdf_path = "./tmp_pdf"
    if os.path.exists(tmp_pdf_path):
        shutil.rmtree(tmp_pdf_path)
    os.makedirs(tmp_pdf_path, exist_ok=True)
    shutil.copy(pdf_path, tmp_pdf_path)

    pdf_path = os.path.abspath(tmp_pdf_path)
    out_path = os.path.abspath(tmp_path)
    pdf_path = pdf_path.replace("\\", "/")
    out_path = out_path.replace("\\", "/")
    
    wd = os.path.abspath(PDFFIGURES2_PATH)

    print(pdf_path)
    print(out_path)
    print(os.listdir(wd))
    #command = ' '.join(['run-main', 'org.allenai.pdffigures2.FigureExtractorBatchCli', pdf_path, '-m', out_path, '-d', out_path])
    sbt_command = f"sbt \"runMain org.allenai.pdffigures2.FigureExtractorBatchCli {pdf_path}/ -m {out_path}/\""
    print(sbt_command)
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
            images_dict[fig_table_name] = img

    return images_dict
