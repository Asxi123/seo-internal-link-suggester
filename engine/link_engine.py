import pandas as pd
from urllib.parse import urlparse, urlunparse
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def normalize_url(url):
    """
    Normalize URLs for better comparison.
    Removes fragments, query strings, and trailing slashes.
    """

    if not url:
        return ""

    parsed = urlparse(url)

    scheme = parsed.scheme.lower()
    netloc = parsed.netloc.lower()
    path = parsed.path.rstrip("/")

    normalized = urlunparse(
        (
            scheme,
            netloc,
            path,
            "",
            "",
            ""
        )
    )

    return normalized


def build_page_text(page):
    """
    Build weighted text from title, headings, and content.
    Title and headings are repeated to make them more important.
    """

    title = page.get("title", "") or ""
    h1 = page.get("h1", "") or ""
    h2 = page.get("h2", "") or ""
    content = page.get("content", "") or ""

    combined_text = f"""
    {title} {title} {title}
    {h1} {h1} {h1}
    {h2} {h2}
    {content}
    """

    return combined_text.strip()


def get_word_count(page):
    """
    Count words in the page content.
    """

    content = page.get("content", "") or ""

    words = content.split()

    return len(words)


def get_links_count(page):
    """
    Count all extracted links from the page.
    """

    links = page.get("links", []) or []

    return len(links)


def get_suggested_anchor_text(target_page):
    """
    Generate suggested anchor text.

    Priority:
    1. H1
    2. Title
    3. First H2
    4. URL
    """

    h1 = target_page.get("h1", "") or ""
    title = target_page.get("title", "") or ""
    h2 = target_page.get("h2", "") or ""
    url = target_page.get("url", "") or ""

    if h1:
        return h1.split("|")[0].strip()

    if title:
        return title.strip()

    if h2:
        return h2.split("|")[0].strip()

    return url.strip()


def get_priority(similarity_score, source_word_count, target_word_count):
    """
    Decide suggestion priority based on similarity and page depth.

    High:
        Strong similarity and both pages have meaningful content.

    Medium:
        Good similarity but less content or weaker score.

    Low:
        Weak similarity but still above threshold.
    """

    if similarity_score >= 0.35 and source_word_count >= 300 and target_word_count >= 300:
        return "High"

    if similarity_score >= 0.15:
        return "Medium"

    return "Low"


def generate_reason(similarity_score, source_page, target_page, priority):
    """
    Generate a human-readable reason for the suggestion.
    """

    source_title = source_page.get("title", "") or "source page"
    target_title = target_page.get("title", "") or "target page"

    if similarity_score >= 0.50:
        strength = "very strong topical similarity"
    elif similarity_score >= 0.30:
        strength = "strong topical similarity"
    elif similarity_score >= 0.15:
        strength = "moderate topical similarity"
    else:
        strength = "some topical similarity"

    reason = (
        f'The source page "{source_title}" and the target page "{target_title}" '
        f"have {strength} based on their titles, headings, and page content. "
        f"The suggested priority for this internal link is {priority}."
    )

    return reason


def page_already_links_to_target(source_page, target_page):
    """
    Check if the source page already links to the target page.
    """

    target_url = normalize_url(target_page.get("url", ""))

    source_links = source_page.get("links", []) or []

    normalized_source_links = set()

    for link in source_links:
        normalized_source_links.add(normalize_url(link))

    return target_url in normalized_source_links


def generate_link_suggestions(
    pages,
    similarity_threshold=0.05,
    max_suggestions_per_page=5
):
    """
    Generate internal link suggestions based on content similarity.

    Output includes:
    - source URL
    - target URL
    - similarity score
    - suggested anchor text
    - priority
    - word counts
    - link counts
    - reason
    """

    if not pages or len(pages) < 2:
        return pd.DataFrame()

    page_texts = [build_page_text(page) for page in pages]

    vectorizer = TfidfVectorizer(
        stop_words="english",
        max_features=5000,
        ngram_range=(1, 2)
    )

    tfidf_matrix = vectorizer.fit_transform(page_texts)
    similarity_matrix = cosine_similarity(tfidf_matrix)

    suggestions = []

    for source_index, source_page in enumerate(pages):
        source_url = source_page.get("url", "")
        source_title = source_page.get("title", "")

        source_word_count = get_word_count(source_page)
        source_links_count = get_links_count(source_page)

        page_suggestions = []

        for target_index, target_page in enumerate(pages):
            if source_index == target_index:
                continue

            target_url = target_page.get("url", "")
            target_title = target_page.get("title", "")

            link_exists = page_already_links_to_target(source_page, target_page)

            if link_exists:
                continue

            similarity_score = similarity_matrix[source_index][target_index]

            if similarity_score >= similarity_threshold:
                target_word_count = get_word_count(target_page)
                target_links_count = get_links_count(target_page)

                priority = get_priority(
                    similarity_score=similarity_score,
                    source_word_count=source_word_count,
                    target_word_count=target_word_count
                )

                suggested_anchor_text = get_suggested_anchor_text(target_page)

                reason = generate_reason(
                    similarity_score=similarity_score,
                    source_page=source_page,
                    target_page=target_page,
                    priority=priority
                )

                page_suggestions.append({
                    "priority": priority,
                    "source_url": source_url,
                    "source_title": source_title,
                    "target_url": target_url,
                    "target_title": target_title,
                    "similarity_score": round(float(similarity_score), 4),
                    "suggested_anchor_text": suggested_anchor_text,
                    "source_word_count": source_word_count,
                    "target_word_count": target_word_count,
                    "source_links_count": source_links_count,
                    "target_links_count": target_links_count,
                    "link_exists": link_exists,
                    "reason": reason,
                    "suggestion": (
                        f'Add an internal link from "{source_title}" '
                        f'to "{target_title}" using anchor text: '
                        f'"{suggested_anchor_text}".'
                    )
                })

        page_suggestions = sorted(
            page_suggestions,
            key=lambda item: item["similarity_score"],
            reverse=True
        )

        page_suggestions = page_suggestions[:max_suggestions_per_page]

        suggestions.extend(page_suggestions)

    df = pd.DataFrame(suggestions)

    if not df.empty:
        priority_order = {
            "High": 1,
            "Medium": 2,
            "Low": 3
        }

        df["priority_order"] = df["priority"].map(priority_order)

        df = df.sort_values(
            by=["priority_order", "source_url", "similarity_score"],
            ascending=[True, True, False]
        )

        df = df.drop(columns=["priority_order"])

    return df
