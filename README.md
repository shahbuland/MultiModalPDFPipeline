# MultiModalPDFPipeline
Data pipeline to read PDFs with figures for multimodal model training

# Setup
Please install all the requirements (`pip install -r requirements.txt`) to be able to use Nougat and process PDFs. On top of that you need .NET framework and cloning the repository for PDFFigures into this repository Scala Build Tool. SBT can be installed easily using [coursier](https://get-coursier.io/docs/cli-installation) and running `cs setup`. After this ensure coursier's bin folder is in your path (it should be added automatically, albeit with a soft restart to whatever terminal you're using). 

# Usage
Put URLs of PDFs you're interested in downloading into `paper_urls.txt`. If you want to add your own PDFs, create a folder called `paper_cache` and put the PDFs in it. Then, run `python -m write_dataset` to create the output dataset.
