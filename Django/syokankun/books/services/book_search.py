from datetime import datetime
import json
import os
import re
import time
from django.db import transaction
from django.db.models import Q
from google import genai
from google.genai import types
import requests
import logging

logger = logging.getLogger(__name__)

from books.models import Book

try:
    from books.models import Series
except ImportError:
    Series = None
    
GEMINI_API_KEY=""

RAKUTEN_BOOKS_API_URL = (
    "https://app.rakuten.co.jp/services/api/BooksBook/Search/20170404"
)
REQUEST_INTERVAL_SEC = 1.1  # レート制限（1 req/sec）を考慮して余裕を持たせる

SERIES_EXTRACTOR_PROMPT = """あなたは書籍データベースの検索補助AIです。
ユーザーが入力した書籍情報（タイトルまたはISBN、複数行の場合あり）をもとに、
その本が属するシリーズ（続編・関連巻・既刊・未発売巻を含む）の
「シリーズ名」「著者名」「タイトル候補」「ISBN候補」を抽出してください。

【ルール】
1. ユーザー入力に含まれる書籍も候補に含めてください。
2. 同じシリーズ・関連作品として楽天ブックスAPIで検索できそうなタイトルを優先的に挙げてください。
3. ISBNは確実にわかるもののみ記載し、推測や不確かな番号は入れないでください（わからなければ空配列 [] で構いません）。
4. 出力は必ず指定のJSON形式のみとし、説明文は含めないでください。

【出力フォーマット】
{{
  "series_names": ["シリーズ名1"],
  "authors": ["著者名1"],
  "titles": ["タイトル候補1", "タイトル候補2"],
  "isbns": ["9784000000001"]
}}

【ユーザー入力】
{user_inputs_text}
"""


def parse_raw_inputs(raw_text: str) -> list[str]:
    """改行区切りの入力を整形し、空行除外・重複排除して返す"""
    if not raw_text:
        return []
    lines = [line.strip() for line in raw_text.splitlines()]
    return list(dict.fromkeys([line for line in lines if line]))


def normalize_isbn(value: str) -> str:
    """ハイフンや空白を除いてISBN（10桁/13桁）を正規化する"""
    return re.sub(r"[^0-9Xx]", "", value or "").upper()


def _clean_str_list(values: object) -> list[str]:
    """JSON配列から有効な文字列のみを抽出し、順序を保ったまま重複排除する"""
    if not isinstance(values, list):
        return []
    cleaned = [v.strip() for v in values if isinstance(v, str) and v.strip()]
    return list(dict.fromkeys(cleaned))


def extract_series_candidates(raw_text: str) -> dict:
    """
    改行区切りの入力（タイトル・ISBN）からAIで同シリーズ候補を抽出し、
    後続のDB検索・楽天API検索に渡せる辞書形式で返す。
    """
    user_inputs = parse_raw_inputs(raw_text)
    if not user_inputs:
        return {
            "raw_inputs": [],
            "series_names": [],
            "authors": [],
            "titles": [],
            "isbns": [],
        }

    direct_isbns = [
        norm for item in user_inputs if len(norm := normalize_isbn(item)) in (10, 13)
    ]

    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    model_name = os.environ.get("GEMINI_MODEL", "gemini-3.5-flash-lite")

    data: dict = {}
    if api_key:
        try:
            client = genai.Client(api_key=api_key)
            prompt = SERIES_EXTRACTOR_PROMPT.format(
                user_inputs_text="\n".join(user_inputs)
            )
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                ),
            )
            parsed = json.loads(response.text or "{}")
            if isinstance(parsed, dict):
                data = parsed
        except Exception:
            data = {}

    series_names = _clean_str_list(data.get("series_names"))
    authors = _clean_str_list(data.get("authors"))

    titles = _clean_str_list(data.get("titles"))
    for item in user_inputs:
        if len(normalize_isbn(item)) not in (10, 13):
            titles.append(item)
    titles = list(dict.fromkeys(titles))

    ai_isbns = [
        norm
        for raw_isbn in _clean_str_list(data.get("isbns"))
        if len(norm := normalize_isbn(raw_isbn)) in (10, 13)
    ]
    isbns = list(dict.fromkeys(direct_isbns + ai_isbns))

    return {
        "raw_inputs": user_inputs,
        "series_names": series_names,
        "authors": authors,
        "titles": titles,
        "isbns": isbns,
    }


