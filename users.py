import streamlit as st
import bcrypt

MAX_LOGIN_ATTEMPTS = 5


def check_password(username, password):
    env_key = f"{username.upper()}_HASH"
    stored_hash = st.secrets.get(env_key)

    if not stored_hash:
        return False
    return bcrypt.checkpw(
        password.encode("utf-8"), stored_hash["value"].encode("utf-8")
    )


def login():
    if "login_attempts" not in st.session_state:
        st.session_state["login_attempts"] = 0

    if st.session_state["login_attempts"] >= MAX_LOGIN_ATTEMPTS:
        st.error("🚫 Too many failed login attempts. Try again later.")
        st.stop()

    st.markdown(
        """
<style>
.login-title {
    text-align: center;
    font-size: 28px;
    margin-bottom: 1.5rem;
    color: inherit;
}

/* Input boxes */
.stTextInput > div > div > input {
    background-color: #f0f2f6;
    color: #333;
    border: 1px solid #ccc;
    border-radius: 8px;
}

/* Input labels */
.stTextInput label {
    color: #666;
}

/* Login button */
.stButton > button {
    background-color: #3a8ddd;
    color: white;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    width: 100%;
    height: 3rem;
    margin-top: 1rem;
    transition: background-color 0.3s ease;
}

.stButton > button:hover {
    background-color: #337fcc;
}
</style>
""",
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(
            '<div class="login-title">🔐 Login User</div>', unsafe_allow_html=True
        )
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if check_password(username, password):
                st.session_state["authenticated"] = True
                st.session_state["username"] = username
                st.session_state["login_attempts"] = 0
                st.success(f"Welcome, {username}!")
                st.rerun()
            else:
                st.session_state["login_attempts"] += 1
                remaining = MAX_LOGIN_ATTEMPTS - st.session_state["login_attempts"]
                st.error(f"❌ Invalid credentials. {remaining} attempts left.")


def logout():
    username = st.session_state.get("username", "User")
    st.sidebar.markdown("---")
    st.sidebar.write(f"🔓 Logged in as: `{username}`")

    if st.sidebar.button("Logout"):
        for key in [
            "authenticated",
            "username",
            "final_df",
            "original_df",
            "removed_questions",
            "removed_patterns",
        ]:
            st.session_state.pop(key, None)
        st.success("👋 Logged out successfully.")
        st.rerun()
