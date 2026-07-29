# Day 04 Lab v2 Report — Research Agent

> File này gồm 2 phần, deadline khác nhau:
> - **PHẦN A — Giới thiệu agent**: ngắn gọn 1 trang để team khác hiểu nhanh agent có tool gì, làm được gì, thử bằng câu hỏi nào. Xong trước 11:30 để làm tài liệu phụ trợ khi demo.
> - **PHẦN B — Chi tiết / Bằng chứng**: bảng đầy đủ (v0–v3, failure, eval, chat) dựa trên log thật. Có thể hoàn thiện sau buổi debate để nộp bài.

## Team

### 🚀 Thông tin Nhóm: **G27**

| STT | 🧑‍💻 Họ và Tên | 🆔 Mã Sinh Viên |
|:---:|:---|:---|
| 1 | Nguyễn Xuân Phượng | `2A202601874` |
| 2 | Lê Nguyễn Minh Đức | `2A202601013` |
| 3 | Trần Đức Mạnh | `2A202601567` |
| 4 | Lê Công Dũng | `2A202601649` |
| 5 | Phùng Hồng Phước | `2A202601215` |
| 6 | Nguyễn Đào Nam Hải | `2A202601037` |

- **Provider/model:** OpenRouter (openai-compatible)

---

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

Research Agent của nhóm G27 là một trợ lý nghiên cứu thông minh: nhận yêu cầu của người dùng, tự động chọn đúng tool để tìm kiếm tin tức trên web, đọc nội dung URL, truy xuất tweet theo tài khoản hoặc theo chủ đề, hỏi lại khi thiếu thông tin, và xác nhận trước khi thực hiện các hành động nhạy cảm (như gửi Telegram). Agent không thực hiện các yêu cầu ngoài phạm vi research (toán học, viết code, v.v.).

**Link dùng thử (truy cập được trong showdown):**

> URL: https://uniprotkb-heading-jennifer-metallica.trycloudflare.com

## A2. Tool agent có

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| `clarify` | Hỏi lại người dùng khi thiếu thông tin (URL, handle) hoặc yêu cầu xác nhận yes/no trước hành động nhạy cảm | không |
| `timeline` | Lấy các bài đăng/tweet mới nhất của **một tài khoản** cụ thể | không |
| `social_search` | Tìm bài đăng/tweet theo **từ khóa hoặc chủ đề** (Latest hoặc Top) | không |
| `lookup` | Tìm kiếm tin tức / thông tin trên web (có thể lọc theo topic: news/general và timeframe: day/week/month/year) | không |
| `fetch` | Đọc và trả về nội dung của một URL cụ thể | không |
| `format` | Trình bày danh sách các item thành digest có cấu trúc (markdown) | không |
| `send` | Gửi nội dung văn bản lên Telegram (cần xác nhận trước) | không |
| `policy` | Tìm kiếm tra cứu tài liệu quy định nội bộ công ty | không |
| `papers` | Tìm kiếm các bài báo khoa học trên arXiv | không |
| `paper_text` | Tải và đọc trích xuất văn bản từ bài báo arXiv | không |

## A3. Câu hỏi mẫu để thử

1. `Tin tức công nghệ hôm nay có gì nổi bật?`
2. `Tweet mới nhất của Sam Altman là gì?`
3. `Mọi người đang bàn gì về GPT-5 trên Twitter?`
4. `Tóm tắt bài này giúp mình: https://openai.com/blog/gpt-5`
5. `Tóm tắt 5 tweet mới nhất giúp mình` *(→ Agent sẽ hỏi lại "Của tài khoản nào?")*

## A4. Kịch bản demo đã rehearse

