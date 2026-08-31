import json

batch_size = 10
total_files = 57

batches = [list(range(i, min(i + batch_size, total_files))) for i in range(0, total_files, batch_size)]

for b_idx, b in enumerate(batches):
    with open(f"val_prompt_{b_idx}.txt", "w", encoding="utf-8") as f:
        f.write(f"You are an expert Swedish semantic validator for CEFR B1 (SFI D). Your task is to process articles {b[0]} to {b[-1]}.\n\n")
        f.write("For EACH of the following JSON files, you must:\n")
        f.write("1. Read the file.\n")
        f.write("2. Validate the `sv` text for SFI D fluency and correct any awkward grammar (do NOT remove any target words).\n")
        f.write("3. Translate the final `sv` text to English (the `en` field).\n")
        f.write("4. Overwrite the file using `write_to_file` with the updated JSON. Ensure you include the `en` field and keep `sv`, `target_words`, etc.\n\n")
        f.write("Here are the files you need to process in this batch:\n")
        for idx in b:
            f.write(f"- course/sfid/phase2/article_{idx}.json\n")
        
        f.write("\nIMPORTANT: Please use your `write_to_file` tool to save each updated article back to its original path. Once you have successfully updated all files in this batch, reply to me saying 'Batch complete'.\n")

print(f"Generated {len(batches)} validation prompts.")
