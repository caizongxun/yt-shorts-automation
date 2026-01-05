# 🎬 YouTube Shorts 零成本全自動生產系統

一個完全開源、無需創作靈感、純程式碼驅動的 YouTube Shorts 量產流水線。

## 核心特性

- **Content Scraper**: 自動從 Reddit 熱門貼文抓取故事內容
- **Audio Engine**: 使用 Edge-TTS 免費高品質文字轉語音 (支援多種聲線)
- **Video Compositor**: MoviePy + FFmpeg 自動合成視頻、添加字幕、Ken Burns 效果
- **Visual Randomization**: 動態背景變換、字體顏色隨機、濾鏡微調
- **Auto-uploader**: Selenium 自動上傳到 YouTube Studio、填寫標題/標籤
- **Schedule Manager**: 分散發布時間、避免「重複內容」演算法打擊

## 專案架構

```
yt-shorts-automation/
├── configs/                    # 配置檔 (OAuth、API Key、参數)
│   ├── reddit_config.json
│   ├── youtube_config.json
│   └── content_config.json
├── scripts/
│   ├── 01_fetch_reddit.py     # Reddit 故事爬蟲
│   ├── 02_generate_audio.py   # TTS 語音生成
│   ├── 03_compose_video.py    # 視頻合成主程序
│   ├── 04_upload_youtube.py   # 自動上傳
│   └── 00_setup.py            # 一鍵環境初始化
├── assets/
│   ├── gameplay/              # (需手動下載) 遊戲背景影片
│   ├── satisfying/            # (需手動下載) 紓壓影片
│   ├── music/                 # (需手動下載) 免版權背景音樂
│   └── overlays/              # 視覺特效疊層
├── output/                    # 生成的影片輸出
├── logs/                      # 運行日誌
└── requirements.txt           # 依賴包

```

## 快速開始

### 前置要求

- Python 3.9+
- NVIDIA GPU (CUDA 11.8+) - 可選，但推薦
- FFmpeg 已安裝
- Chrome/Chromium 瀏覽器 (Selenium 用)

### 安裝

```bash
# 1. Clone 專案
git clone https://github.com/caizongxun/yt-shorts-automation.git
cd yt-shorts-automation

# 2. 建立虛擬環境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 安裝依賴
pip install -r requirements.txt

# 4. 初始化配置
python scripts/00_setup.py
```

### 配置步驟

#### 1️⃣ Reddit API (可選，若只用 LLM 生成內容則跳過)

```bash
# 前往 https://www.reddit.com/prefs/apps
# 建立 "script" 應用程式，取得:
# - Client ID
# - Client Secret
# - User Agent

# 編輯 configs/reddit_config.json
{
  "client_id": "YOUR_CLIENT_ID",
  "client_secret": "YOUR_CLIENT_SECRET",
  "user_agent": "yt-shorts-bot/1.0",
  "subreddits": ["AskReddit", "NoSleep", "Confessions"],
  "sort_by": "top",
  "time_filter": "day",
  "limit": 5
}
```

#### 2️⃣ YouTube API (用於自動上傳)

```bash
# 前往 Google Cloud Console
# 啟用 YouTube Data API v3
# 下載 OAuth 2.0 認證 JSON
# 放到 configs/youtube_client_secret.json
```

#### 3️⃣ 下載背景素材

```bash
# 自動下載無版權遊戲影片
python scripts/download_assets.py --source=gameplay

# 或手動下載並放到 assets/ 資料夾
# 推薦來源:
# - YouTube: "No Copyright Gameplay Minecraft Parkour"
# - Pexels/Pixabay: 免費影片 API
# - Archive.org: 公有領域內容
```

## 核心模組說明

### 1. Content Scraper (`01_fetch_reddit.py`)

```python
# 自動抓取 Reddit 熱門故事
from scripts.content_scraper import RedditScraper

scraper = RedditScraper(config_path="configs/reddit_config.json")
stories = scraper.fetch_top_stories(
    subreddit="AskReddit",
    limit=5,
    min_length=100  # 最少字數
)
```

支援兩種內容來源：
- **Reddit API**: 真實故事，觀眾多元
- **LLM 生成**: 一致性更高，無人工成本

### 2. Audio Engine (`02_generate_audio.py`)

```python
# 文字轉語音 (0 成本)
from scripts.audio_generator import EdgeTTSEngine

engine = EdgeTTSEngine(voice="en-US-ChristopherNeural", rate="+10%")
audio_file = engine.generate("Here is a crazy fact about space...")
# 輸出: audio.mp3 (高品質，16kHz)
```

支援語言：英文、中文、日文等 100+

### 3. Video Compositor (`03_compose_video.py`)

**最複雜但最有趣的部分。**

```python
from scripts.video_compositor import ShortsCompositor

compositor = ShortsCompositor(
    background_folder="assets/gameplay/",
    music_folder="assets/music/",
    overlay_folder="assets/overlays/"
)

video = compositor.compose(
    audio_file="voiceover.mp3",
    title="Incredible Space Facts",  # 用於自動生成字幕
    randomize=True,  # 啟用隨機特效
    output_file="final_short.mp4"
)
```

