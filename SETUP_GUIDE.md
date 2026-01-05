# YouTube Shorts 自動化系統 - 完整設置指南

## 目錄

1. [快速開始](#快速開始)
2. [環境設置](#環境設置)
3. [配置步驟](#配置步驟)
4. [運行方式](#運行方式)
5. [背景素材下載](#背景素材下載)
6. [常見問題](#常見問題)

---

## 快速開始

假設你已安裝 Python 3.9+，以下 5 分鐘內快速啟動：

```bash
# 1. Clone 專案
git clone https://github.com/caizongxun/yt-shorts-automation.git
cd yt-shorts-automation

# 2. 建立虛擬環境
python -m venv venv
source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate     # Windows

# 3. 安裝依賴
pip install -r requirements.txt

# 4. 下載背景素材 (可選)
mkdir -p assets/gameplay assets/music
# 參考下面的「背景素材下載」章節

# 5. 生成 3 個影片
python scripts/daily_pipeline.py --count 3 --voice en-male
```

完成！影片將保存到 `output/videos/`

---

## 環境設置

### 先決條件

- **Python 3.9+**
- **FFmpeg**: 用於視頻處理
  - macOS: `brew install ffmpeg`
  - Ubuntu/Debian: `sudo apt-get install ffmpeg`
  - Windows: 下載 [ffmpeg.org](https://ffmpeg.org/download.html)

- **Chrome/Chromium** (可選，用於 YouTube 上傳)
- **GPU (可選)**：用於 AI 圖片生成，但不是必需的

### 依賴包說明

| 包名 | 用途 | 成本 |
|------|------|------|
| `edge-tts` | 免費文字轉語音 | \\$0 |
| `moviepy` | 視頻合成 | \\$0 |
| `praw` | Reddit 數據爬蟲 | \\$0 (需配置) |
| `selenium` | YouTube 自動上傳 | \\$0 (需配置) |
| `whisper` | 音頻轉錄 (提取時間軸) | \\$0 |

---

## 配置步驟

### 1. Reddit API 配置 (可選)

如果要從 Reddit 自動抓取故事：

#### 步驟 A: 創建 Reddit 應用

1. 訪問 [reddit.com/prefs/apps](https://reddit.com/prefs/apps)
2. 點擊 "Create Another App"
3. 選擇 "script"
4. 填寫表單：
   - Name: "yt-shorts-bot"
   - Redirect URI: `http://localhost:8080`
5. 點擊 "Create app"
6. 複製：
   - **Client ID** (藍色部分)
   - **Client Secret** (點擊 "secret")

#### 步驟 B: 配置 configs/reddit_config.json

```bash
cp configs/reddit_config.json.example configs/reddit_config.json
```

編輯 `configs/reddit_config.json`：

```json
{
  "client_id": "YOUR_CLIENT_ID_HERE",
  "client_secret": "YOUR_CLIENT_SECRET_HERE",
  "user_agent": "yt-shorts-bot/1.0 by YOUR_REDDIT_USERNAME",
  "subreddits": ["AskReddit", "NoSleep", "Confessions"],
  "sort_by": "top",
  "time_filter": "day",
  "limit": 5,
  "min_length": 100
}
```

### 2. YouTube Upload 配置 (可選)

如果要自動上傳到 YouTube：

#### 步驟 A: 啟用 YouTube Data API

1. 訪問 [Google Cloud Console](https://console.cloud.google.com)
2. 創建新項目 (或選擇現有)
3. 搜尋 "YouTube Data API v3" 並啟用
4. 建立 OAuth 2.0 認證：
   - 類型：Desktop Application
   - 下載 JSON 認證檔
5. 將文件保存為 `configs/youtube_client_secret.json`

#### 步驟 B: 配置 Chrome WebDriver

```bash
# 下載適合你 Chrome 版本的 ChromeDriver
# https://chromedriver.chromium.org/

# 放到系統 PATH 或專案根目錄
cp chromedriver /usr/local/bin/
```

### 3. 本地 LLM 配置 (用於內容生成，避免 ChatGPT 付費)

如果不用 Reddit API：

```bash
# 安裝 Ollama
curl https://ollama.ai/install.sh | sh

# 下載 Llama 2 模型
ollama run llama2

# Ollama 會在 http://localhost:11434 運行
# 系統會自動連接
```

---

## 運行方式

### 方式 1: 單次運行

```bash
# 生成 3 個影片 (不上傳)
python scripts/daily_pipeline.py --count 3

# 生成 5 個影片，使用女性聲音
python scripts/daily_pipeline.py --count 5 --voice en-female

# 生成並排隊上傳到 YouTube
python scripts/daily_pipeline.py --count 3 --upload

# 測試模式 (不生成任何文件)
python scripts/daily_pipeline.py --dry-run
```

### 方式 2: 每日自動運行

#### Linux/macOS (使用 Cron)

```bash
# 編輯 crontab
crontab -e

# 在文件末尾添加 (每天凌晨 3 點運行)
0 3 * * * cd /path/to/yt-shorts-automation && python scripts/daily_pipeline.py --count 3 >> logs/cron.log 2>&1
```

#### Windows (使用任務排程器)

1. 打開 "任務排程器"
2. 右鍵 > "建立工作"
3. 名稱: "YouTube Shorts Pipeline"
4. 觸發程序: 每日 03:00
5. 動作:
   ```
   程式: C:\path\to\python.exe
   引數: C:\path\to\scripts\daily_pipeline.py --count 3
   ```
6. 確定

#### Docker (雲端部署，推薦)

```bash
# 建構 Docker 映像
docker build -t yt-shorts-bot .

# 本地測試
docker run -v $(pwd)/output:/app/output yt-shorts-bot python scripts/daily_pipeline.py --count 1

# 部署到 Heroku/Railway/Replit (參考各平台文檔)
```

---

## 背景素材下載

### 方法 1: 自動下載 (需配置 YouTube API)

```bash
python scripts/download_assets.py --source=gameplay --count=10
```

### 方法 2: 手動下載

#### 遊戲背景 (Minecraft 跑酷，最推薦)

1. YouTube 搜尋："No Copyright Gameplay Minecraft Parkour"
2. 推薦頻道：
   - [No Copyright Gameplay](https://www.youtube.com/@NocopyrightGameplay)
   - [Kratos World](https://www.youtube.com/@KratosWorld)
3. 下載 3-5 個 10-20 分鐘的影片
4. 放到 `assets/gameplay/`

```bash
# 使用 yt-dlp 自動下載
pip install yt-dlp
yt-dlp -f "bestvideo[height<=1080]" -o "assets/gameplay/%(title)s.%(ext)s" "YOUTUBE_PLAYLIST_URL"
```

#### 背景音樂 (Lo-Fi，可選)

1. YouTube Audio Library (YouTube Studio 內免費)
2. Pexels Music
3. Pixabay Music
4. 放到 `assets/music/`

#### 紓壓影片 (Oddly Satisfying)

1. Pexels Videos 搜尋 "slime", "soap"
2. Pixabay 搜尋 "satisfying"
3. 放到 `assets/satisfying/`

---

## 常見問題

### Q: 生成的影片沒有字幕？

A: 需要安裝 Whisper 模型：

```bash
pip install openai-whisper
python -c "import whisper; whisper.load_model('base')"
```

第一次運行會自動下載 ~140MB 的模型檔。

### Q: 無法連接 Reddit API？

A: 檢查 configs/reddit_config.json：
- Client ID/Secret 是否正確？
- User Agent 是否包含你的 Reddit 用戶名？

### Q: YouTube 上傳失敗？

A: 需要手動登入一次：

```bash
python scripts/youtube_uploader.py  # 會打開瀏覽器要求登入
```

之後可以自動上傳。

### Q: 如何更改語音？

A: 支援的語音：
- `en-male` (推薦，深沉男聲)
- `en-female` (自然女聲)
- `en-casual` (隨便男聲)
- `en-male-old` (老年男聲)

```bash
python scripts/daily_pipeline.py --count 3 --voice en-female
```

或編輯 `daily_pipeline.py` 的預設值。

### Q: 如何跳過 YouTube 上傳？

A: 默認不上傳。只有加入 `--upload` 才會上傳：

```bash
# 只生成影片，不上傳
python scripts/daily_pipeline.py --count 3

# 生成並上傳
python scripts/daily_pipeline.py --count 3 --upload
```

### Q: 成本多少？

A: 完全免費，除了電費：
- Edge-TTS: \\$0
- MoviePy/FFmpeg: \\$0 (開源)
- YouTube: \\$0 (免費平台)
- 背景素材: \\$0 (公開領域 + 免版權)
- **唯一成本**: 圖片生成的 GPU 電費 (~\\$5-15/月)

### Q: 可以用 GPU 加速嗎？

A: Whisper 支援 GPU。編輯 `scripts/video_compositor.py`：

```python
model = whisper.load_model("base", device="cuda")
```

需要 NVIDIA GPU + CUDA 11.8+。

---

## 下一步

1. 根據上述步驟完成配置
2. 生成第一批 3 個影片：`python scripts/daily_pipeline.py --count 3`
3. 檢查 `output/videos/` 文件夾
4. 設置每日自動運行
5. 監控 `logs/` 文件夾查看運行日誌

## 支援

遇到問題？
1. 檢查 `logs/` 目錄的錯誤日誌
2. 閱讀本文檔的常見問題
3. GitHub Issues 提交問題
4. 修改代碼並提 PR！

---

**祝你成功！** 🎬🚀
