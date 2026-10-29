"""Tests for OLX parser and data normalization."""

from pathlib import Path
from src.providers.parser import (
    canonicalize_url,
    extract_source_id_from_url,
    parse_price,
    extract_district,
    extract_rooms,
    extract_area,
    parse_olx_html_list,
)


def test_price_parsing_uzs():
    """Test price strings in UZS."""
    samples = [
        ("3 500 000 so‘m", 3500000, "UZS"),
        ("2.600.000 сум", 2600000, "UZS"),
        ("4500000 UZS", 4500000, "UZS"),
        ("1,800,000 som", 1800000, "UZS"),
    ]
    for raw, expected_val, expected_curr in samples:
        price, curr, clean = parse_price(raw)
        assert price == expected_val, f"Failed for {raw}: got {price}"
        assert curr == expected_curr


def test_price_parsing_usd_conversion():
    """Test USD price conversion to UZS based on exchange rate."""
    samples = [
        ("300 y.e.", 300 * 12800, "USD"),
        ("$400", 400 * 12800, "USD"),
        ("500 у.е.", 500 * 12800, "USD"),
    ]
    for raw, expected_val, expected_curr in samples:
        price, curr, clean = parse_price(raw)
        assert price == expected_val, f"Failed for {raw}: got {price}"
        assert curr == expected_curr


def test_district_extraction():
    """Test recognition of Tashkent districts in Uzbek and Russian."""
    pairs = [
        ("Chilonzor 9-kvartalda kvartira", "Chilonzor"),
        ("Чиланзарский район, метро Чиланзар", "Chilonzor"),
        ("Yunusobod 4-mavze 1 xonali", "Yunusobod"),
        ("Юнусабад 11 квартал", "Yunusobod"),
        ("Mirzo Ulug‘bek tumani Buyuk Ipak Yo‘li", "Mirzo Ulug‘bek"),
        ("Мирзо-Улугбекский район", "Mirzo Ulug‘bek"),
        ("Yakkasaroy Shota Rustaveli", "Yakkasaroy"),
        ("Сергелийский р-н, Сергели 7", "Sergeli"),
        ("Olmazor tumani Qorasaroy", "Olmazor"),
        ("Шайхантахурский р-н", "Shayxontohur"),
        ("Учтепа 26-квартал", "Uchtepa"),
        ("Яшнабад Дустлик", "Yashnobod"),
        ("Yangi Hayot tumani", "Yangi Hayot"),
        ("Мирабадский район Госпитальный", "Mirobod"),
    ]
    for text, expected_district in pairs:
        res = extract_district(text)
        assert res == expected_district, f"Failed for '{text}': got '{res}'"


def test_room_count_extraction():
    """Test room count extraction."""
    samples = [
        ("1 xonali kvartira", 1),
        ("2-xona uy", 2),
        ("3 комнатная квартира", 3),
        ("4 хона", 4),
        ("Studiya kvartira ijaraga", 0),
        ("Студия в новостройке", 0),
    ]
    for text, expected_rooms in samples:
        assert extract_rooms(text) == expected_rooms


def test_area_extraction():
    """Test area extraction in m²."""
    samples = [
        ("54 m² kvartira", 54.0),
        ("82.5 м2 площадь", 82.5),
        ("Kvartira 36 кв.м", 36.0),
        ("120 kv.m", 120.0),
    ]
    for text, expected_area in samples:
        assert extract_area(text) == expected_area


def test_canonical_url_and_source_id():
    """Test query param stripping and source ID extraction."""
    raw_url = "https://www.olx.uz/d/oz/obyavlenie/chilonzor-2-xona-ID70101.html?search[order]=created_at:desc&utm_source=tg"
    canonical = canonicalize_url(raw_url)
    assert canonical == "https://www.olx.uz/d/oz/obyavlenie/chilonzor-2-xona-ID70101.html"
    source_id = extract_source_id_from_url(canonical)
    assert source_id == "70101"


def test_missing_fields_graceful_handling():
    """Missing or empty values must return None gracefully without raising exceptions."""
    assert parse_price(None) == (None, "UZS", None)
    assert extract_district("") is None
    assert extract_rooms("") is None
    assert extract_area("") is None
    assert canonicalize_url("") == ""
    assert extract_source_id_from_url("") is None


def test_fixture_based_html_parsing():
    """
    Test parsing an actual fixture HTML file without hitting external network.
    Verifies cards count, data fields, and resilient extraction.
    """
    fixture_path = Path(__file__).parent / "fixtures" / "sample_olx_page.html"
    html_content = fixture_path.read_text(encoding="utf-8")

    items = parse_olx_html_list(html_content)
    assert len(items) == 4

    # Item 1: Chilonzor 2-room
    i1 = items[0]
    assert i1.source_id == "10101"
    assert "chilonzor" in i1.canonical_url.lower()
    assert i1.district == "Chilonzor"
    assert i1.price_uzs == 3500000
    assert i1.rooms == 2
    assert len(i1.image_urls) == 1

    # Item 2: Yunusobod USD price & ISO timestamp
    i2 = items[1]
    assert i2.source_id == "10102"
    assert i2.district == "Yunusobod"
    assert i2.price_uzs == 300 * 12800
    assert i2.currency == "USD"
    assert i2.publication_date is not None
    assert i2.rooms == 1

    # Item 3: Mirzo Ulugbek
    i3 = items[2]
    assert i3.source_id == "10103"
    assert i3.district == "Mirzo Ulug‘bek"
    assert i3.price_uzs == 6000000
    assert i3.rooms == 3
    assert i3.area == 85.0

    # Item 4: Minimal fields (handled gracefully)
    i4 = items[3]
    assert i4.source_id == "10104"
    assert i4.title == "Kvartira ijaraga beriladi"
    assert i4.price_uzs is None
    assert i4.district is None

