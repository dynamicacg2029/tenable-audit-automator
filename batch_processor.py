import os
import json
from openai import OpenAI
from src.logic.validator import validate_regex

# --- Configuration ---
INPUT_DIR = "data/input_docs"
OUTPUT_FILE = "outputs/batch_compliance.audit"
# Ensure these folders exist
os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs("outputs", exist_ok=True)

client = OpenAI(api_key="YOUR_OPENAI_API_KEY")

def split_requirements(text):
    """
    Splits bulk text into individual requirements. 
    Customizable based on the standard (IRS vs STIG).
    """
    # Simple split based on double newlines; can be upgraded to Regex split
    chunks = [c.strip() for c in text.split("\n\n") if len(c.strip()) > 50]
    return chunks

def process_batch():
    all_audit_items = []
    
    for filename in os.listdir(INPUT_DIR):
        if filename.endswith(".txt"):
            with open(os.path.join(INPUT_DIR, filename), "r") as f:
                content = f.read()
                requirements = split_requirements(content)
                
                print(f"🔍 Found {len(requirements)} requirements in {filename}...")
                
                for i, req in enumerate(requirements):
                    print(f"  -> Processing Item {i+1}...")
                    
                    # LLM Call for each chunk
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "system", "content": "Convert to Tenable custom_item JSON."},
                                  {"role": "user", "content": req}],
                        response_format={"type": "json_object"}
                    )
                    
                    item_json = json.loads(response.choices[0].message.content)
                    
                    # Logic to format as Tenable text
                    audit_text = f"<custom_item>\n"
                    for k, v in item_json.items():
                        audit_text += f"  {k.ljust(12)} : \"{v}\"\n"
                    audit_text += "</custom_item>"
                    
                    all_audit_items.append(audit_text)

    # Wrap in Tenable Header
    final_file = '<check_type: "Unix">\n\n' + "\n\n".join(all_audit_items) + "\n\n</check_type>"
    
    with open(OUTPUT_FILE, "w") as out:
        out.write(final_file)
    print(f"✅ Success! Batch file saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    process_batch()
