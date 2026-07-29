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

> URL: *(sẽ cập nhật link Cloudflare Tunnel từ Thành viên 4 trước demo)*

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
| *(Tool mới — T.viên 3)* | *(Sẽ cập nhật sau khi có code)* | **Có** |

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
| v1 | Sửa `system_prompt.md`: thêm luật clarify khi thiếu handle/URL, boundary yes/no, từ chối out-of-scope | Thêm luật rõ ràng sẽ fix lỗi missing_info + wrong_boundary + out_of_scope | **0.95** | 0.95 | 0.95 | 0.83 | `v1_B_base_openai_20260729T103707406239.json` |
| v2 | Sửa `system_prompt.md`: thêm luật huỷ bỏ tool khi user cancel, xử lý song song rõ hơn | Explicit source switch nên xoá tool đã bị huỷ khỏi các turn sau | **1.00** ✅ | **1.00** | **1.00** | **1.00** | `v2_B_base_openai_20260729T111647141782.json` |
| v3 | *(Sẽ chạy sau demo — chờ feedback để xác định hypothesis)* | — | — | — | — | — | — |

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
| 2 | `"hello"` | v0 | `send(text="Xin chào!...")` → `send(confirmed=true)` | ❌ Gọi `send` cho tin chào hỏi — sai boundary |
| 3 | `"hôm nay là ngày nào, cả âm lịch và dương lịch"` | v0 | `lookup(...)` × 3 lần | ⚠️ Đúng tool nhưng lặp 3 lần, query nhồi cả "âm lịch dương lịch" |
| 4 | `"hello"` | v0 | `lookup(query="tin tức công nghệ nổi bật hôm nay")` | ❌ Câu chào không cần tool, v0 vẫn gọi lookup |

**Phiên 2 (v2 — sau khi tối ưu):** `ui_v0_openrouter_20260729T113233038379.transcript.json`

| Turn | User Input | Version | Tool Calls | Outcome |
|---|---|---|---|---|
| 1 | `"Lấy 5 tweet mới nhất của Sam Altman."` | v2 | `timeline(screenname="sama", limit=5)` | ✅ Routing đúng, map tên → handle tự động |
| 2 | `"Tóm tắt 5 tweet mới nhất giúp mình."` | v2 | `timeline(screenname="sama", limit=5)` | ✅ Giữ context từ turn 1, không hỏi lại handle |

**Phiên 3 (v2 — research):** `ui_v0_openrouter_20260729T113432760672.transcript.json`

| Turn | User Input | Version | Tool Calls | Outcome |
|---|---|---|---|---|
| 1 | `"Tin AI hôm nay có gì nổi bật?"` | v2 | `lookup(query="AI", topic="news", timeframe="day")` | ✅ Query sạch — không nhồi "hôm nay" vào query |

> **So sánh v0 vs v2:** v0 gọi sai tool (send cho chào hỏi), lặp tool, nhồi từ thời gian vào query. v2 routing chuẩn 100%, query sạch, giữ context đa lượt.

## B5. Tool capability evidence

| Category | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Core: `lookup` (Tavily) | `v1_B_base_openai_*.json` | Tìm tin tức theo topic+timeframe | Quota Tavily free tier |
| Core: `fetch` (Firecrawl) | smoke test PASS | Đọc nội dung URL thành công | Mỗi lần fetch tốn credit |
| Core: `timeline`/`social_search` (RapidAPI) | smoke test PASS | Lấy tweet theo handle và theo keyword | RapidAPI free plan có rate limit |
| Core: `clarify` | `R10`, `R11`, `R12` (v1) | Hỏi lại đúng khi thiếu info, xác nhận trước khi send | — |
| Must-have: Tool mới (T.viên 3) | *(chờ code)* | *(chờ cập nhật)* | — |

## B6. Reflection

- **Những fix thuộc về `system_prompt.md`:** (1) Luật clarify khi thiếu handle/URL; (2) Luật xác nhận yes/no trước khi `send`; (3) Luật từ chối out-of-scope (toán, code); (4) Luật huỷ bỏ tool khi user cancel. Những luật này chỉ model mới đọc và thực thi được — không phải schema tool.
- **Những fix thuộc về `tools.yaml`:** Mô tả rõ khi nào dùng `topic=news`, convention `timeframe` ("hôm nay" → `day`), và boundary xác nhận của `send`. Cụ thể hoá description giúp model chọn đúng arg mà không cần nhồi thêm ngữ nghĩa vào `query`.
- **Failure cần review thủ công thay vì grader:** Case R13 (v0) — routing đúng (gọi cả `lookup` và `social_search`) nhưng `query` arg không khớp chính xác ("AI news" vs "AI"). Grader chấm fail nhưng intent thực tế gần đúng. Transcript Turn 3 (hỏi ngày âm/dương lịch) gọi đúng tool nhưng lặp 3 lần — routing PASS nhưng execution kém hiệu quả.
- **Thành tựu nổi bật đến v2:** Từ v0 (70%) → v2 (100%) chỉ qua 2 vòng sửa `system_prompt.md`, mỗi vòng fix một nhóm lỗi cụ thể. Tất cả 20 case PASS ở v2 với `provider_error_cases=0` và `measured_cases=20`.
- **Dự kiến cho v3 (sau demo):** Áp dụng feedback từ demo để xác định hypothesis tiếp theo — có thể là chuẩn hoá query, tối ưu multi-turn context, hoặc tích hợp tool mới.


---