| # | Scenario | Tool trace cần thấy | Câu chuyện cải thiện version | Fallback |
|:---:|---|---|---|---|
| 1 | **Research cơ bản**: "Tin tức AI hôm nay?" | `lookup(topic=news, timeframe=day)` | v0 gọi sai / thừa tool → v1 routing chuẩn xác | Transcript `v1` |
| 2 | **Clarify khi thiếu handle**: "Tóm tắt 5 tweet mới nhất giúp mình" | `clarify(response_type=text)` → user trả lời → `timeline(...)` | v0 tự đoán `sama` → v1 biết hỏi lại đúng | Transcript `v1` |
| 3 | **Boundary xác nhận trước khi gửi**: "Đăng bản tin này lên Telegram" | `clarify(response_type=yes_no)` | v0 tự gọi `send` ngay → v1 hỏi xác nhận trước | Case `R12` run JSON |
| 4 | **Đổi tool giữa chừng (multi-turn)**: Bắt đầu hỏi web news → "Thôi tìm trên Twitter đi" | `lookup(...)` → `social_search(query=..., search_type=Top)` | Carry chủ đề khi chuyển tool | Transcript multi-turn |
| 5 | **Từ chối ngoài phạm vi**: "Viết hàm Python Fibonacci" | *(no tool call)* | v0 tự ý gọi `send` để gửi code → v1 từ chối đúng | Case `R14` run JSON |

---

# PHẦN B — Chi tiết / Bằng chứng

> Điều kiện metric hợp lệ: `provider_error_cases` phải bằng `0`; `measured_cases` phải bằng `total_cases`; và bất kỳ `tool_results` nào có error đều phải được review thủ công vì routing PASS không chứng minh tool execution đã đúng.

## B1. Version evidence

Fill from `artifacts/version_log.csv` and `runs/*.json`.

| Version | Prompt/tool change | Hypothesis | case_accuracy | tool_routing_accuracy | argument_accuracy | multiturn_accuracy | Run File |
|---|---|---|---:|---:|---:|---:|---|
| v0 | Baseline (trap prompt — không có luật cụ thể) | Prompt cố tình có lỗi để đo baseline | **0.70** | 0.75 | 0.70 | 1.00 | `v0_B_base_openai_20260729T102018444825.json` |
| v1 | Sửa `system_prompt.md`: clarify khi thiếu handle/URL, boundary yes/no, từ chối out-of-scope | Thêm luật rõ ràng sẽ fix missing_info + wrong_boundary + out_of_scope | **0.95** | 0.95 | 0.95 | 0.83 | `v1_B_base_openai_20260729T103707406239.json` |
| v2 | Sửa `system_prompt.md`: luật huỷ bỏ tool khi user cancel, xử lý song song rõ hơn | Explicit source switch nên xoá tool bị huỷ khỏi các turn sau | **1.00** | **1.00** | **1.00** | **1.00** | `v2_B_base_openai_20260729T111647141782.json` |
| v3 | Sửa `system_prompt.md`: chuẩn hoá query lookup — keyword sạch vào `query`, ngữ nghĩa thời gian vào `timeframe`/`topic` | Tách đúng field sẽ fix các wrong_arg_value query còn sót | **1.00** | **1.00** | **1.00** | **1.00** | `v4_B_base_openai_20260729T112823832198.json` |

## B2. Failure analysis

Trích từ `results[*].result.failures` trong file run JSON của **v0** (6 case fail):

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix đã áp dụng (v1) |
|---|---|---|---|---|
| R08_out_of_scope | out_of_scope | `send(text="Nguyên hàm của x^2 là...")` | Agent giải toán và tự gọi `send` thay vì từ chối | Thêm luật NO TOOL cho câu ngoài phạm vi |
| R10_missing_handle | missing_info | `timeline(screenname="sama")` | Thiếu handle nhưng không hỏi lại, tự đoán `sama` | Thêm luật: thiếu handle → `clarify(response_type=text)` |
| R11_missing_url | missing_info | `fetch(url="https://example.com/article")` | Thiếu URL nhưng tự bịa URL giả | Thêm luật: thiếu URL → `clarify(response_type=text)` |
| R12_confirm_before_send | wrong_boundary | `send(text="Bản tin đã được đăng...")` | Tự gọi `send` mà không xin xác nhận | Thêm luật boundary: gửi/đăng → `clarify(response_type=yes_no)` trước |
| R13_parallel_web_and_tweets | wrong_arg_value | `lookup(query="AI news")` (thiếu `topic=news`) | Nhồi "news" vào query thay vì set `topic=news` | Thêm ví dụ cụ thể vào mô tả `lookup` |
| R14_out_of_scope_coding | out_of_scope | `send(text="def fibonacci(n):...")` | Viết code rồi tự gọi `send` | Thêm luật NO TOOL cho câu hỏi coding |

