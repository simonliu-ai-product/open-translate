# Open Translate - Full Stack Google Colab Runner
# Repository: https://github.com/simonliu-ai-product/open-translate.git
# This script prepares the environment and launches the server directly from the repository code.

import os
import sys

# 1. Setup requirements
def install_dependencies():
    print("Installing system dependencies (Node.js 20)...")
    !curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
    !sudo apt-get install -y nodejs
    print("Installing Python dependencies...")
    !pip install -q fastapi uvicorn pyngrok nest-asyncio transformers torch accelerate pillow opencc python-multipart python-dotenv sqlalchemy psycopg2-binary pymysql

# 2. Main execution
def main():
    # 1. Get Tokens
    try:
        from google.colab import userdata
        hf_token = userdata.get('HF_TOKEN')
        ngrok_token = userdata.get('NGROK_TOKEN')
        os.environ["HF_TOKEN"] = hf_token
    except Exception:
        print("Error: HF_TOKEN and NGROK_TOKEN must be set in Colab Secrets.")
        return

    # 2. Install Dependencies
    install_dependencies()

    # 3. Clone repository if not exists
    if not os.path.exists("open-translate"):
        print("Cloning repository...")
        !git clone https://github.com/simonliu-ai-product/open-translate.git
        %cd open-translate
    
    # 4. Build Frontend
    print("Building frontend...")
    if os.path.exists("frontend"):
        !cd frontend && npm install && npm run build
        # Copy dist to root for the backend to find it easily
        !cp -r frontend/dist .
    else:
        print("Warning: 'frontend' directory not found. API only mode.")

    # 5. Setup Ngrok
    from pyngrok import ngrok
    import nest_asyncio
    
    ngrok.set_auth_token(ngrok_token)
    public_url = ngrok.connect(8000).public_url
    
    print("\n" + "="*50)
    print(f"OPEN TRANSLATE UI: {public_url}")
    print("="*50)
    print("\nStarting server from backend/main.py...")

    # 6. Run the actual backend script
    nest_asyncio.apply()
    # We run it using the python command to ensure it uses the file in the folder
    !python backend/main.py

if __name__ == "__main__":
    main()