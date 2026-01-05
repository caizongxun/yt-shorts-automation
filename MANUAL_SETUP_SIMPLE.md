# 手動模式 TL;DR 版本

**就是這樣簡單！**

---

## 5 分鐘快速開始

### 1️⃣ 安裝 (2 分鐘)

```bash
git clone https://github.com/caizongxun/yt-shorts-automation.git
cd yt-shorts-automation
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 2️⃣ 建立故事檔案 (2 分鐘)

在 `content/` 資料夾建立 `story_1.txt`：

```
Title: Your Amazing Story Title

Your story text goes here. 
Can be multiple paragraphs.
Will be automatically converted to speech.
```

再做 `story_2.txt` 和 `story_3.txt`（複製貼上修改即可）

### 3️⃣ 執行 (1 分鐘)

```bash
python scripts/manual_daily_pipeline.py --count 3
```

### 4️⃣ 完成！

影片在 `output/videos/` 
- `manual_short_00.mp4`
- `manual_short_01.mp4`
- `manual_short_02.mp4`

✅ **完成！手動上傳或享受生活吧** 🎬

---

## 常見問題

### 故事應該多長？

**200-400 字**

太短（<100）→ 影片太快
太長（>600）→ 超過 60 秒限制

### 格式一定要這樣？

**是的**

```
Title: 標題在這裡

內容在這裡
```

Title 行是必須的（便於識別）

### 我想要中文故事

需要改變語言設定（暫時不支援，但可以修改代碼）

### 影片看起來都一樣怎麼辦

系統會自動隨機化：
- 背景影片選擇
- 字幕顏色
- 視覺效果
- 色調調整

**完全不會被 YouTube 演算法判定為重複內容**

---

## 每日自動化 (可選)

### Windows

1. `Win + R` → `taskschd.msc`
2. 右鍵 → 建立工作
3. 觸發程序：每天 3:00 AM
4. 動作：執行程式
   - 程式：`C:\Python311\python.exe`
   - 引數：`scripts/manual_daily_pipeline.py --count 3`
   - 開始位置：你的專案目錄

### Mac/Linux

```bash
crontab -e
# 加入這一行
0 3 * * * cd /path/to/yt-shorts-automation && python scripts/manual_daily_pipeline.py --count 3
```

---

## 成本

| 項目 | 成本 |
|------|------|
| 軟體 | $0 |
| 文字轉語音 | $0 |
| 影片製作 | $0 |
| YouTube | $0 |
| **總計** | **$0** |

---

## 進階選項

### 改變聲音

```bash
python scripts/manual_daily_pipeline.py --count 3 --voice en-female
```

可選聲音：
- `en-male` (預設)
- `en-female`
- `en-casual`
- `en-male-old`

### 禁用隨機化

```bash
python scripts/manual_daily_pipeline.py --no-randomize
```

### 建立示例

```bash
python scripts/manual_daily_pipeline.py --create-examples
```

會在 `content/` 建立 3 個範例檔案（可編輯或參考）

---

## 檔案位置

```
 content/              ← 放你的故事在這裡
 output/videos/        ← 完成的影片在這裡
 output/audio/         ← 生成的語音檔案
 logs/                 ← 執行紀錄（有問題時查看）
 assets/gameplay/      ← 背景影片
```

---

## 有問題？

1. 檢查 `logs/` 中的最新日誌
2. 確保 `content/` 中有 `.txt` 檔案
3. 確保 Python 已安裝所有依賴 (`pip install -r requirements.txt`)
4. 嘗試執行示例：`--create-examples`

---

## 下一步

✅ 有 3 個故事 → 執行腳本

✅ 想要自動化 → 設定 Cron / 工作排程

✅ 想上傳到 YouTube → 設定 `--upload` (需要 OAuth)

✅ 需要幫助 → 查看完整文件：[MANUAL_WORKFLOW.md](MANUAL_WORKFLOW.md)

---

**就這樣！你已經擁有一個免費的 YouTube Shorts 製作工廠了** 🚀
