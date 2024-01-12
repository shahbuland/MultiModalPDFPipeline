from read_dataset import read_dataset

ds = read_dataset("output_dataset")

print("Done")
print(ds['train'][0].keys())
print(ds['train'][0]['text'][2])
print(ds['train'][0]['figure'])