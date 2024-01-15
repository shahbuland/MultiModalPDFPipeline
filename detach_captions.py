"""
This script is a utility that disentangles figure/table captions from dataset
"""
import os
import re
import json
from typing import Dict, List

def extract_captions(page_text : str):
    """
    Separate page text from any captions near end

    :param page_text: The full text from the page
    """
    text = page_text
    
    figure_table_pattern = re.compile(r"(Figure|Table) \d+: ")
    matches = list(figure_table_pattern.finditer(text))

    captions = [] # List of dictionaries

    for match in reversed(matches):
        caption = text[match.start():]
        text = text[:match.start()]
        
        id = int(caption[caption.find(" "):caption.find(":")]) # the number is between space and colon: Figure X:
        captions.append({"id": id, "caption": caption})

    return text, captions

def process_document(doc_path):
    """
    Process a single document into its corresponding components.
    """

    files = os.listdir(doc_path)
    files = [os.path.join(doc_path, fp) for fp in files]

    # Sort so that digits stay in order
    def custom_sort_key(file_path):
        basename = os.path.basename(file_path)
        digits = int(basename[:8])
        is_txt = basename.endswith(".txt")
        return (digits, is_txt)

    files.sort(key=custom_sort_key)

    for file in files: # Iterating through every file for a document
        if file.endswith(".txt"):
            with open(file, 'r') as f:
                text_content = f.read()
                text_content, captions = extract_captions(text_content)

                # Write the modified text back to the file
                with open(file, 'w') as f:
                    f.write(text_content)

                # Write the captions to a json file
                with open(os.path.join(doc_path, f"{os.path.basename(file)[:8]}-media.json"), 'w') as f:
                    json.dump({"figures": [c for c in captions if "Figure" in c["caption"]],
                               "tables": [c for c in captions if "Table" in c["caption"]]}, f)

def process_folder(folder_path):
    """
    Process all documents in a folder.
    """
    document_paths = os.listdir(folder_path)

    for doc_path in document_paths: # Iterating through documents
        process_document(os.path.join(folder_path, doc_path))

if __name__ == "__main__":
    process_folder("output_dataset")
