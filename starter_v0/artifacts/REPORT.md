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
| v3 | Sửa `system_prompt.md` + `tools.yaml`: resolve conflict cancellation vs parallel routing | Final active sources quyết định tool set — không bị ảnh hưởng bởi turn đã huỷ | *(chờ run file từ Đội trưởng)* | — | — | — | — |

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

Trích từ `transcripts/ui_v0_openrouter_20260729T101200411379.transcript.json` — phiên live chat thực tế qua UI:

| Turn | User Input | Version | Tool Calls + Args | Outcome |
|---|---|---|---|---|
| 2 | `"hello"` | v0 | `send(text="Xin chào!...")` → `send(confirmed=true, ...)` | ❌ v0 tự gọi `send` cho tin chào hỏi thông thường — sai boundary |
| 3 | `"hôm nay là ngày nào, cả âm lịch và dương lịch"` | v0 | `lookup(query="hôm nay ngày bao nhiêu âm lịch dương lịch 2024", timeframe=day)` × 3 lần | ⚠️ Gọi đúng tool nhưng lặp 3 lần lookup, query không chuẩn |
| 4 | `"hello\"` | v0 | `lookup(query="tin tức công nghệ nổi bật hôm nay", timeframe=day)` | ❌ Câu chào → không cần tool, nhưng v0 vẫn gọi lookup |

> **Nhận xét:** Transcript v0 minh chứng rõ vấn đề của trap prompt: agent gọi `send` không cần thiết, gọi tool thừa cho câu meta. Đây là lý do phải tối ưu lên v1→v2. Bổ sung thêm transcript v2/v3 sau khi chạy live chat với prompt mới.

## B5. Tool capability evidence

| Category | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Core: `lookup` (Tavily) | `v1_B_base_openai_*.json` | Tìm tin tức theo topic+timeframe | Quota Tavily free tier |
| Core: `fetch` (Firecrawl) | smoke test PASS | Đọc nội dung URL thành công | Mỗi lần fetch tốn credit |
| Core: `timeline`/`social_search` (RapidAPI) | smoke test PASS | Lấy tweet theo handle và theo keyword | RapidAPI free plan có rate limit |
| Core: `clarify` | `R10`, `R11`, `R12` (v1) | Hỏi lại đúng khi thiếu info, xác nhận trước khi send | — |
| Must-have: Tool mới (T.viên 3) | *(chờ code)* | *(chờ cập nhật)* | — |

## B6. Reflection

- **Những fix thuộc về `system_prompt.md`:** Luật clarify khi thiếu handle/URL, luật xác nhận yes/no trước khi `send`, luật từ chối out-of-scope (toán, code), luật huỷ bỏ tool khi user cancel. Những luật này chỉ model mới đọc và thực thi được — không phải schema tool.
- **Những fix thuộc về `tools.yaml`:** Mô tả rõ khi nào dùng `topic=news`, convention `timeframe` ("hôm nay" → `day`), và boundary xác nhận của `send`. Việc làm rõ description trong tools.yaml giúp model chọn đúng arg mà không cần nhồi thêm vào query.
- **Failure cần review thủ công thay vì grader:** Case R13 (v0) — routing đúng (gọi cả `lookup` và `social_search`) nhưng `query` arg không khớp chính xác ("AI news" vs "AI"). Grader chấm fail nhưng intent thực tế gần đúng. Tương tự, transcript Turn 3 (hỏi ngày âm/dương lịch) gọi đúng tool nhưng lặp 3 lần — routing PASS, execution cần cải thiện.
- **Thành tựu nổi bật:** Từ v0 (70%) → v2 (100%) chỉ qua 2 vòng sửa `system_prompt.md`. Tất cả 20 case đều PASS ở v2 với `provider_error_cases=0` và `measured_cases=20`.
- **Cải thiện tiếp theo:** Bổ sung tool mới để mở rộng phạm vi nghiên cứu; viết thêm eval case cho tool mới; chạy group eval sau khi tích hợp tool mới vào v3.


---