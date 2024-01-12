import os
from PIL import Image
import re

"""
This scripts provides a method to read from the resulting dataset created.
It has no dependencies on anything else from this repository, allowing it to be plugged in 
wherever it is needed. It returns the dataset as a dictionary. 
The following assumptions are made:
- Figures and tables are assumed to always be at the end of a page

The dictionary has keys: (each dictionary represents a single doc)
    - text: The raw text of the document in pages (List[str])
    - figure: Iterables of Triples of figures with their captions and page numbers 
        - List[Tuple[int, str, Image]] or List[Tuple[int, str, str]] 
        - Type changes depending on whether img_paths_only is called
    - table: Same data type as figures
"""

def read_dataset(ds_path, train_test = None, img_paths_only = False):
    """
    Return dictionary of dataset given path to it.

    :param train_test: Training fraction. Set to none to return just the dataset as train split
    :param img_paths_only: Whether to return Images or paths to them
    """

    # Notes on directory structures:
    # Top level is a folder containing a different folder for every individual document
    # Each documents folder contains all its pages numbered 00000000.txt ....
    # Figures or tables are numbered by page they appear on along with suffix, i.e.:
    # 00000000-figure1.png or 00000000-table1.png
    # Captions for figures or tables appear at end of their corresponding page as "Figure 1: ..." or "Table 1: ..."
    
    # Check if the file is a tar file
    if ds_path.endswith('.tar'):
        import tarfile
        with tarfile.open(ds_path, 'r') as tar:
            tar.extractall()

        # Update ds_path to the extracted directory
        ds_path = os.path.splitext(ds_path)[0]

    document_paths = os.listdir(ds_path)
    if train_test:
        doc_paths_train = document_paths[:int(train_test * len(document_paths))]
        doc_paths_tests = document_paths[int(train_test * len(document_paths)):]
    else:
        doc_paths_train = document_paths
        doc_paths_test = []

    def extract_file_info(path):
        """
        Extract info from file names. Namely, the page number, the figure/table number, and whether page is text/figure/table
        Returns a tuple (classification, page_num, num)
            - classification is one of "text", "figure", "table"
            - page_num is an int
            - num is None if "text" otherwise an int
        """

        base_path = os.path.basename(path)
        page_num = int(base_path[:8])
        
        if base_path.endswith(".txt"):
            return ("text", page_num, None)
        elif base_path.endswith(".png"):
            if base_path[8:].startswith("-table"):
                num = int(base_path[14:-4])
                return ("table", page_num, num)
            elif base_path[8:].startswith("-figure"):
                num = int(base_path[15:-4])
                return ("figure", page_num, num)
        else:
            raise ValueError("Invalid path for dataset")

    def extract_captions(page_text : str, valid_nums):
        """
        Separate page text from any captions near end

        :param page_text: The full text from the page
        :param valid_nums: List of ints representing the numbers for the captions we are still looking for
        """
        text = page_text
        
        figure_table_pattern = re.compile(r"(Figure|Table) \d+: ")
        matches = list(figure_table_pattern.finditer(text))

        captions = {} # Dict mapping numbers to captions

        for match in reversed(matches):
            if not valid_nums: # Break early if no captions left to look for
                break # May prevent cases where text is referencing some other caption and that results in text being cut short

            caption = text[match.start():]
            text = text[:match.start()]
        
            num = int(caption[caption.find(" "):caption.find(":")]) # the number is between space and colon: Figure X:
            if num in valid_nums:
                captions[num] = caption

        return text, captions
    
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

        figure_queue = {}
        table_queue = {}

        # Sort so that digits stay in order
        # images will always come before text
        def custom_sort_key(file_path):
            basename = os.path.basename(file_path)
            digits = int(basename[:8])
            is_txt = basename.endswith(".txt")
            return (digits, is_txt)

        files.sort(key=custom_sort_key)

        for file in files: # Iterating throughe very file for a document
                (file_type, page_num, num) = extract_file_info(file)
                if file_type == "text":
                    with open(file, 'r') as f:
                        text_content = f.read()
                        text_content, captions = extract_captions(
                            text_content,
                            list(figure_queue.keys()) + list(table_queue.keys()) # Combine keys
                        ) # Split text from instances of captions. Only look for captions corresponding to figures/tables already in queue
                        for key in captions: # Iterate over the found captions
                            if key in figure_queue: # If the key corresponds to a figure, remove from queue and add to figures
                                figure_path = figure_queue[key]
                                figures.append((page_num, captions[key], figure_path if img_paths_only else Image.open(figure_path)))
                                del figure_queue[key]
                            if key in table_queue: # Like-wise if table
                                table_path = table_queue[key]
                                tables.append((page_num, captions[key], table_path if img_paths_only else Image.open(table_path)))
                                del table_queue[key]

                        pages.append(text_content)
                elif file_type == "figure": # If its a figure or table, just add to queue until we find matching page
                    figure_queue[num] = file
                elif file_type == "table":
                    table_queue[num] = file

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