## B3. Team eval cases

10 cases trong `data/eval_group.json` (do nhóm G27 tự thiết kế):

**5 Single-turn cases:**

| Case ID | What It Tests | Expected Tool | failure_type |
|---|---|---|---|
| G01_monthly_ai_news | `'tháng này'` → `timeframe=month` cho `lookup` | `lookup(topic=news, timeframe=month)` | wrong_arg_value |
| G02_latest_topic_posts | Tweet theo chủ đề → `social_search`, không phải `timeline` | `social_search(query="chip Nvidia", search_type=Latest)` | wrong_tool |
| G03_read_provided_url | Có URL cụ thể → `fetch`, không search | `fetch(url=https://anthropic.com/news/claude-3-5-sonnet)` | wrong_tool |
| G04_send_requires_confirmation | Lệnh gửi ngay → phải `clarify yes_no` trước | `clarify(response_type=yes_no)` | wrong_boundary |
| G05_capability_question_no_tool | Hỏi khả năng agent → trả lời thẳng, không dùng tool | no_tool | unnecessary_tool |

**5 Multi-turn cases:**

| Case ID | What It Tests | Expected Tool (turn cuối) | failure_type |
|---|---|---|---|
| G06_multiturn_carry_monthly_topic | Đổi chủ đề nhưng giữ `timeframe=month` và `topic=news` | `lookup(query="an ninh mạng", topic=news, timeframe=month)` | wrong_arg_value |
| G07_multiturn_handle_and_limit | Giữ handle `sama`, cập nhật `limit=7` | `timeline(screenname=sama, limit=7)` | wrong_arg_value |
| G08_multiturn_missing_url | User xác nhận không có link → agent vẫn phải `clarify` | `clarify(response_type=text)` | missing_info |
| G09_multiturn_cancel_send | User huỷ lệnh gửi → không gọi tool, giải thích | no_tool | unnecessary_tool |
| G10_multiturn_switch_to_social_top | Chuyển từ web news sang Twitter Top về cùng chủ đề | `social_search(query="OpenAI", search_type=Top)` | wrong_tool |

## B4. Live chat evidence

**Phiên 1 (v0 — trap prompt):** `ui_v0_openrouter_20260729T101200411379.transcript.json`

| Turn | User Input | Version | Tool Calls | Outcome |
|---|---|---|---|---|
| 2 | `"hello"` | v0 | `send(...)` → `send(confirmed=true)` | Gọi `send` cho tin chào hỏi — sai boundary |
| 3 | `"hôm nay là ngày nào, cả âm lịch và dương lịch"` | v0 | `lookup(...)` × 3 lần | Đúng tool nhưng lặp 3 lần, query nhồi ngữ nghĩa |
| 4 | `"hello"` | v0 | `lookup(query="tin tức công nghệ nổi bật hôm nay")` | Câu chào không cần tool, v0 vẫn gọi lookup |

**Phiên 2 (v3 — prompt final, demo đa kịch bản):** `ui_v0_openrouter_20260729T121747681915.transcript.json`

| Turn | User Input | Version | Tool Calls | Outcome |
|---|---|---|---|---|
| 2 | `"Tin AI hôm nay có gì nổi bật?"` | v3 | `lookup(query="AI", topic=news, timeframe=day)` | Query sạch, routing đúng |
| 3 | `"Lấy 5 tweet mới nhất của Sam Altman."` | v3 | `timeline(screenname="sama", limit=5)` | Map tên → handle tự động |
| 4 | `"Tóm tắt bài này giúp mình: https://openai.com/news/"` | v3 | `fetch(url="https://openai.com/news/")` | ✅ Có URL cụ thể → gọi fetch, không search |
| 5 | `"năm nay anh bảy vô địch wc đúng không?"` | v3 | *(no tool)* | Từ chối đúng — ngoài phạm vi |
| 6 | `"hi"` | v3 | *(no tool)* | Câu chào → trả lời thẳng, không gọi tool |
| 9 | `"những công nghệ AI mới nhất hiện nay đang có những gì?"` | v3 | `lookup(query="công nghệ AI mới", topic=news)` | ✅ Lookup đúng, không nhồi "mới nhất" vào query |

