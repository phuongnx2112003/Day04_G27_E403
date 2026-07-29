import streamlit as st
import json
from pathlib import Path
from datetime import datetime

# Import các hàm tiện ích từ file chat.py để đảm bảo đồng nhất logic
from chat import (
    run_model_tool_loop,
    trim_history,
    write_transcript,
    now_iso,
    safe_slug,
    ARTIFACTS_DIR,
)
from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import build_artifact_version, artifact_version_dict

# Khởi tạo môi trường (nạp .env)
ROOT = Path(__file__).parent
TRANSCRIPTS_DIR = ROOT / "transcripts"
load_lab_env(ROOT)

st.set_page_config(page_title="Research Agent UI", page_icon="🤖", layout="wide")

# --- 1. GIAO DIỆN SIDEBAR (CẤU HÌNH) ---
with st.sidebar:
    st.header("⚙️ Cấu hình Model")
    provider_name = st.selectbox("Provider", ["openrouter", "openai", "anthropic", "gemini"])
    model_name = st.text_input("Model (tuỳ chọn)", value="")
    version_label = st.text_input("Version Label", value="v0")
    max_tool_rounds = st.number_input("Max Tool Rounds", min_value=1, max_value=10, value=4)
    history_window = st.number_input("History Window (số cặp User/Agent)", min_value=1, max_value=20, value=5)
    
    if st.button("🗑️ Reset Chat & Tạo Session Mới"):
        st.session_state.clear()
        st.rerun()

    st.markdown("---")
    st.markdown("**Hướng dẫn:**\n- Nhập `/exit` hoặc `/quit` để kết thúc (hoặc bấm Reset).\n- UI hiển thị chi tiết các lần gọi Tool trong từng Expanders 🔧.")

# --- 2. KHỞI TẠO SESSION STATE ---
if "history" not in st.session_state:
    st.session_state.history = []
    st.session_state.turn_index = 0

    # Nạp System Prompt và Tools như chat.py
    system_prompt_path = ARTIFACTS_DIR / "system_prompt.md"
    tools_path = ARTIFACTS_DIR / "tools.yaml"
    
    st.session_state.system_prompt = system_prompt_path.read_text(encoding="utf-8") if system_prompt_path.exists() else "You are a helpful assistant."
    tool_declarations = load_tool_declarations(tools_path) if tools_path.exists() else {}
    st.session_state.openai_tools = to_openai_tools(tool_declarations)
    
    artifact_version = build_artifact_version(version_label, system_prompt_path, tools_path)
    
    # Tạo Transcript cho phiên UI
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    transcript_id = "_".join([safe_slug(version_label), safe_slug(provider_name), timestamp])
    st.session_state.transcript_path = TRANSCRIPTS_DIR / f"ui_{transcript_id}.transcript.json"
    
    st.session_state.transcript = {
        "transcript_id": transcript_id,
        **artifact_version_dict(artifact_version),
        "provider": provider_name,
        "system_prompt": str(system_prompt_path),
        "tools": str(tools_path),
        "history_window": history_window,
        "max_tool_rounds": max_tool_rounds,
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "turns": [],
    }

st.title("🤖 Trợ lý AI (Research Agent)")
# st.caption(f"Artifact Version: `{st.session_state.transcript['artifact_version']}` | Ghi log tại: `{st.session_state.transcript_path.name}`")

