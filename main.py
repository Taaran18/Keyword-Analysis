import os
import argparse
from pathlib import Path
import pandas as pd
import warnings

# 🔇 Suppress TensorFlow and Keras logs
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
warnings.filterwarnings("ignore", category=DeprecationWarning)

from processor import (
    load_and_clean_file,
    filter_questions,
    filter_patterns,
    cluster_keywords,
)
from intent import label_all_clusters
from sentiment_helper import assign_cluster_sentiment


def process_keywords(file, user_filter, min_k, max_k, pos_def, neg_def):
    df = load_and_clean_file(file)
    if df is None:
        return None, None, None, None, None

    df_no_questions, df_removed_questions = filter_questions(df)
    word_list = [w.strip() for w in user_filter.split(",") if w.strip()]
    df_cleaned, df_removed_patterns_all = filter_patterns(
        df_no_questions.copy(), word_list
    )
    df_removed_patterns = df_removed_patterns_all[
        ~df_removed_patterns_all["Keyword"].isin(df_removed_questions["Keyword"])
    ]

    df_clustered, embeddings, centers, df_misc = cluster_keywords(
        df_cleaned, min_k, max_k
    )
    df_labeled = label_all_clusters(df_clustered, embeddings, centers)
    df_labeled = assign_cluster_sentiment(df_labeled, pos_def, neg_def)

    return df_labeled, df_cleaned, df_removed_questions, df_removed_patterns, df_misc


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Keyword Grouping CLI")
    parser.add_argument("file", help="Path to Excel file (.xlsx)")
    parser.add_argument(
        "--filter", default="free, help, download", help="Words to filter out"
    )
    parser.add_argument("--min", type=int, default=5, help="Minimum group size")
    parser.add_argument("--max", type=int, default=20, help="Maximum group size")
    parser.add_argument(
        "--positive", default="Seeking services", help="Definition of Positive Intent"
    )
    parser.add_argument(
        "--negative", default="Reporting issues", help="Definition of Negative Intent"
    )

    args = parser.parse_args()
    path = Path(args.file)

    if not path.exists():
        print(f"❌ File not found: {path}")
        exit(1)

    df_labeled, *_ = process_keywords(
        file=path,
        user_filter=args.filter,
        min_k=args.min,
        max_k=args.max,
        pos_def=args.positive,
        neg_def=args.negative,
    )

    if df_labeled is not None:
        output_path = path.with_stem(path.stem + "_processed").with_suffix(".xlsx")
        df_labeled.to_excel(output_path, index=False)
        print(f"✅ Success! Output saved to: {output_path}")
        print(df_labeled.head())
    else:
        print("❌ Failed to process file.")
