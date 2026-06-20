import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def generate_link_suggestions(pages, similarity_threshold=0.20, max_suggestions_per_page=5):
    """
    Generate internal link suggestions based on content similarity.
    """

    if not pages:
        return pd.DataFrame()

    df = pd.DataFrame(pages)

    if len(df) < 2:
        print("At least 2 pages are needed for link suggestions.")
        return pd.DataFrame()

    # Combine important page elements
    df["combined_text"] = (
        df["title"].fillna("") + " " +
        df["h1"].fillna("") + " " +
        df["h2"].fillna("") + " " +
        df["content"].fillna("")
    )

    vectorizer = TfidfVectorizer(
        stop_words="english",
        max_features=5000
    )

    tfidf_matrix = vectorizer.fit_transform(df["combined_text"])

    similarity_matrix = cosine_similarity(tfidf_matrix)

    suggestions = []

    for source_index in range(len(df)):
        source_url = df.iloc[source_index]["url"]
        source_title = df.iloc[source_index]["title"]

        similarities = []

        for target_index in range(len(df)):
            if source_index == target_index:
                continue

            score = similarity_matrix[source_index][target_index]

            if score >= similarity_threshold:
                similarities.append((target_index, score))

        similarities = sorted(similarities, key=lambda x: x[1], reverse=True)
        similarities = similarities[:max_suggestions_per_page]

        for target_index, score in similarities:
            target_url = df.iloc[target_index]["url"]
            target_title = df.iloc[target_index]["title"]

            suggestions.append({
                "source_url": source_url,
                "source_title": source_title,
                "target_url": target_url,
                "target_title": target_title,
                "similarity_score": round(float(score), 3),
                "suggestion": f"Add an internal link from '{source_title}' to '{target_title}'"
            })

    result_df = pd.DataFrame(suggestions)

    return result_df