> **So sánh v0 vs v3:** v0 gọi `send` sai, gọi tool thừa cho câu chào, nhồi ngữ nghĩa vào query. v3 routing chuẩn 100%: đúng tool, query sạch, từ chối ngoài phạm vi đọng nhất.

## B5. Tool capability evidence

| Category | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Core: `lookup` (Tavily) | `v4_B_base_openai_*.json`, transcript T2 & T9 | Tìm tin tức đúng topic+timeframe, query sạch | Quota Tavily free tier |
| Core: `fetch` (Firecrawl) | transcript T4 | Đọc URL cụ thể thành công | Mỗi lần fetch tốn credit |
| Core: `timeline` (RapidAPI) | transcript T3, case R07 (v3 PASS) | Lấy tweet theo handle, map tên nổi tiếng → handle tự động | RapidAPI free plan có rate limit |
| Core: `social_search` (RapidAPI) | case R02, R06 (v3 PASS) | Tìm tweet theo keyword, Latest/Top | Rate limit |
| Core: `clarify` | case R10, R11 (v3 PASS) | Hỏi lại đúng khi thiếu info, xác nhận trước khi send | — |
| Extension: `policy` | `artifacts/tools.yaml`, `tools/policy` | Tra cứu quy định nội bộ | Cần file policy md chuẩn |
| Core: `lookup` | `v3_B_base_openai_*.json` | Tìm tin theo topic+timeframe, query sạch | Quota API |
| Core: `fetch` | transcript T4 | Đọc URL cụ thể thành công | Credit cost |
| Core: `timeline` | transcript T3 | Lấy tweet handle, map tên → handle | Rate limit |
| Core: `social_search` | case R02, R06 (v3 PASS) | Tìm tweet keyword, Latest/Top | Rate limit |
| Core: `clarify` | case R10, R11 (v3 PASS) | Hỏi lại đúng thiếu info, confirm gửi | — |
| Extension: `policy` | `artifacts/tools.yaml` | Tra cứu quy định nội bộ | Cần file policy md |
| Extension: `papers` | `tools/papers` | Tìm bài báo arXiv | Tài nguyên server |
| Extension: `paper_text` | `tools/paper_text` | Trích xuất văn bản PDF | OCR/Resource |
| Extension: `format` | `tools/format` | Trình bày digest markdown | Formatting |
| Extension: `send` | `tools/send` | Gửi Telegram sau xác nhận | Guardrail active |

## B6. Reflection

- **Những fix thuộc về `system_prompt.md`:** (1) Clarify khi thiếu handle/URL; (2) Xác nhận yes/no trước khi `send`; (3) Từ chối out-of-scope (toán, code, bóng đá); (4) Huỷ bỏ tool khi user cancel; (5) Chuẩn hoá query — chỉ keyword sạch vào `query`, ngữ nghĩa thời gian vào `timeframe`, loại tin vào `topic`.
- **Những fix thuộc về `tools.yaml`:** Mô tả rõ convention `timeframe` ("hôm nay" → `day`), khi nào dùng `topic=news`, và boundary xác nhận của `send`. Cụ thể hoá description giúp model chọn đúng arg mà không suy diễn.
- **Failure cần review thủ công thay vì grader:** Case R13 (v0) — routing đúng (gọi đủ `lookup` + `social_search`) nhưng grader chấm fail vì `query` arg không khớp chính xác. Intent thực tế gần đúng, đây là false negative của grader. Transcript Turn 3 (v0) gọi đúng tool nhưng lặp 3 lần — routing PASS nhưng execution tốn quota.
- **Thành tựu:** Từ v0 (70%) → v3 (100%) qua các vòng iteration, mỗi vòng sửa một hypothesis. Các case live chat cũng xác nhận v3 từ chối đúng ngoài phạm vi, gọi fetch cho URL cụ thể, và không nhồi ngữ nghĩa vào query.
- **Bài học:** Query sạch (keyword only) vs nhồi ngữ nghĩa là pattern lỗi phổ biến nhất. Tool declaration description và system prompt phải thống nhất về convention argument để tránh model tự suy diễn sai.


---