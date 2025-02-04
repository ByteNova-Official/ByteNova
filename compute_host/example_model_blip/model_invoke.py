import requests
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
import json

processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-large")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-large").to("cuda")

def invoke(input_text):
    try:
        input_json = json.loads(input_text)
        text = input_json['text']
        image_url = input_json['image_url']
    except:
        text = ""
        image_url = input_text
    raw_image = Image.open(requests.get(image_url, stream=True).raw).convert('RGB')
    if text:
        inputs = processor(raw_image, text, return_tensors="pt").to("cuda")
    else:
        inputs = processor(raw_image, return_tensors="pt").to("cuda")
    out = model.generate(**inputs)
    return processor.decode(out[0], skip_special_tokens=True)
