from transformers import NougatProcessor, VisionEncoderDecoderModel

device = 'cuda'
processor = NougatProcessor.from_pretrained("facebook/nougat-base")
model = VisionEncoderDecoderModel.from_pretrained("facebook/nougat-base").to(device)

from pdf_utils import load_pdf, load_figures

imgs = load_pdf("https://arxiv.org/pdf/1706.03762.pdf")
figs = load_figures("attention.pdf")

print(figs.keys())

exit()

pixel_values = processor(imgs[2], data_format = "channels_first", return_tensors = "pt").pixel_values.to(device)

outputs = model.generate(
    pixel_values,
    min_length = 1,
    max_new_tokens = 30
)

sequence = processor.batch_decode(outputs, skip_special_tokens = True)[0]
sequence = processor.post_process_generation(sequence, fix_markdown = False)

print("==============================")
print(sequence)