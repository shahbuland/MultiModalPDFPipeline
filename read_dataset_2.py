import os
import json
from PIL import Image

def read_dataset(ds_path, train_test = None, img_paths_only = False):
    """
    Return dictionary of dataset given path to it.

    :param train_test: Training fraction. Set to none to return just the dataset as train split
    :param img_paths_only: Whether to return Images or paths to them
    """

    document_paths = os.listdir(ds_path)
    if train_test:
        doc_paths_train = document_paths[:int(train_test * len(document_paths))]
        doc_paths_tests = document_paths[int(train_test * len(document_paths)):]
    else:
        doc_paths_train = document_paths
        doc_paths_test = []

    def process_document(doc_path):
        """
        Process a single document into its corresponding components.
        Returns dictionary with keys:
            - text : list of text from each page of the document
            - figure : list of triples of all figures from the doc with (page_num, caption, path or image)
            - table : list of triples of all tables (same format as figures)
        """

        pages = []
        figures = []
        tables = []

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
                    pages.append(text_content)
            elif file.endswith("-media.json"):
                with open(file, 'r') as f:
                    media_content = json.load(f)
                    for figure in media_content["figures"]:
                        figure_path = os.path.join(doc_path, f"{os.path.basename(file)[:8]}-figure{figure['id']}.png")
                        figures.append((int(os.path.basename(file)[:8]), figure["caption"], figure_path if img_paths_only else Image.open(figure_path)))
                    for table in media_content["tables"]:
                        table_path = os.path.join(doc_path, f"{os.path.basename(file)[:8]}-table{table['id']}.png")
                        tables.append((int(os.path.basename(file)[:8]), table["caption"], table_path if img_paths_only else Image.open(table_path)))

        return {
            "text" : pages,
            "figure" : figures,
            "table" : tables
        }

    def process_subset(doc_paths):
        res = []

        for path in doc_paths: # Iterating through documents
            res.append(
                process_document(os.path.join(ds_path, path))
            )

        return res
    
    return {
        "train" : process_subset(doc_paths_train),
        "test" : process_subset(doc_paths_test)
    }
