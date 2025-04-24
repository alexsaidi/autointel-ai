import os
import shutil
import openai
import datetime
import traceback

# Set OpenAI key from environment
openai.api_key = os.getenv("OPENAI_API_KEY")

APP_FILENAME = "app.py"
BACKUP_DIR = "backups"
SELF_FILE = "self_update.py"

# Ensure backup directory exists
os.makedirs(BACKUP_DIR, exist_ok=True)

def timestamp():
    return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

def backup_app():
    ts = timestamp()
    backup_path = os.path.join(BACKUP_DIR, f"{APP_FILENAME}.{ts}.bak")
    shutil.copy(APP_FILENAME, backup_path)
    return backup_path

def load_code(path):
    with open(path, "r") as f:
        return f.read()

def save_code(path, content):
    with open(path, "w") as f:
        f.write(content)

def enhance_code_with_gpt(prompt, code):
    print("🔧 Sending code to GPT for enhancement...")
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are AutoIntel AI, the smartest software engineer assistant. "
                    "Improve this Streamlit app code by adding enhancements, fixes, performance gains, "
                    "and prepare it to become smarter over time."
                ),
            },
            {"role": "user", "content": f"{prompt}\n\n{code}"},
        ],
        temperature=0.7,
    )
    return response.choices[0].message["content"]

def self_enhance():
    try:
        print("🧠 Starting self-enhancement process...")

        # Step 1: Backup
        backup_path = backup_app()
        print(f"✅ Backup created at: {backup_path}")

        # Step 2: Read current code
        original_code = load_code(APP_FILENAME)

        # Step 3: Generate enhanced code
        enhanced_code = enhance_code_with_gpt(
            prompt="Enhance this Streamlit app and implement smart self-learning features.",
            code=original_code
        )

        # Step 4: Save new version
        save_code(APP_FILENAME, enhanced_code)
        print("✅ Enhanced code written successfully!")

    except Exception as e:
        print("❌ Enhancement failed! Rolling back...")
        traceback.print_exc()

        # Restore backup
        shutil.copy(backup_path, APP_FILENAME)
        print("✅ Rolled back to last working version.")

if __name__ == "__main__":
    self_enhance()
