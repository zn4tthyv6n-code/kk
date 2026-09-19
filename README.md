# 旅程提案所：GitHub Pages 與離線版

這是一套 GitHub Pages 靜態網站，加上 GitHub Actions 官網資料同步程式。
不需要 OpenAI／ChatGPT 帳號或金鑰；使用者不需要安裝 Python。Python 僅在 GitHub 排程主機執行。

**不是即時庫存系統。** 每 6 小時嘗試讀取可樂旅遊公開官網，成功後發布新的資料快照。頁面載明同步時間；搜尋在瀏覽器本機執行。LINE 送出需要網路。

## 你的儲存庫

已確認儲存庫：https://github.com/zn4tthyv6n-code/iris
現有網站：https://zn4tthyv6n-code.github.io/iris/
本更新包不需刪除原有根目錄檔案。改選 GitHub Actions 發布後，網站內容取自程式產生的 `site/`，不再使用舊的根目錄 `index.html`。

## 上傳與啟用

1. 建立 GitHub 儲存庫，使用 `main` 作為預設分支。公開儲存庫可使用 GitHub Free 的 Pages。
2. 將本資料夾的內容上傳至儲存庫根目錄。務必包含 `.github/workflows/update-and-publish.yml`，不是只上傳 HTML 或 ZIP。
3. 儲存庫 **Settings → Pages → Build and deployment → Source** 選擇 **GitHub Actions**。
4. 到 **Actions → 更新官網資料並發布 → Run workflow** 執行第一次更新。若上傳時自動執行失敗，先完成第 3 步再重新執行。
5. 等同步及發布成功，開啟部署結果顯示的 Pages 網址。不能在尚未成功前把網址當成可用網站。
6. 用瀏覽器開啟並等待畫面顯示「已完成離線快取」，之後可斷網重新開啟原網址。也可以下載「含目前資料的 HTML」直接離線開啟。

ZIP 解壓縮後若看不到 `.github`，那是隱藏資料夾。macOS Finder 可按 Command+Shift+. 顯示。也可使用 GitHub Desktop 上傳完整資料夾。

## 同步範圍與頻率

編輯 `sync-config.json` 的 destinations 設定搜尋關鍵字；預設為北海道、日本、韓國、越南。每個目的地最多核對 18 個官網候選行程，並收錄已核對行程的可報名出發日。不是全官網資料庫，未找到不表示沒有販售。

`maxPatternsPerDestination` 可設定 1–40，目的地最多 12 個。請求間隔至少 1 秒，避免密集抓取。範圍過大可能超出工作流程 20 分鐘上限。

`.github/workflows/update-and-publish.yml` 的 cron `17 */6 * * *` 表示每 6 小時的第 17 分鐘排程（UTC）。GitHub 可能延遲排程；公開儲存庫連續 60 天無活動可能停用排程，需在 Actions 檢查及重新啟用。

「載入最新已發布版本」只重新取得最近成功發布的快照，不會立即觸發官網抓取。要立刻重新抓取，請到 GitHub Actions 手動 Run workflow。

## 失敗、資料與限制

- 任一官網請求／格式解析失敗時，本次發布停止，保留上一個成功版本，不把舊資料冒充新資料。請查看 Actions 失敗紀錄。
- 官網可能封鎖自動請求或改版，需維護解析程式；本程式不繞過登入、驗證碼或存取限制。
- 官網價格、席位是同步當時的值，送客或報名前請再確認。候補、不開放報名、APP 限定團不納入一般推薦。
- 景點只做文字比對，不保證入內參觀；保留來源的車經等說明。兒童／嬰兒價格、房型與長者適合度另確認。
- 本機手動新增／修改的資料只存在該瀏覽器，不會上傳 GitHub。重載新版頁面時優先載入官網快照；需要保留手動修改請先匯出 JSON，之後重新匯入。
- 瀏覽器可能清除離線快取，私密瀏覽也可能不支援保存。重要資料請下載 HTML 或 JSON 備份。
- Pages 發布的行程與程式可供網站訪客讀取。不要加入客戶個資、內部成本、未公開條件或密碼。
- 第一次同步前不含虛構行程，不提供未查證價格。

## 本機檢查（可選）

使用 Python 3.10+，無需安裝第三方套件：

```
python3 -m unittest discover -s tests
python3 scripts/sync.py
python3 -m http.server 8000 --directory site
```

同步需網路；輸出在 `site/`。GitHub Pages 使用 HTTPS 才能啟用 Service Worker。單檔 HTML 下載則不需要 Service Worker。

## 官方說明

- https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages
- https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule
