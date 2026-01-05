# PyCharm 影片下載快速指南

**只需貼 URL，一鍵下載 720p MP4！**

---

## 安裝依賴 (一次性)

### 方法 1: 在 PyCharm 終端執行

打開 PyCharm 底部的 **Terminal** (或 `Alt + F12`)，執行：

```bash
pip install yt-dlp
```

### 方法 2: 更新完整依賴

```bash
pip install -r requirements.txt
```

---

## 開始下載

### 在 PyCharm 中執行

1. **打開 PyCharm**
2. **按 `Ctrl + Alt + R` 或右下角選 Terminal**
3. **執行下載工具**

```bash
python tools/download_background.py
```

### 會看到這樣的提示

```
============================================================
YouTube/Pexels/Pixabay Video Downloader (720p)
============================================================

Supported sources:
  - YouTube: youtube.com/watch?v=...
  - Pexels: pexels.com/video/...
  - Pixabay: pixabay.com/videos/...
  - Any video URL

[INPUT] Paste video URL (or 'quit' to exit): 
```

---

## 使用方式

### 從 Pexels 下載

1. 打開 https://www.pexels.com/videos/
2. 搜尋 "gaming" 或 "minecraft"
3. 點擊任何影片
4. **複製網址列的 URL**
5. **貼到 PyCharm Terminal**

```
[INPUT] Paste video URL (or 'quit' to exit): https://www.pexels.com/video/1234567/flying-over-mountains/
[INPUT] Quality (default 720, or enter custom): 720
[START] Downloading video...
  URL: https://www.pexels.com/video/1234567/flying-over-mountains/
  Quality: 720p
  Format: MP4
  Output: assets/gameplay

[PROCESSING] Extracting video info...
  Title: Flying Over Mountains
  Duration: 15 seconds

[DOWNLOADING] Starting download...
  Progress: 45.5% at 1.2MB/s ETA: 00:05
```

### 從 YouTube 下載

1. 搜尋 "Minecraft Parkour No Copyright"
2. 複製影片網址
3. 貼到 Terminal

```
[INPUT] Paste video URL: https://www.youtube.com/watch?v=dQw4w9WgXcQ
```

### 從 Pixabay 下載

1. 打開 https://pixabay.com/videos/
2. 搜尋並複製 URL
3. 貼上

```
[INPUT] Paste video URL: https://pixabay.com/videos/download/video-1234567/
```

---

## 完整流程示例

### 情境：想要 5 部背景影片

```bash
# 1. 啟動下載工具
python tools/download_background.py

# 2. 第一個影片
[INPUT] Paste video URL: https://www.pexels.com/video/123/
[INPUT] Quality: 720
# (等待下載完成)
[SUCCESS] Download completed!
  File: assets/gameplay/Flying_Over_Mountains.mp4
  Size: 125.34 MB

[INPUT] Download another video? (y/n): y

# 3. 第二個影片
[INPUT] Paste video URL: https://www.pexels.com/video/456/
...

# 4-5. 繼續下載其他影片
# ...

# 6. 完成
[INPUT] Download another video? (y/n): n
[EXIT] All done! Your videos are in: assets/gameplay/
```

### 現在可以製作影片

```bash
python scripts/manual_daily_pipeline.py --count 3
```

---

## 快捷方式 (更快)

### 如果知道 URL，直接加參數

```bash
python tools/download_background.py "https://www.pexels.com/video/123/"
```

自動下載，無需互動！

### 指定自訂品質

```bash
python tools/download_background.py "https://youtube.com/watch?v=..." 1080
```

下載 1080p

---

## 支持的來源

| 來源 | 支援度 | 品質 | 需要帳戶 |
|------|------|------|----------|
| **YouTube** | ✅ 完全 | 720p-4K | ❌ 否 |
| **Pexels** | ✅ 完全 | 最高 720p | ❌ 否 |
| **Pixabay** | ✅ 完全 | 最高 1080p | ❌ 否 |
| **Vimeo** | ✅ 大部分 | 取決於影片 | ⚠️ 部分 |
| **Facebook** | ✅ 大部分 | 720p | ⚠️ 部分 |
| **Twitter/X** | ✅ 大部分 | 720p | ⚠️ 部分 |
| 其他網址 | ✅ 大部分 | 取決於影片 | ✅ 變數 |

