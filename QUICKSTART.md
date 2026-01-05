# 快速開始 30 秒

## 第 1-2 分鐘: 安裝

```bash
git clone https://github.com/caizongxun/yt-shorts-automation.git
cd yt-shorts-automation
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

## 第 3 分鐘: 下載背景

```bash
mkdir -p assets/gameplay assets/music
# 手動下載 3-5 個 Minecraft 跑饷影片到 assets/gameplay/
# (參考 SETUP_GUIDE.md 第二部分)
```

## 第 4-5 分鐘: 生成 Shorts

```bash
python scripts/daily_pipeline.py --count 3 --voice en-male
```

## 完成！

影片保存在 `output/videos/`

​

---

## 步驟鯨逩

| 步驟 | 角色 | 作用 |
|--------|--------|----------|
| 1 | ContentScraper | 從 Reddit 抱取故事 (或用 LLM 生成) |
| 2 | AudioGenerator | 文字轉語音 (Edge-TTS) |
| 3 | VideoCompositor | 視頻 + 字幕 + 音頻合成 |
| 4 | UploadScheduler | 排程發布 (Selenium) |

---

## 單個 Shorts 的成本

| 項目 | 成本 |
|------|------|
| Edge-TTS | \\$0 |
| MoviePy | \\$0 |
| YouTube | \\$0 |
| **總計** | **\\$0** |

---

## 下一步

✅ 重輔: [SETUP_GUIDE.md](SETUP_GUIDE.md) - 完整配置步驟

✅ 架構: [ARCHITECTURE.md](ARCHITECTURE.md) - 技術細節

✅ API: [README.md](README.md) - 幼程 API 文檔

---

**應該略過這里為良，幸事！** 🎬
