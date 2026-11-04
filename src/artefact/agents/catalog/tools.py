from langchain_core.tools import tool

from artefact.data import catalog as catalog_data


@tool
def search_products(
    query: str | None = None,
    category: str | None = None,
    max_price: float | None = None,
    in_stock_only: bool = False,
) -> dict:
    """Search the store catalog. Returns total_found (how many products match) and products:
    up to 40 of them, cheapest first, with name, category, price_brl, final_price_brl
    (with the active promotion applied), stock, status and promotion.

    Args:
        query: product name, brand or model, e.g. "Takamine GD20" or "Yamaha nylon".
            For a type of product such as "violões", use category instead.
        category: one of "Guitarras", "Baixos", "Baterias e Percussão", "Teclados e Pianos",
            "Violões", "Instrumentos de Sopro (Madeiras)", "Instrumentos de Sopro (Metais)",
            "Cordas Orquestrais", "Ukuleles".
        max_price: highest price in BRL.
        in_stock_only: only products that are active and have stock.
    """
    return catalog_data.search_products(query, category, max_price, in_stock_only)


@tool
def get_active_promotions(category: str | None = None) -> list[dict]:
    """List the promotions that are active right now, with the same fields as search_products;
    promotion holds the promotion name and discount. Expired promotions are never returned.

    Args:
        category: optional category name, same values as in search_products.
    """
    return catalog_data.get_active_promotions(category)