with st.expander("🔗 Lịch sử thay đổi theo phiên bản", expanded=False):
    st.info("Cách đọc: **Input** là câu người dùng nói; **Output** là tool/arguments agent thực sự chọn. Mỗi tab thể hiện một giả thuyết được kiểm chứng bằng eval, không chỉ là thay đổi theo cảm giác.")
    v0_tab, v1_tab, v2_tab = st.tabs(["v0 · Baseline", "v1", "v2"])

    with v0_tab:
        st.subheader("v0 — Bản ban đầu để tìm lỗi")
        col1, col2 = st.columns(2)
        col1.metric("Kết quả", "14/20 PASS", "70% case accuracy")
        col2.metric("Điều cần học", "6 lỗi", "routing và safety")
        st.markdown("**Input demo:** `Đăng bản tin này lên Telegram giúp mình`.")
        st.markdown("**Output thực tế:** agent gọi ngay `send(...)` thay vì hỏi người dùng xác nhận.")
        st.markdown("**Đánh giá:** agent hiểu tool nhưng chưa có ranh giới an toàn; cũng hay đoán handle/URL khi thiếu thông tin hoặc gọi tool cho câu ngoài phạm vi.")
        st.caption("Cách nói khi thuyết trình: “V0 là baseline. Chúng em cố tình chạy thật để xác định agent sai ở đâu trước khi tối ưu.”")

    with v1_tab:
        st.subheader("v1 — Sửa routing và safety")
        col1, col2 = st.columns(2)
        col1.metric("Kết quả", "19/20 PASS", "+25 điểm so với v0")
        col2.metric("Case còn lỗi", "M06", "source switch")
        st.markdown("**Input demo:** `Tóm tắt 5 tweet mới nhất giúp mình`.")
        st.markdown("**Output sau thay đổi:** agent gọi `clarify(response_type='text')` để hỏi tài khoản, thay vì tự đoán người cần tìm.")
        st.markdown("**Đã làm gì:** viết rõ trong prompt khi dùng từng tool, map tên sang handle, hỏi lại khi thiếu URL/handle, xác nhận yes/no trước `send`, và không gọi tool cho câu meta/out-of-scope.")
        st.markdown("**Đánh giá:** các lỗi lớn của v0 được xử lý; chỉ còn M06, nơi agent chưa bỏ hoàn toàn nguồn Twitter cũ sau khi user đổi sang web.")
        st.caption("Cách nói: “Chỉ bằng cách làm rõ instruction, accuracy tăng từ 70% lên 95%.”")

    with v2_tab:
        st.subheader("v2 — Thử xử lý việc hủy một nguồn")
        col1, col2 = st.columns(2)
        col1.metric("Kết quả", "19/20 PASS", "không tăng")
        col2.metric("M06", "Vẫn fail", "gọi dư social_search")
        st.markdown("**Input demo:** `Mọi người nói gì về OpenAI trên Twitter?` → `Bỏ Twitter, chuyển sang tìm trên web tin tức đi` → `Giữ chủ đề OpenAI`.")
        st.markdown("**Output thực tế:** agent gọi cả `lookup(OpenAI)` **và** `social_search(OpenAI)`; tool Twitter là tool dư.")
        st.markdown("**Đã làm gì:** thêm rule rằng nguồn bị hủy phải bị loại khỏi context các lượt sau.")
        st.markdown("**Đánh giá:** hypothesis chưa đúng. Rule mới vẫn yếu hơn rule gọi nhiều tool, nên metric giữ nguyên 95%. Đây là evidence cho thấy thay đổi prompt không phải lúc nào cũng cải thiện.")
        st.caption("Cách nói: “V2 không tăng điểm, nhưng log cho chúng em biết chính xác hai rule đang mâu thuẫn.”")

DEMO_PROMPTS = [
    ("📰 Tin AI hôm nay", "Tin AI hôm nay có gì nổi bật?"),
    ("👤 Tweet của Sam Altman", "Lấy 5 tweet mới nhất của Sam Altman."),
    ("🌐 Web + mạng xã hội", "Tìm trên web tin AI hôm nay và tìm thêm tweet về AI."),
    ("🔗 Đọc một URL", "Tóm tắt bài này giúp mình: https://openai.com/news/"),
    ("❓ Demo hỏi lại", "Tóm tắt 5 tweet mới nhất giúp mình."),
]

selected_demo_prompt = None
with st.expander("💡 Câu hỏi gợi ý để demo", expanded=True):
    st.caption("Các kịch bản này lần lượt minh hoạ lookup, timeline, gọi nhiều tool, fetch URL và clarify.")
    for index, (label, prompt) in enumerate(DEMO_PROMPTS):
        if st.button(label, key=f"demo_prompt_{index}", use_container_width=True):
            selected_demo_prompt = prompt

# --- 3. HIỂN THỊ LỊCH SỬ CHAT VÀ TOOL TRACES ---
for msg in st.session_state.history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        
        # Render lại các công cụ mô hình đã gọi ở các turn trước
        if "rounds" in msg and msg["rounds"]:
            for r_idx, round_data in enumerate(msg["rounds"], 1):
                tool_results = round_data.get("tool_results", [])
                if tool_results:
                    for tool_res in tool_results:
                        with st.expander(f"🔧 Tool: `{tool_res.get('tool')}` (Round {r_idx})"):
                            st.write("**Args (Đầu vào):**")
                            st.json(tool_res.get("args", {}))
                            st.write("**Result (Kết quả):**")
                            st.json(tool_res.get("result", {}))

