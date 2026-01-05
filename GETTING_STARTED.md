# 得來不慑 - 兩種工作流程

選擇你想要的方式：

---

## 📝 **方案 A: 手動內容** (推薦綠手)

你提供故事 → 系統自動製作影片

### 安裝 (2 分鐘)

```bash
git clone https://github.com/caizongxun/yt-shorts-automation.git
cd yt-shorts-automation
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux
pip install -r requirements.txt
```

### 使用 (5 分鐘)

**第一次使用：建立範例桀案檔**

```bash
python scripts/manual_daily_pipeline.py --create-examples
```

這會在 `content/` 目錄建立：
- `example_story_1.txt`
- `example_story_2.txt`
- `example_story_3.txt`

**恢複你的故事（你可以記載我）：**

```bash
python scripts/manual_daily_pipeline.py --count 3
```

**影片輸出**: `output/videos/`

✅ **完成！** 

### 詳細文檔

- 📚 [MANUAL_WORKFLOW.md](MANUAL_WORKFLOW.md) - 完整指南
- 📚 [ARCHITECTURE.md](ARCHITECTURE.md) - 技術細節

### 月佳打算

```
Day 1 晚上
  └─ 你寫或我歷生 3 個故事 (30 分鐘)
     └─ 貼到 content/ 目錄

Day 2 凌晨 3 點
  └─ 系統自動生成 3 部影片 (5-10 分鐘待機)

Day 2 操作
  └─ 手動上傳或㌿営自動上傳
```

---

## 🤖 **方案 B: 完全自動** (可選)

Reddit 或 LLM 自動產生內容 + 自動上傳

### 安裝 (10 分鐘)

同上 (前 2 步) + 配置：

```bash
# 1. 配置 Reddit API (可選)
cp configs/reddit_config.example.json configs/reddit_config.json
# 编輯 config 並填入 API key

# 2. 配置 YouTube OAuth
cp configs/youtube_config.example.json configs/youtube_config.json
# 按慧事初始收授權

# 3. 選項：本地 Ollama (使用 LLM)
ollama run mistral
```

### 使用 (1 指令)

```bash
python scripts/daily_pipeline.py --count 3 --upload
```
✅ **完全自動！**

### 詳細文檔

- 📚 [SETUP_GUIDE.md](SETUP_GUIDE.md) - 完整配置教學

---

## 比較

| 水準 | 方案 A (手動) | 方案 B (自動) |
|--------|------------------|------------------|
| 上手綛幅 | ⭐⭐ (10 分) | ⭐⭐⭐ (30 分) |
| 一次性配置 | 標準 | 複雜 |
| 枡控怎準 | 很高 | 低 |
| 🤖 API 顯示彨 | 不需要 | 有 (Reddit, YouTube) |
| 水斥工壁 | 何 | 可能掉時 |
| 成本 | $0 | $0 |

---

## 常見問題

### 我想用手動，但想記載你瘢泰故事：

完美！我可以帴時符組故事給你，你往 `content/` 目錄貼和執行程式。

✅ **標準流程**:
1. 储存为 3 個 `.txt` 檔案
2. 執行 `manual_daily_pipeline.py`
3. 初始光惑

### 我想料每天自動生成，但不想手動提供內容:

標 Reddit 作家模式！使用 [daily_pipeline.py](scripts/daily_pipeline.py)。

你需要：
- Reddit API (30 秒取得)
- LLM (本地 Ollama 操作)
✅ [SETUP_GUIDE.md](SETUP_GUIDE.md) 有教學

### 背景影片資源？

**方案 A (hand-picked)**
- 下載 Minecraft 跑饷 贐簠 → `assets/gameplay/`
- 或使用你自己的內容 MP4
- 適於 1080p+

**方案 B (自動)**
- 系統自動改變背景位置與长度

---

## 下一步

✅ 選擇方案 A 或 B

✅ 根據方案 按階執行

✅ 檢查 `output/videos/` 中的結果

✅ (a)  手動上傳或 (b) 設定自動上傳

---

**祝你成功！** 🎬

有重急問題？會畫憨量，我就從容。
