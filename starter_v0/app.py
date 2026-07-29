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
    ARTIFACTS_DIR
)
from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import build_artifact_version, artifact_version_dict

# Khởi tạo môi trường (nạp .env)
ROOT = Path(__file__).parent
TRANSCRIPTS_DIR = ROOT / "transcripts"
load_lab_env(ROOT)

# st.set_page_config(page_title="Research Agent UI", page_icon="🤖", layout="wide")

# --- 1. GIAO DIỆN SIDEBAR (CẤU HÌNH) ---
with st.sidebar:
    st.header("⚙️ Cấu hình Model")
    provider_name = st.selectbox("Provider", ["openrouter", "openai", "anthropic", "gemini"])
    model_name = st.text_input("Model Override (bỏ trống để dùng mặc định)", value="")
    version_label = st.text_input("Version Label", value="v0")
    max_tool_rounds = st.number_input("Max Tool Rounds", min_value=1, max_value=10, value=4)
    history_window = st.number_input("History Window (số cặp User/Agent)", min_value=1, max_value=20, value=5)
    
    if st.button("🗑️ Reset Chat & Tạo Session Mới"):
        st.session_state.clear()
        st.rerun()

    st.markdown("---")
    st.markdown("**Hướng dẫn:**\n- Nhập `/exit` hoặc `/quit` để kết thúc (hoặc bấm Reset).\n- Đổ Model cần Reset chat lại trước.\n- UI hiển thị chi tiết các lần gọi Tool trong từng Expanders 🔧.")

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
        "model": model_name or None,
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
if user_text := st.chat_input("Nhập câu hỏi hoặc yêu cầu của bạn..."):
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
        with st.spinner("Agent đang suy nghĩ và chạy công cụ..."):
            try:
                # Chạy nguyên bản vòng lặp logic (giống hệt chat.py)
                result = run_model_tool_loop(
                    provider=provider,
                    messages=messages,
                    tools=st.session_state.openai_tools,
                    model=selected_model,
                    max_tool_rounds=max_tool_rounds,
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