from sentence_transformers import SentenceTransformer

model = SentenceTransformer("distiluse-base-multilingual-cased-v2")
model.save("models/distiluse-base-multilingual-cased-v2")