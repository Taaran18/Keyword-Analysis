import os
import openai
import time
import streamlit as st

openai.api_key = st.secrets["OPENAI_API_KEY"]["value"]

if openai.api_key is None:
    raise ValueError("API key not found. Please set your OPENAI_API_KEY.")


def label_cluster_with_openai_intent(phrases):
    prompt = (
        "You are a world-class expert in search behavior and user intent classification.\n"
        "You will receive a list of search keywords that belong to the same topic cluster.\n\n"
        "Your task is to analyze this cluster deeply and return:\n"
        "1. A concise, clear sentence that explains what users in this cluster are trying to achieve or learn.\n"
        "2. A single, meaningful **intent category** for the cluster (not just generic terms like 'Informational', but actual purpose or action, like 'Booking', 'Comparison', 'Diagnosis', 'Purchase', 'Complaint', 'Exploration', etc.).\n\n"
        "Think about what real users are hoping to accomplish based on these terms.\n"
        "Make sure your category is specific, even if it's not a traditional taxonomy label.\n\n"
        "Respond in exactly this format:\n"
        "Intent Description: <detailed sentence>\n"
        "Intent Type: <one-word category>\n\n"
        "Here are the keywords:\n"
        + "\n".join(f"- {kw}" for kw in phrases)
        + "\n\nYour Answer:"
    )

    try:
        print(f"🔍 Prompting OpenAI with {len(phrases)} keywords...")
        response = openai.ChatCompletion.create(
            model="gpt-4.1-2025-04-14",
            messages=[
                {
                    "role": "system",
                    "content": "You are an assistant that helps with user intent classification.",
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=150,
            temperature=0,
        )
        result = response["choices"][0]["message"]["content"].strip()
        print("📥 OpenAI response:\n", result)

        desc = intent_type = ""
        for line in result.splitlines():
            line_lower = line.lower()
            if "intent description:" in line_lower:
                desc = line.split(":", 1)[-1].strip()
            elif "intent type:" in line_lower:
                intent_type = line.split(":", 1)[-1].strip()

        if not desc or not intent_type:
            return "Generic intent description", "Generic"

        return desc, intent_type

    except Exception as e:
        print("❌ OpenAI error:", e)
        return "Generic intent description", "Generic"


def label_all_clusters(df, embeddings, centers):
    cluster_labels = {}
    cluster_intents = {}
    total_clusters = df["Cluster"].nunique()
    start_time = time.time()

    for i, cluster_num in enumerate(df["Cluster"].unique(), start=1):
        cluster_keywords = df[df["Cluster"] == cluster_num]["Keyword"].tolist()
        sample_keywords = cluster_keywords[:10]
        try:
            description, intent_type = label_cluster_with_openai_intent(sample_keywords)
        except Exception:
            description, intent_type = "N/A", "N/A"

        cluster_labels[cluster_num] = description
        cluster_intents[cluster_num] = intent_type

    df["Intent_Description"] = df["Cluster"].map(cluster_labels)
    df["Intent_Type"] = df["Cluster"].map(cluster_intents)
    return df
