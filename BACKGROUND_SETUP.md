# 背景影片設置指南

## 影片長度限制？沒有！

**答案：完全沒有限制！**

系統會自動處理任何長度的影片：

| 影片長度 | 系統處理方式 |
|--------|----------|
| 短影片 (< 60 秒) | 自動循環播放直到達到語音長度 |
| 中等影片 (1-10 分鐘) | 隨機選擇一個片段 |
| 長影片 (1 小時+) | 隨機截取所需長度的片段 |
| 多部影片 | 每次隨機選一部,隨機截取位置 |

---

## 技術細節

### 自動分割演算法

```python
當您提供 1 小時影片，系統需要 45 秒語音時：

1. 加載影片 (1 小時)
2. 計算可用起始位置:
   max_start = 3600 - 45 = 3555 秒
3. 隨機選擇起始點:
   start_time = random.uniform(0, 3555)  # 例如 1234 秒
4. 截取片段:
   segment = 1234 秒 ~ 1279 秒
5. 縮放到 1080x1920 (Shorts 比例)
6. 套用特效和字幕
7. 輸出 MP4 檔案

每次執行都會隨機選擇不同位置 ✓
```

### 支援的格式

| 格式 | 支援 | 說明 |
|------|------|------|
| MP4 | ✓ | 最佳選擇 |
| MOV | ✓ | Apple 格式 |
| AVI | ✓ | 舊格式 |
| MKV | ✓ | 容器格式 |
| WebM | ✓ | 開源格式 |

---

## 推薦影片來源

### 1. YouTube (最簡單)

**搜尋關鍵字：**
- "Minecraft Parkour No Copyright"
- "Relaxing Gameplay 1080p"
- "Gaming Background Video"
- "Code Rain Background"
- "Cinematic Footage No Copyright"