---

## 常見問題

### Q: 下載很慢怎麼辦?

**A:** 這是正常的，取決於：
- 你的網路速度
- 影片大小
- 伺服器速度

通常 10 分鐘的 720p 影片需要 1-5 分鐘。

### Q: 可以下載 1080p 或 4K 嗎?

**A:** 可以！但比較慢且檔案大：

```bash
python tools/download_background.py "[URL]" 1080
```

不過系統最終都會縮放到 1080x1920 (Shorts 比例)，所以 720p 就夠了。

### Q: 下載失敗怎麼辦?

**A:** 嘗試：

1. **檢查網路連線**
   ```bash
   ping google.com
   ```

2. **更新 yt-dlp**
   ```bash
   pip install --upgrade yt-dlp
   ```

3. **嘗試不同 URL**
   - 某些 YouTube 影片可能有地區限制
   - 試試 Pexels 或 Pixabay

4. **檢查檔案權限**
   ```bash
   ls -l assets/gameplay/
   ```

### Q: 影片會被存在哪裡?

**A:** 自動存在 `assets/gameplay/` 資料夾

```
yt-shorts-automation/
└── assets/
    └── gameplay/
        ├── Gaming_Background_1.mp4
        ├── Minecraft_Parkour.mp4
        └── ...
```

### Q: 可以邊下載邊製作影片嗎?

**A:** 可以！只要有 1 部影片，就能開始製作：

**終端 1 (下載):**
```bash
python tools/download_background.py
```

**終端 2 (製作):**
```bash
python scripts/manual_daily_pipeline.py --count 3
```

### Q: 下載後能刪除嗎?

**A:** 可以！刪除 `assets/gameplay/` 中的檔案即可

```bash
rm assets/gameplay/unwanted_video.mp4
```

系統會自動從剩餘影片中選擇。

---

## 推薦影片尋找流程

### 最簡單方式 (Pexels)

1. 打開 https://www.pexels.com/videos/
2. 搜尋 "gaming"
3. 找到喜歡的影片
4. 點進去 → 複製網址
5. 貼到 PyCharm Terminal
6. 完成！

### 5 分鐘內完成

```
打開 Pexels (30 秒)
   ↓
搜尋 "minecraft" (15 秒)
   ↓
選擇影片並複製 URL (30 秒)
   ↓
貼到 PyCharm Terminal (5 秒)
   ↓
下載中... (2-3 分鐘)
   ↓
完成，可以製作影片了！
```

---

## 進階選項

### 只下載音頻

```bash
python tools/download_background.py "[URL]" "audio"
```

### 設定自訂檔名

編輯 `tools/download_background.py` 第 85 行：
```python
'outtmpl': str(self.output_dir / 'my_custom_name.%(ext)s'),
```

### 批量下載 (進階)

建立 `download_list.txt`：
```
https://www.pexels.com/video/123/
https://www.pexels.com/video/456/
https://www.pexels.com/video/789/
```

然後執行：
```bash
while IFS= read -r url; do
    python tools/download_background.py "$url"
done < download_list.txt
```

---

## 完整使用示例

```bash
# 1. 安裝
pip install yt-dlp

# 2. 下載 3 部影片
python tools/download_background.py
# (貼 3 個 URL，每個下載完後選 y)

# 3. 檢查已下載
ls assets/gameplay/
# 應該看到 3 個 MP4 檔案

# 4. 建立故事
# 在 content/ 建立 story_1.txt, story_2.txt, story_3.txt

# 5. 製作影片
python scripts/manual_daily_pipeline.py --count 3

# 6. 上傳
# 在 output/videos/ 中找到 3 部完成的影片
# 上傳到 YouTube Shorts
```

---

**就這樣！你已經有了完整的自動化系統** 🎬