內部流程：
1. 隨機選擇背景影片片段 (60 秒)
2. 使用 Whisper 提取 audio 時間軸 (每個單字的精確時間)
3. 逐字高亮字幕 (黃色 Impact 字體，黑色邊框)
4. 疊加微量背景音樂 (vol=5%)
5. 隨機色調調整 (Color Grading)
6. 編碼輸出 (H.264, 1080p, 30fps)

### 4. Auto-uploader (`04_upload_youtube.py`)

```python
from scripts.youtube_uploader import YouTubeUploader

uploader = YouTubeUploader(
    credentials_path="configs/youtube_client_secret.json"
)

uploader.upload(
    video_path="final_short.mp3",
    title="Incredible Space Facts #Shorts",
    tags=["#Shorts", "#Facts", "#Space"],
    description="Did you know...",
    schedule_time="2025-01-06 14:00:00"  # 定時發布
)
```

## 反濫用機制 (Anti-Detection)

為避免 YouTube 演算法認為您是「機器人內容農場」，系統內建以下隨機性：

| 機制 | 實作 |
|------|------|
| **背景輪替** | 動態從 5+ 個遊戲影片庫挑選 |
| **字幕樣式** | 隨機 3-5 種字體、顏色、大小 |
| **色調調整** | 每部影片微調亮度/對比 (-5% ~ +5%) |
| **背景音樂** | 隨機挑選 30 首 Lo-Fi 曲目 (5% 音量) |
| **轉場特效** | 50% 機率添加膠片雜訊 Overlay |
| **上傳排程** | 分散於 12:00, 15:00, 19:00 發布 (避免同時上傳) |
| **延遲間隔** | 兩部影片之間隨機 45-90 分鐘延遲 |

## 自動化流程 (Cron / Scheduler)

### 選項 A: Linux Cron

```bash
# 每天凌晨 3 點自動生成 3 部影片，於隔日分批發布
0 3 * * * cd /path/to/yt-shorts-automation && python scripts/daily_pipeline.py >> logs/cron.log 2>&1
```

### 選項 B: Windows Task Scheduler

```
觸發程序: 每日 03:00
執行: python C:\path\to\daily_pipeline.py
```

### 選項 C: Docker + Cloud (推薦)

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "scripts/daily_pipeline.py"]
```

部署到 Heroku/Railway/Replit，完全無成本運行 (在免費層範圍內)。

## 費用分析

| 項目 | 成本 | 備註 |
|------|------|------|
| 模型 (FLUX/SDXL) | \\$0 | 開源，本機執行 |
| TTS (Edge-TTS) | \\$0 | 免費 API |
| 合成軟體 (MoviePy/FFmpeg) | \\$0 | 開源 |
| 上傳 (YouTube) | \\$0 | 免費平台 |
| 背景素材 | \\$0 | 免版權來源 |
| **GPU 電費** | \\$5-15/月 | 僅在本機跑圖時消耗 |
| **總成本** | **\\$0-15/月** | 取決於圖生成需求 |

## 常見問題

### Q: 會被 YouTube 封號嗎？

A: 風險存在，但如果遵守以下規則會大大降低：
- ✅ 每部影片都有「隨機變量」(字體、背景、特效)
- ✅ 遵守「歸屬要求」(Reddit 內容要標註來源、使用免版權素材)
- ✅ 不做「單一主題重複」(例如只做數學題 1000 部會被判重複)
- ❌ 不要一次上傳 100 部 (會秒關頻道)

### Q: 如何增加訂閱？

A: 系統只負責「量產」。建議搭配：
- TikTok/Instagram Reels 同步發布
- 社群互動 (Reddit 回覆、Discord 社群)
- 利基市場集中 (例如只做「動漫冷知識」而非「什麼都做」)

### Q: 如何變現？

A: YouTube Shorts 收入來源：
1. **YouTube Partner Program (YPP)**: 月收 \\$100+ (需 10K 訂閱 + 100 萬次觀看)
2. **AdSense**: 最簡單，但分潤低
3. **品牌合作**: 定向商家贊助

### Q: 可以在中國用嗎？

A: YouTube 在中國被屏蔽。建議改為：
- **抖音/快手自動化** (類似邏輯，改用樂音/iBug TTS)
- **小紅書**: 漸增流量渠道

## 貢獻與改進

這是開源專案，歡迎提 PR 或 Issue！

核心可改進的地方：
- [ ] 支援多語言自動化
- [ ] 集成 ChatGPT 故事生成 (比 Ollama 更強)
- [ ] TikTok/Instagram 自動同步發布
- [ ] 實時觀看數據分析儀表板
- [ ] 字幕辨識最優化 (OCR-based)

## 免責聲明

本專案僅供教育用途。使用者需自行負責：
- ✅ 遵守 YouTube ToS (服務條款)
- ✅ 尊重他人版權 (使用免版權素材)
- ✅ 遵守當地法律

開發者不對使用本工具的任何後果負責。

---

**Last Update**: 2026-01-05  
**Maintainer**: @caizongxun  
**License**: MIT  