def search_books_in_db(candidates: dict) -> dict:
    """
    AIで抽出した候補（series_names / titles / isbns）をもとに
    ローカルDB（books）を検索し、ヒットした書籍と不足候補を返す。
    """
    series_names = [s.strip() for s in candidates.get("series_names", []) if s and s.strip()]
    titles = [t.strip() for t in candidates.get("titles", []) if t and t.strip()]
    isbns = [normalize_isbn(i) for i in candidates.get("isbns", []) if i and i.strip()]
    isbns = [i for i in isbns if len(i) in (10, 13)]

    query_filter = Q()
    if isbns:
        query_filter |= Q(isbn__in=isbns)

    for series_name in series_names:
        query_filter |= Q(series_name__icontains=series_name)
        if Series is not None and any(f.name == "series" for f in Book._meta.get_fields()):
            query_filter |= Q(series__name__icontains=series_name)

    for title in titles:
        query_filter |= Q(title__icontains=title)

    if not query_filter:
        return {
            "books": [],
            "found_isbns": set(),
            "missing_isbns": isbns,
            "missing_titles": titles,
            "missing_series_names": series_names,
        }

    books_qs = Book.objects.filter(query_filter)
    if Series is not None and any(f.name == "series" for f in Book._meta.get_fields()):
        books_qs = books_qs.select_related("series")

    books = list(books_qs.distinct().order_by("volume_number", "sales_date", "id"))

    found_isbns = {normalize_isbn(book.isbn) for book in books if getattr(book, "isbn", None)}
    missing_isbns = [isbn for isbn in isbns if isbn not in found_isbns]

    existing_titles_lower = [
        (book.title or "").lower() for book in books if getattr(book, "title", None)
    ]
    missing_titles = [
        title
        for title in titles
        if not any(title.lower() in existing for existing in existing_titles_lower)
    ]

    existing_series_lower = []
    for book in books:
        if getattr(book, "series_name", None):
            existing_series_lower.append(book.series_name.lower())
        if getattr(book, "series", None) and getattr(book.series, "name", None):
            existing_series_lower.append(book.series.name.lower())

    missing_series_names = [
        s_name
        for s_name in series_names
        if not any(s_name.lower() in existing for existing in existing_series_lower)
    ]

    return {
        "books": books,
        "found_isbns": found_isbns,
        "missing_isbns": missing_isbns,
        "missing_titles": missing_titles,
        "missing_series_names": missing_series_names,
    }


def _parse_volume_number(title: str, series_name: str) -> int | None:
    target = title or ""
    if series_name and target.startswith(series_name):
        target = target[len(series_name) :]

    match = re.search(
        r"(?:第?\s*(\d+)\s*巻|[\s\(（【\[](\d+)[\)）】\]]?)$", target.strip()
    )
    if match:
        num_str = match.group(1) or match.group(2)
        return int(num_str) if num_str else None
    return None


def _parse_sales_date(raw_date: str):
    if not raw_date:
        return None
    normalized = (
        raw_date.replace("年", "-")
        .replace("月", "-")
        .replace("日", "")
        .replace("/", "-")
        .strip()
    )
    parts = [p.zfill(2) for p in normalized.split("-") if p.isdigit()]
    if len(parts) == 3:
        try:
            return datetime.strptime("-".join(parts), "%Y-%m-%d").date()
        except ValueError:
            return None
    if len(parts) == 2:
        try:
            return datetime.strptime(f"{parts[0]}-{parts[1]}-01", "%Y-%m-%d").date()
        except ValueError:
            return None
    return None


def _fetch_rakuten_items(params: dict) -> list[dict]:
    app_id = os.environ.get("")
    if not app_id:
        return []

    query_params = {
        "applicationId": app_id,
        "format": "json",
        "hits": 30,
        **params,
    }

    time.sleep(REQUEST_INTERVAL_SEC)
    try:
        resp = requests.get(RAKUTEN_BOOKS_API_URL, params=query_params, timeout=10)
        resp.raise_for_status()
        payload = resp.json()
        items = payload.get("Items", [])
        return [
            row.get("Item", {})
            for row in items
            if isinstance(row, dict) and row.get("Item")
        ]
    except Exception:
        return []


