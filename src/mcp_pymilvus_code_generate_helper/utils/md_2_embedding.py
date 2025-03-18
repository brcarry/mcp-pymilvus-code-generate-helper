import os

import pandas as pd
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
docs_dir_path = "/Users/zilliz/Downloads/web-content-master/v2.5.x/site/en/userGuide"
save_file_name = "user_guide.csv"

markdown_files = []
for root, dirs, files in os.walk(docs_dir_path):
    for file in files:
        if file.endswith(".md"):
            markdown_files.append(os.path.join(root, file))

print(f"Found {len(markdown_files)} Markdown files to process")

df = pd.DataFrame(columns=["metadata", "content", "embedding", "file_name"])
processed_count = 0

for file_index, markdown_path in enumerate(markdown_files):
    print(f"Processing file [{file_index + 1}/{len(markdown_files)}]: {markdown_path}")
    file_name = os.path.basename(markdown_path)

    try:
        with open(markdown_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"Failed to read file: {e}")
        continue

    print(f"Content length: {len(content)} characters")

    try:
        print("Generating embedding...")
        response = client.embeddings.create(model="text-embedding-3-small", input=content)
        embedding = response.data[0].embedding
        print(f"Generation successful! Embedding dimension: {len(embedding)}")

        df.loc[len(df)] = {
            "metadata": "",
            "content": content,
            "embedding": embedding,
            "file_name": file_name,
        }

        processed_count += 1

        if processed_count % 10 == 0:
            temp_path = os.path.join("embeddings_temp.csv")
            df.to_csv(temp_path, index=False)
            print(
                f"Saved temporary results to: {temp_path}, processed {processed_count} documents so far"
            )

    except Exception as e:
        print(f"Failed to generate embedding: {e}")

print("All documents process finished.")

output_path = os.path.join(save_file_name)
df.to_csv(output_path, index=False)

print(f"Successfully generated embeddings and saved to: {output_path}")
print(f"Dataset size: {len(df)} rows x {len(df.columns)} columns")
