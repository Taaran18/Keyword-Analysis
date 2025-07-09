import os
import streamlit as st
import pandas as pd
from utils import plot_intent_distribution, export_data_to_excel
from users import login, logout
from main import process_keywords

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
st.set_page_config(page_title="🔍 Keyword Intent Grouper", layout="wide")

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
    st.session_state["username"] = ""

if not st.session_state["authenticated"]:
    login()
    st.stop()
else:
    logout()

st.markdown(
    "<h1 style='text-align: center;'>💡 Keyword Intent Grouping App</h1>",
    unsafe_allow_html=True,
)
st.markdown("## 📤 Upload Your Keyword File")

uploaded_file = st.file_uploader(
    "Upload an Excel file with a 'Keyword' or 'Keywords' column", type=["xlsx"]
)
if uploaded_file:
    st.session_state["original_df"] = pd.read_excel(uploaded_file)
    st.session_state["original_count"] = len(st.session_state["original_df"])
    st.success(f"✅ File loaded: {st.session_state['original_count']} rows total")
    st.dataframe(st.session_state["original_df"].head(10))

st.markdown("## 🧠 Define Sentiment Meaning")
st.session_state["positive_intent"] = st.text_input(
    "Describe what a Positive Intent means",
    value="Users seeking professional help or services",
)
st.session_state["negative_intent"] = st.text_input(
    "Describe what a Negative Intent means",
    value="Users expressing problems, issues, or confusion",
)

if "original_df" in st.session_state:
    st.markdown("## 🧹 Filter Settings")
    user_input = st.text_input(
        "Enter unwanted words to filter (comma-separated)", value="free, help, download"
    )
    min_k = st.number_input("📉 Minimum keywords per group", min_value=1, value=5)
    max_k = st.number_input(
        "📈 Maximum keywords per group", min_value=min_k + 1, value=20
    )

    if st.button("🚀 Clean & Group"):
        with st.spinner("Filtering and grouping..."):
            (
                df_labeled,
                df_cleaned,
                df_removed_questions,
                df_removed_patterns,
                df_misc,
            ) = process_keywords(
                uploaded_file,
                user_input,
                min_k,
                max_k,
                st.session_state["positive_intent"],
                st.session_state["negative_intent"],
            )

            if df_labeled is None:
                st.error("❌ Failed to process file.")
            else:
                st.session_state["final_df"] = df_labeled
                st.session_state["final_clean_df"] = df_cleaned
                st.session_state["removed_questions"] = df_removed_questions
                st.session_state["removed_patterns"] = df_removed_patterns
                st.session_state["misc_keywords"] = df_misc
                st.session_state["max_keywords_per_group"] = max_k

                st.success("🎯 Grouping complete!")
                st.dataframe(df_labeled.head())
                st.markdown("### 📈 Intent Distribution")
                plot_intent_distribution(df_labeled)

                if not df_misc.empty:
                    st.warning(f"⚠️ {len(df_misc)} keywords moved to Miscellaneous.")
                    st.dataframe(df_misc.head())

if "final_df" in st.session_state:
    st.markdown("## 💾 Download All Processed Data (Excel)")
    dfs_to_export = {
        "Final_Clustered_Keywords": st.session_state["final_df"],
        "Removed_Questions": st.session_state.get("removed_questions", pd.DataFrame()),
        "Removed_Patterns": st.session_state.get("removed_patterns", pd.DataFrame()),
        "Cleaned_Keywords": st.session_state.get("final_clean_df", pd.DataFrame()),
    }
    excel_buffer = export_data_to_excel(dfs_to_export)
    st.download_button(
        label="⬇️ Download Full Excel Report",
        data=excel_buffer,
        file_name="keyword_intelligence.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
