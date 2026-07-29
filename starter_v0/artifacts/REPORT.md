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
| v0 | Baseline (trap prompt) | Prompt cố tình có lỗi để đo baseline | **0.70** | 0.75 | 0.70 | 1.00 | `v0_B_base_openai_20260729T102018444825.json` |
| v1 | Sửa system_prompt.md: thêm luật clarify, boundary, out-of-scope | Thêm luật rõ ràng sẽ fix các lỗi missing_info + wrong_boundary + out_of_scope | **0.95** | 0.95 | 0.95 | 0.83 | `v1_B_base_openai_20260729T103707406239.json` |
| v2 | *(Chờ Đội trưởng chạy và cung cấp kết quả)* | — | — | — | — | — | — |
| v3 | *(Chờ Đội trưởng chạy và cung cấp kết quả)* | — | — | — | — | — | — |

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

> *(Sẽ cập nhật sau khi có transcript từ UI — thư mục `transcripts/`)*

| Scenario/Turn | Version | Tool Calls + Args | Transcript/Run | Outcome |
|---|---|---|---|---|
| *(chờ UI chạy)* | — | — | — | — |

## B5. Tool capability evidence

| Category | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Core: `lookup` (Tavily) | `v1_B_base_openai_*.json` | Tìm tin tức theo topic+timeframe | Quota Tavily free tier |
| Core: `fetch` (Firecrawl) | smoke test PASS | Đọc nội dung URL thành công | Mỗi lần fetch tốn credit |
| Core: `timeline`/`social_search` (RapidAPI) | smoke test PASS | Lấy tweet theo handle và theo keyword | RapidAPI free plan có rate limit |
| Core: `clarify` | `R10`, `R11`, `R12` (v1) | Hỏi lại đúng khi thiếu info, xác nhận trước khi send | — |
| Must-have: Tool mới (T.viên 3) | *(chờ code)* | *(chờ cập nhật)* | — |

## B6. Reflection

- **Những fix thuộc về `system_prompt.md`:** Luật clarify khi thiếu handle/URL, luật xác nhận yes/no trước khi `send`, luật từ chối out-of-scope (toán, code). Những luật này chỉ model mới đọc và thực thi được — không phải schema tool.
- **Những fix thuộc về `tools.yaml`:** Mô tả rõ khi nào dùng `topic=news`, convention `timeframe` ("hôm nay" → `day`), và boundary xác nhận của `send`.
- **Failure cần review thủ công thay vì grader:** Case R13 — routing đúng (gọi cả `lookup` và `social_search`) nhưng `query` arg không khớp chính xác ("AI news" vs "AI"). Grader chấm fail nhưng intent thực tế gần đúng.
- **Cải thiện tiếp theo:** Thêm tool mới để mở rộng khả năng nghiên cứu; cân nhắc viết eval case cho tool mới; tối ưu thêm `multiturn_accuracy` (hiện v1 = 0.83).


---

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

> 1–2 câu mô tả agent dùng để làm gì.

Ví dụ: "Research agent: tìm tin theo từ khóa / theo tài khoản, đọc URL và tổng hợp thành digest."

**Link dùng thử (truy cập được trong showdown):**

> Dán public URL nếu người khác cần mở từ máy riêng; localhost cũng được nếu demo trực tiếp trên máy trình chiếu. Streamlit được khuyến nghị, nhưng nhóm có thể dùng bất kỳ framework nào.
>
> URL:

## A2. Tool agent có

> Liệt kê các tool agent đang dùng. Mỗi tool 1 dòng: tên + làm được gì.

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | hỏi lại người dùng khi thiếu thông tin | không |
|  |  |  |
|  |  |  |

## A3. Câu hỏi mẫu để thử

> 3–5 câu hỏi/yêu cầu mẫu để team khác tự thử agent ngay.

1.
2.
3.

## A4. Kịch bản demo đã rehearse

> Chuẩn bị 3–5 scenario. Mỗi scenario cần cho thấy tool đã làm gì và một thay đổi cụ thể giữa các version.

| Scenario | Tool trace cần thấy | Câu chuyện cải thiện version | Fallback run/transcript |
|---|---|---|---|
|  |  |  |  |

---

# PHẦN B — Chi tiết / Bằng chứng

> Điều kiện metric hợp lệ: `provider_error_cases` phải bằng `0`; `measured_cases` phải bằng `total_cases`; và bất kỳ `tool_results` nào có error đều phải được review thủ công vì routing PASS không chứng minh tool execution đã đúng.

## B1. Version evidence

Fill from `artifacts/version_log.csv` and `runs/*.json`.

| Version | Prompt/tool change | Hypothesis | Metric name | Before | After | Run File |
|---|---|---|---|---:|---:|---|
| v0 | baseline |  |  |  |  |  |
| v1 |  |  |  |  |  |  |
| v2 |  |  |  |  |  |  |
| v3 |  |  |  |  |  |  |

## B2. Failure analysis

Use actual failures from `results[*].result.failures`.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
|  |  |  |  |  |

## B3. Team eval cases

List the 10 cases added to `data/eval_group.json`:

- 5 single-turn
- 5 multi-turn

This section is for the mandatory team-authored eval set. Optional built-ins do
not belong here.

File template để trống có chủ đích; nhóm phải tự thiết kế đủ 10 case.

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
|  |  |  |  |

## B4. Live chat evidence

Use `transcripts/*.transcript.json`.

| Scenario/Turn | Version | Tool Calls + Args | Transcript/Run | Outcome |
|---|---|---|---|---|
|  |  |  |  |  |

## B5. Tool capability evidence

Phân loại rõ tool mới bắt buộc, optional built-in và tool đủ điều kiện bonus. Chỉ ghi Telegram/PDF nếu nhóm thực sự dùng; base report không cần chúng.

UI is core deliverable, not bonus. Do not list it here.

| Category | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Must-have: tool mới đầu tiên |  |  |  |
| Optional built-in |  |  |  |
| Bonus: tool mới thứ 4 trở đi |  |  |  |

## B6. Reflection

- Which fixes belonged in `system_prompt.md`?
- Which fixes belonged in `tools.yaml`?
- Which failure needed manual review instead of automatic grading?
- What would you improve next?
