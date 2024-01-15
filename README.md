# MultiModalPDFPipeline
Data pipeline to read PDFs with figures for multimodal model training using [Nougat](https://huggingface.co/facebook/nougat-base)

# Setup
Please install all the requirements (`pip install -r requirements.txt`) to be able to use Nougat and process PDFs. On top of that you need .NET framework and cloning the repository for PDFFigures into this repository Scala Build Tool. SBT can be installed easily using [coursier](https://get-coursier.io/docs/cli-installation) and running `cs setup`. After this ensure coursier's bin folder is in your path (it should be added automatically, albeit with a soft restart to whatever terminal you're using). 

# Usage
Put URLs of PDFs you're interested in downloading into `paper_urls.txt`. If you want to add your own PDFs, create a folder called `paper_cache` and put the PDFs in it. Then, run `python -m write_dataset` to create the output dataset.  
If you want to detach the captions from the text (i.e. put them into a json file so that it's easier to tell which captions are associated with which figure/table) run `python -m detach_captions`.  
To read the contents of the dataset in a simple format for downstream uses, check out the function in `read_dataset.py` or `read_dataset_2.py`. The former is for when you want to detach captions in place, the latter assumes detach_captions has been used on the dataset.
