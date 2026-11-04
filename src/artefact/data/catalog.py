import unicodedata
from functools import cache

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from artefact.data.loader import load_csv

MAX_RESULTS = 40

MIN_SCORE = 0.3


def normalize(text: str) -> str:
    # Lowercase without accents, so "Violoes" matches "Violões"
    without_accents = (
        unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    )
    return without_accents.casefold().strip()


@cache
def catalog() -> pd.DataFrame:
    products = load_csv("products")

    categories = load_csv("categories")[["category_id", "name"]]
    categories = categories.rename(columns={"name": "category"})

    # Expired promotions are dropped here, so they can never be offered.
    promotions = load_csv("promotions")
    promotions = promotions[promotions["is_active"] == 1]
    promotions = promotions[["product_id", "discount_percent", "description"]]
    promotions = promotions.rename(columns={"description": "promotion"})

    df = products.merge(categories, on="category_id", how="left")
    df = df.merge(promotions, on="product_id", how="left")
    df["discount_percent"] = df["discount_percent"].fillna(0)
    df["final_price_brl"] = (
        df["price_brl"] * (1 - df["discount_percent"] / 100)
    ).round(2)
    return df


@cache
def search_index() -> tuple[TfidfVectorizer, object]:
    # Only name + category are indexed: some descriptions mention a different brand than the name
    texts = (catalog()["name"] + " " + catalog()["category"]).map(normalize)
    vectorizer = TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 4))
    matrix = vectorizer.fit_transform(texts)
    return vectorizer, matrix


def to_record(row: pd.Series) -> dict:
    promotion = None
    if pd.notna(row["promotion"]):
        promotion = f"{row['promotion']} ({int(row['discount_percent'])}% off)"
    return {
        "name": row["name"],
        "category": row["category"],
        "price_brl": float(row["price_brl"]),
        "final_price_brl": float(row["final_price_brl"]),
        "stock": int(row["stock_quantity"]),
        "status": row["status"],
        "promotion": promotion,
    }


def search_products(
    query: str | None = None,
    category: str | None = None,
    max_price: float | None = None,
    in_stock_only: bool = False,
) -> dict:
    df = catalog()

    # Open listings show only products on sale, a search by name also finds discontinued or coming-soon products, so the agent can explain their status
    if not query:
        df = df[df["status"] == "active"]
    if category:
        df = df[df["category"].map(normalize) == normalize(category)]
    if max_price is not None:
        df = df[df["final_price_brl"] <= max_price]
    if in_stock_only:
        df = df[(df["status"] == "active") & (df["stock_quantity"] > 0)]

    if query:
        vectorizer, matrix = search_index()
        scores = cosine_similarity(vectorizer.transform([normalize(query)]), matrix)[0]
        df = df.assign(score=scores[df.index])
        df = df[df["score"] >= MIN_SCORE].sort_values("score", ascending=False)
    else:
        df = df.sort_values("final_price_brl")

    records = []
    for _, row in df.head(MAX_RESULTS).iterrows():
        records.append(to_record(row))
    return {"total_found": len(df), "products": records}


def get_active_promotions(category: str | None = None) -> list[dict]:
    df = catalog()
    df = df[df["discount_percent"] > 0]
    if category:
        df = df[df["category"].map(normalize) == normalize(category)]

    records = []
    for _, row in df.sort_values("final_price_brl").iterrows():
        records.append(to_record(row))
    return records
