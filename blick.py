import requests
import json
import time

SEARCH_TERMS = [
    "chmobile",
    "gomo",
    "galaxus mobile",
    "talktalk"
]

SEARCH_URL = "https://search.ws.blick.ch/search"
COMMENT_URL = "https://community.ws.blick.ch/community/comment/"

session = requests.Session()
session.trust_env = False


def get_all_search_results(term):

    page = 0
    articles = []

    while True:

        url = (
            f"{SEARCH_URL}"
            f"?pub=blick"
            f"&q={term}"
            f"&page={page}"
        )

        try:

            r = session.get(
                url,
                timeout=30
            )

            print(
                f"[SEARCH] {term} "
                f"Seite {page} "
                f"HTTP {r.status_code}"
            )

            if r.status_code != 200:
                break

            data = r.json()

        except Exception as e:

            print(
                f"Fehler Suche "
                f"{term} Seite {page}: {e}"
            )

            break

        total_pages = data.get(
            "total_pages",
            1
        )

        page_articles = data.get(
            "content",
            []
        )

        articles.extend(
            page_articles
        )

        print(
            f"  Artikel auf Seite: "
            f"{len(page_articles)} "
            f"| Total bisher: "
            f"{len(articles)}"
        )

        if page >= (total_pages - 1):
            break

        page += 1

        time.sleep(0.5)

    return articles


def get_all_comments(article_id):

    page = 1
    comments = []

    while True:

        url = (
            f"{COMMENT_URL}"
            f"?page={page}"
            f"&discussion_type_id={article_id}"
        )

        try:

            r = session.get(
                url,
                timeout=30
            )

            if r.status_code != 200:

                print(
                    f"[COMMENTS] "
                    f"{article_id} "
                    f"HTTP {r.status_code}"
                )

                break

            data = r.json()

        except Exception as e:

            print(
                f"[COMMENTS] "
                f"Fehler {article_id}: {e}"
            )

            break

        total_pages = data.get(
            "total_pages",
            1
        )

        page_comments = data.get(
            "content",
            []
        )

        comments.extend(
            page_comments
        )

        print(
            f"[COMMENTS] "
            f"{article_id} "
            f"{page}/{total_pages} "
            f"({len(page_comments)} Kommentare)"
        )

        if page >= total_pages:
            break

        page += 1

        time.sleep(0.3)

    return comments


output = []

for term in SEARCH_TERMS:

    print()
    print("=" * 60)
    print("SUCHE:", term)
    print("=" * 60)

    articles = get_all_search_results(term)

    for idx, article in enumerate(
        articles,
        start=1
    ):

        article_id = article.get(
            "articleId"
        )

        href = (
            article.get(
                "link",
                {}
            ).get(
                "href"
            )
        )

        article_url = None

        if href:
            article_url = (
                "https://www.blick.ch"
                + href
            )

        title = article.get(
            "title"
        )

        lead = article.get(
            "lead"
        )

        published_date = article.get(
            "publishedDate"
        )

        print()
        print(
            f"[ARTICLE] "
            f"{idx}/{len(articles)} "
            f"ID={article_id}"
        )

        #
        # NEWS RECORD
        #
        output.append({
            "record_type": "news",
            "search_term": term,
            "article_id": article_id,
            "url": article_url,
            "title": title,
            "lead": lead,
            "published_date": published_date,

            "comment_id": None,
            "comment_body": None,
            "comment_user": None,
            "comment_created": None
        })

        #
        # COMMENTS
        #
        comments = []

        if article_id:
            comments = get_all_comments(
                article_id
            )

        for comment in comments:

            output.append({
                "record_type": "comment",
                "search_term": term,
                "article_id": article_id,
                "url": article_url,
                "title": title,
                "lead": lead,
                "published_date": published_date,

                "comment_id":
                    comment.get(
                        "id"
                    ),

                "comment_body":
                    comment.get(
                        "body"
                    ),

                "comment_user":
                    comment.get(
                        "user",
                        {}
                    ).get(
                        "name"
                    ),

                "comment_created":
                    comment.get(
                        "created"
                    )
            })

        time.sleep(0.2)

with open(
    "blick_export.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        output,
        f,
        ensure_ascii=False,
        indent=2
    )

print()
print("=" * 60)
print("FERTIG")
print(f"Datensätze: {len(output):,}")
print("Datei gespeichert:")
print("  blick_export.json")
print("=" * 60)