def _upsert_book_item(item: dict) -> Book | None:
    isbn = normalize_isbn(item.get("isbn", ""))
    title = (item.get("title") or "").strip()
    if not isbn or not title:
        return None

    series_name = (item.get("seriesName") or "").strip()
    author = (item.get("author") or "").strip()
    sales_date = _parse_sales_date(item.get("salesDate") or "")
    volume_number = _parse_volume_number(title, series_name)
    cover_url = (item.get("largeImageUrl") or item.get("mediumImageUrl") or "").strip()

    defaults = {
        "title": title,
        "author": author,
        "series_name": series_name,
        "volume_number": volume_number,
        "sales_date": sales_date,
        "cover_url": cover_url,
    }

    with transaction.atomic():
        if Series is not None and series_name:
            series_obj, _ = Series.objects.get_or_create(name=series_name)
            if any(f.name == "series" for f in Book._meta.get_fields()):
                defaults["series"] = series_obj

        valid_fields = {f.name for f in Book._meta.get_fields()}
        safe_defaults = {k: v for k, v in defaults.items() if k in valid_fields}

        book, _ = Book.objects.update_or_create(
            isbn=isbn,
            defaults=safe_defaults,
        )
    return book


def sync_missing_books_from_rakuten(
    db_result: dict,
    max_title_queries: int = 5,
) -> list[Book]:
    missing_isbns = [normalize_isbn(i) for i in db_result.get("missing_isbns", [])]
    missing_isbns = [i for i in dict.fromkeys(missing_isbns) if len(i) in (10, 13)]

    missing_series = [
        s.strip()
        for s in dict.fromkeys(db_result.get("missing_series_names", []))
        if s and s.strip()
    ]
    missing_titles = [
        t.strip()
        for t in dict.fromkeys(db_result.get("missing_titles", []))
        if t and t.strip()
    ]

    collected_items: list[dict] = []
    seen_isbns: set[str] = set()
    synced_series_lower: set[str] = set()

    def _add_items(items: list[dict]):
        for it in items:
            norm = normalize_isbn(it.get("isbn", ""))
            if norm and norm not in seen_isbns:
                seen_isbns.add(norm)
                collected_items.append(it)
            s_name = (it.get("seriesName") or "").strip().lower()
            if s_name:
                synced_series_lower.add(s_name)

    # 1. 不足ISBNを優先検索
    for isbn in missing_isbns:
        _add_items(_fetch_rakuten_items({"isbn": isbn}))

    # 2. 不足シリーズ名をシリーズ検索
    for series_name in missing_series:
        items = _fetch_rakuten_items({"seriesName": series_name})
        if not items:
            items = _fetch_rakuten_items({"title": series_name})
        _add_items(items)

    # 3. すでにシリーズ検索でカバー済みのものを除き、残りのタイトル候補を上限数まで検索
    title_queries_run = 0
    for title in missing_titles:
        if title_queries_run >= max_title_queries:
            logger.info("Reached max_title_queries (%d); skipping remaining titles.", max_title_queries)
            break
        if any(s in title.lower() for s in synced_series_lower):
            continue
        _add_items(_fetch_rakuten_items({"title": title}))
        title_queries_run += 1

    saved_books: list[Book] = []
    for item in collected_items:
        book = _upsert_book_item(item)
        if book is not None:
            saved_books.append(book)

    return saved_books


def search_books_pipeline(raw_text: str) -> list[Book]:
    """AI候補抽出 → DB検索 → 不足分の楽天API補完・保存を一括実行する"""
    candidates = extract_series_candidates(raw_text)
    db_result = search_books_in_db(candidates)

    books_by_isbn = {
        normalize_isbn(b.isbn): b for b in db_result["books"] if getattr(b, "isbn", None)
    }

    synced_books = sync_missing_books_from_rakuten(db_result)
    for b in synced_books:
        norm = normalize_isbn(b.isbn)
        if norm:
            books_by_isbn[norm] = b

    return list(books_by_isbn.values())