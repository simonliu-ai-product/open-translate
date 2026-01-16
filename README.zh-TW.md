# Open Translate (TranslateGemma) - 繁體中文版本

基於 Google **TranslateGemma** 的開源機器翻譯服務，支援文字與圖片翻譯功能。

## 功能特色

- **文字翻譯**：支援 55 種以上語言的高品質對譯。
- **圖片翻譯**：具備多模態能力，可直接翻譯圖片中的文字。
- **繁體中文優化**：內建 OpenCC 轉換，確保輸出符合台灣繁體中文慣用語。
- **資料庫紀錄**：自動將翻譯紀錄存入資料庫（支援 SQLite, PostgreSQL, MySQL）。
- **待命模型**：服務啟動時即自動加載模型，首位使用者無需等待。
- **容器化部署**：支援 Docker 與 Docker Compose 快速部署。
- **現代化介面**：使用 React 與 Bootstrap 打造簡潔直觀的使用者介面。

## 技術棧

- **模型**：Google TranslateGemma (4B-IT)
- **後端**：FastAPI, PyTorch, Transformers, SQLAlchemy
- **前端**：React, Vite, Bootstrap, Lucide React
- **基礎架構**：Docker, Docker Compose

---

## 快速上手

### 預備條件

- 安裝 Docker 與 Docker Compose
- Hugging Face 帳號與存取token ([HF Token](https://huggingface.co/settings/tokens))
- (選配) NVIDIA GPU 以及相關 Docker GPU 支援以加速推理。

### 安裝與執行

1. **複製專案**:
   ```bash
   git clone https://github.com/simonliu-ai-product/open-translate.git
   cd open-translate
   ```

2. **設定環境變數**:
   在根目錄建立 `.env` 檔案：
   ```env
   HF_TOKEN=您的 HuggingFace token
   NGROK_TOKEN=您的 ngrok token (Colab 端使用)
   VITE_BACKEND_URL=http://localhost:8000
   DATABASE_URL=sqlite:///./sql_app.db (選填)
   ```

3. **使用 Docker Compose 啟動**:
   ```bash
   make up
   # 或
   docker-compose up -d
   ```

4. **進入網頁**:
   開啟瀏覽器並造訪 [http://localhost:3000](http://localhost:3000)。

---

## 相關連結

英文版本請參考 [README.md](./README.md)。

---

## 致謝

- [Google TranslateGemma](https://huggingface.co/collections/google/translategemma)
- [Hugging Face Transformers](https://github.com/huggingface/transformers)
- Simon Liu (Google GDE) 提供的靈感與範例腳本。