**無版權頻道推薦：**
- Pixabay Videos (https://pixabay.com/videos/)
- Pexels Videos (https://www.pexels.com/videos/)
- YouTube Audio Library (免費)

**下載方法：**

```bash
# 使用 youtube-dl (需要安裝)
pip install youtube-dl

youtube-dl -f 22 "[VIDEO_URL]" -o "assets/gameplay/%(title)s.%(ext)s"
```

或使用線上工具：
- SaveFrom.net
- Y2Mate.com
- 4K Video Downloader

### 2. Pexels (推薦)

官網：https://www.pexels.com/videos/

**優點：**
- ✓ 完全免費
- ✓ 無版權
- ✓ 高清質量
- ✓ 可商用
- ✓ 無需註冊

**下載步驟：**
1. 搜尋你想要的影片 ("gaming", "nature", etc.)
2. 點擊影片
3. 點擊「Download」
4. 選擇 720p 或 1080p
5. 儲存到 `assets/gameplay/`

### 3. Pixabay (推薦)

官網：https://pixabay.com/videos/

**優點：**
- ✓ 1000+ 免費影片
- ✓ 高清
- ✓ 無版權

**下載步驟：**
1. 搜尋 ("gaming", "nature", "abstract")
2. 點擊影片
3. 選擇解析度並下載
4. 儲存到 `assets/gameplay/`

---

## 完整步驟

### 步驟 1: 建立資料夾

```bash
mkdir -p assets/gameplay
cd assets/gameplay
```

### 步驟 2: 下載影片

**方法 A: 從 Pexels 下載 (最簡單)**

1. 打開 https://www.pexels.com/videos/
2. 搜尋「gaming」或「nature」
3. 點擊影片 → Download → 選擇解析度
4. 儲存到 `assets/gameplay/` 資料夾

**方法 B: 從 YouTube 下載**

```bash
# 安裝 youtube-dl
pip install youtube-dl

# 下載單個影片
youtube-dl -f 22 "https://www.youtube.com/watch?v=..." -o "assets/gameplay/gameplay_1.mp4"
```

**方法 C: 使用你自己的影片**

```bash
# 複製你的影片到資料夾
cp ~/Videos/my_gameplay.mp4 assets/gameplay/
```

### 步驟 3: 驗證設置

```bash
# 檢查檔案
ls -lh assets/gameplay/

# 應該看到：
# -rw-r--r-- user group 1.2G gameplay_1.mp4
# -rw-r--r-- user group 856M gameplay_2.mp4
```

### 步驟 4: 執行系統

```bash
python scripts/manual_daily_pipeline.py --count 3
```

系統會自動：
1. 隨機選擇 `assets/gameplay/` 中的影片
2. 隨機截取所需長度的片段
3. 縮放到 1080x1920 (Shorts 比例)
4. 添加字幕和語音
5. 輸出 3 部影片

---

## 常見問題

### Q: 影片可以是 1080p 嗎？

**A:** 可以！系統會自動縮放到 1080x1920 (Shorts 比例)。

推薦規格：
- 解析度：720p 或 1080p 以上
- 格式：MP4 (H.264 編碼)
- 寬高比：任何比例都可以
- 檔案大小：沒有限制

### Q: 一定要放多部影片嗎？

**A:** 不需要！系統支持：
- ✓ 1 部超長影片 (1 小時+)
- ✓ 3-5 部中等影片
- ✓ 混合長度影片

系統每次都會隨機選擇不同位置，所以生成的影片不會重複。

### Q: 能使用手機錄製的影片嗎？

**A:** 可以！手機影片通常是 9:16 比例 (直向)，系統會自動處理。

### Q: 影片會被修改或壓縮嗎？

**A:** 是的，系統會：
1. 縮放到 1080x1920
2. 設定 30 FPS
3. 用 H.264 編碼 (標準格式)
4. 添加字幕和語音

這確保 YouTube 最佳相容性。

### Q: 如何避免每次使用同一段落？

**A:** 系統已內建隨機化：

```python
# 自動隨機選擇起始位置
start_time = random.uniform(0, max_start)

# 即使只有 1 部 1 小時影片
# 每次執行都會截取不同位置
```

例如：
- 第 1 次執行：取 0:00-1:00
- 第 2 次執行：取 15:30-16:30
- 第 3 次執行：取 42:00-43:00

### Q: 能混用不同來源的影片嗎？

**A:** 完全可以！

```
assets/gameplay/
├── minecraft_parkour.mp4      (YouTube 下載)
├── nature_scenes.mp4          (Pexels)
├── my_gameplay.mp4            (自己錄製)
└── cinematic_footage.mp4      (Pixabay)
```

系統每次都會隨機選一部。

---

## 技術參數

### 輸出規格

```
解析度: 1080 x 1920 (9:16 Shorts 比例)
FPS: 30
編碼: H.264 (libx264)
音頻編碼: AAC
位元率: 自適應
```

### 自動調整邏輯

```
如果背景影片太短 (< 所需長度)
  ├─ 自動循環播放
  └─ 達到所需長度後停止

如果背景影片太長 (> 所需長度)
  ├─ 計算最大起始位置
  ├─ 隨機選擇起始點
  └─ 截取所需長度片段

寬高比調整:
  ├─ 如果太寬 → 裁剪兩側
  └─ 如果太高 → 裁剪上下
  ├─ 最後縮放到 1080x1920
```

---

## 快速設置 (5 分鐘)

### 最簡單方法

```bash
# 1. 建立資料夾
mkdir assets/gameplay

# 2. 下載任何 MP4 影片放進去
# (從 Pexels / Pixabay / YouTube)

# 3. 執行
python scripts/manual_daily_pipeline.py --count 3
```

就這樣！✓

---

## 檔案大小參考

| 影片長度 | 解析度 | 檔案大小 | 下載時間 |
|--------|--------|--------|----------|
| 1 分鐘 | 720p | ~50 MB | 10 秒 |
| 5 分鐘 | 1080p | ~200 MB | 30 秒 |
| 10 分鐘 | 1080p | ~400 MB | 1 分鐘 |
| 1 小時 | 1080p | ~2.4 GB | 5 分鐘 |

**建議：** 下載 1-2 部 10 分鐘的影片就足夠了。

---

## 正常運作檢查清單

- [ ] 建立了 `assets/gameplay/` 資料夾
- [ ] 下載了至少 1 個 MP4 檔案
- [ ] 影片檔案在 `assets/gameplay/` 中
- [ ] 執行 `python scripts/manual_daily_pipeline.py --count 3`
- [ ] 檢查 `output/videos/` 中的結果

如果一切順利，應該看到：
```
output/videos/
├── manual_short_00.mp4 ✓
├── manual_short_01.mp4 ✓
└── manual_short_02.mp4 ✓
```

---

**就是這樣！** 你已經準備好製作 YouTube Shorts 了 🎬