# --- 4. XỬ LÝ KHI NGƯỜI DÙNG NHẬP TIN NHẮN ---
typed_prompt = st.chat_input("Nhập câu hỏi hoặc yêu cầu của bạn...")
user_text = selected_demo_prompt or typed_prompt
if user_text:
    if user_text.strip() in {"/exit", "/quit"}:
        st.warning("Chat kết thúc. Hãy bấm 'Reset Chat' ở sidebar để bắt đầu lại.")
        st.stop()

    # Hiển thị tin nhắn người dùng
    with st.chat_message("user"):
        st.markdown(user_text)

    # Thêm vào context nội bộ
    st.session_state.turn_index += 1
    
    # Tạo Provider instance
    provider = make_provider(provider_name)
    selected_model = model_name if model_name else getattr(provider, "default_model", None)

    # Dựng mảng messages thuần tuý cho Model
    pure_history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.history]
    messages = [
        {"role": "system", "content": st.session_state.system_prompt},
        *trim_history(pure_history, history_window),
        {"role": "user", "content": user_text},
    ]

    turn_record = {
        "turn_index": st.session_state.turn_index,
        "started_at": now_iso(),
        "user": user_text,
        "status": "started",
        "assistant_text": None,
        "rounds": [],
        "tool_events": [],
    }

    # Hiển thị Assistant xử lý
    with st.chat_message("assistant"):
        live_status = st.status("Agent đang phân tích yêu cầu...", expanded=True)
        live_trace = st.empty()
        live_events = []

        def render_live_trace() -> None:
            is_complete = any(event["type"] == "finished" for event in live_events)
            with live_trace.container():
                for event in live_events:
                    if event["type"] == "tool_calls":
                        calls = event["tool_calls"]
                        if calls:
                            st.write(f"**Round {event['round']}:** chọn {len(calls)} tool")
                        else:
                            st.write(f"**Round {event['round']}:** không cần tool")
                    elif event["type"] == "tool_started":
                        st.info(f"Đang gọi `{event['tool']}` với arguments bên dưới.")
                        st.json(event["args"])
                    elif event["type"] == "tool_result":
                        tool_event = event["event"]
                        with st.expander(
                            f"✅ Kết quả `{tool_event['tool']}` (Round {event['round']})",
                            expanded=not is_complete,
                        ):
                            st.write("**Args:**")
                            st.json(tool_event.get("args", {}))
                            st.write("**Result:**")
                            st.json(tool_event.get("result", {}))

        def on_agent_event(event: dict) -> None:
            live_events.append(event)
            if event["type"] == "tool_calls":
                count = len(event["tool_calls"])
                live_status.update(label=f"Round {event['round']}: model chọn {count} tool...", state="running")
            elif event["type"] == "tool_started":
                live_status.update(label=f"Round {event['round']}: đang chạy {event['tool']}...", state="running")
            elif event["type"] == "tool_result":
                live_status.update(label=f"Round {event['round']}: {event['event']['tool']} đã trả kết quả", state="running")
            elif event["type"] == "finished":
                live_status.update(label="Agent đã hoàn tất", state="complete")
            render_live_trace()

        with st.spinner("Agent đang suy nghĩ và chạy công cụ..."):
            try:
                # Chạy nguyên bản vòng lặp logic (giống hệt chat.py)
                result = run_model_tool_loop(
                    provider=provider,
                    messages=messages,
                    tools=st.session_state.openai_tools,
                    model=selected_model,
                    max_tool_rounds=max_tool_rounds,
                    on_event=on_agent_event,
                )
                
                turn_record.update(result)
                assistant_text = result.get("assistant_text", "")
                rounds = result.get("rounds", [])

                # Render ngay lập tức Tool Traces cho vòng chat hiện tại
                if rounds:
                    for r_idx, round_data in enumerate(rounds, 1):
                        tool_results = round_data.get("tool_results", [])
                        for tool_res in tool_results:
                            with st.expander(f"🔧 Tool: `{tool_res.get('tool')}` (Round {r_idx})"):
                                st.write("**Args (Đầu vào):**")
                                st.json(tool_res.get("args", {}))
                                st.write("**Result (Kết quả):**")
                                st.json(tool_res.get("result", {}))

                # Hiển thị đáp án cuối cùng
                if assistant_text:
                    st.markdown(assistant_text)
                else:
                    st.markdown("*(Không có phản hồi dạng văn bản)*")

                # Cập nhật lịch sử
                st.session_state.history.append({"role": "user", "content": user_text})
                st.session_state.history.append({
                    "role": "assistant",
                    "content": assistant_text,
                    "rounds": rounds # Lưu kèm tool info để giữ UI nguyên trạng khi rerender
                })

            except Exception as exc:
                error_msg = f"{type(exc).__name__}: {str(exc)}"
                live_status.update(label="Agent gặp lỗi", state="error")
                st.error(f"Lỗi: {error_msg}")
                turn_record.update({
                    "status": "provider_error",
                    "error": error_msg,
                })
                st.session_state.history.append({"role": "user", "content": user_text})
                st.session_state.history.append({
                    "role": "assistant",
                    "content": f"⚠️ **Lỗi hệ thống:** {error_msg}",
                    "rounds": []
                })

    # Cập nhật & Ghi Transcript
    turn_record["ended_at"] = now_iso()
    st.session_state.transcript["turns"].append(turn_record)
    write_transcript(st.session_state.transcript_path, st.session_state.transcript)
