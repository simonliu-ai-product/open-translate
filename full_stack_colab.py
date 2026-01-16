# Open Translate - Full Stack Google Colab Runner
# Repository: https://github.com/simonliu-ai-product/open-translate.git
# This script builds the environment, starts the server, and finally exposes it via ngrok once ready.

import os
import time
import subprocess
import requests
import threading

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
    print("Building frontend... (This takes about 1-2 minutes)")
    if os.path.exists("frontend"):
        !cd frontend && npm install && npm run build
        !cp -r frontend/dist .
    else:
        print("Warning: 'frontend' directory not found.")

    # 5. Start Server in background
    print("\nStarting server and loading TranslateGemma model...")
    print("(This will take a few minutes, ngrok will start once the model is ready)")
    
    server_process = subprocess.Popen(
        ["python", "backend/main.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    # Thread to print server logs in real-time
    def print_logs(proc):
        for line in proc.stdout:
            print(f"[Server] {line.strip()}")
    
    log_thread = threading.Thread(target=print_logs, args=(server_process,))
    log_thread.daemon = True
    log_thread.start()

    # 6. Wait for server to be healthy
    max_retries = 60
    ready = False
    for i in range(max_retries):
        try:
            # Check the health endpoint
            response = requests.get("http://localhost:8000/api/health", timeout=2)
            if response.status_code == 200 and response.json().get("model_loaded"):
                ready = True
                break
        except:
            pass
        time.sleep(10)
        if i % 3 == 0:
            print(f"Waiting for model to load... ({i*10}s)")

    if not ready:
        print("Error: Server timed out during model loading.")
        server_process.terminate()
        return

    # 7. Finally, setup Ngrok
    from pyngrok import ngrok
    import nest_asyncio
    
    ngrok.set_auth_token(ngrok_token)
    public_url = ngrok.connect(8000).public_url
    
    print("\n" + "="*60)
    print("🎉 MODEL IS READY AND STANDBY!")
    print(f"👉 OPEN TRANSLATE UI: {public_url}")
    print("="*60 + "\n")

    # Keep the main thread alive while the server is running
    try:
        server_process.wait()
    except KeyboardInterrupt:
        print("Shutting down...")
        server_process.terminate()

if __name__ == "__main__":
    main()