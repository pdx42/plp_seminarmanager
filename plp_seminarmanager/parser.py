"""HTML parser for ProfiLehrePlus seminar management."""

from __future__ import annotations

import re
from typing import Optional
from urllib.parse import parse_qs, urlparse

from bs4 import BeautifulSoup

from .models import DeliveryMode, Seminar, SeminarDetail, SeminarLink

DELIVERY_MODE_PATTERNS = {
    DeliveryMode.PRESENCE: re.compile(r"\b(präsenz|praesenz|vor ort|vorort|in\s*präsenz)\b", re.I),
    DeliveryMode.ONLINE: re.compile(r"\b(online|virtuell|webinar|digital)\b", re.I),
    DeliveryMode.HYBRID: re.compile(r"\b(hybrid|blended|mix\s+aus\s+online\s+und\s+präsenz)\b", re.I),
}

REGISTERED_PATTERNS = [
    re.compile(r"angemeldet[e]?\s*:?\s*(\d+)", re.I),
    re.compile(r"anmeldungen\s*:?\s*(\d+)", re.I),
]


def parse_management_html(html: str) -> list[Seminar]:
    """Parse the management overview table and return seminar stubs."""

    soup = BeautifulSoup(html, "html.parser")
    table = soup.select_one("#datatable-seminarmanagement")
    if table is None:
        return []

    headers = [
        th.get_text(strip=True).lower()
        for th in table.select("thead th")
    ]

    seminars: list[Seminar] = []
    for row in table.select("tbody tr"):
        cells = row.find_all("td")
        title = ""
        links: list[SeminarLink] = []
        management_url: Optional[str] = None
        seminar_id: Optional[str] = None

        for idx, cell in enumerate(cells):
            text = cell.get_text(" ", strip=True)
            header = headers[idx] if idx < len(headers) else ""

            for anchor in cell.find_all("a", href=True):
                label = anchor.get_text(strip=True) or header or "Link"
                url = anchor["href"]
                links.append(SeminarLink(label=label, url=url))
                if management_url is None:
                    management_url = url
                if seminar_id is None:
                    seminar_id = _extract_seminar_id(url)

            if not title and ("seminar" in header or "titel" in header or "bezeichnung" in header):
                title = text
            elif not title and text:
                title = text

        seminars.append(
            Seminar(
                seminar_id=seminar_id,
                title=title,
                management_url=management_url,
                links=links,
            )
        )

    return seminars


def parse_detail_html(html: str) -> SeminarDetail:
    """Parse seminar detail page HTML for description, delivery mode, and counts."""

    soup = BeautifulSoup(html, "html.parser")
    description = _extract_description(soup)
    delivery_mode = _extract_delivery_mode(description)
    registered_count = _extract_registered_count(soup.get_text(" ", strip=True))
    links = _extract_links(soup)

    return SeminarDetail(
        description=description,
        delivery_mode=delivery_mode,
        registered_count=registered_count,
        links=links,
    )


def _extract_description(soup: BeautifulSoup) -> str:
    candidates = [
        soup.select_one(".seminar-description"),
        soup.select_one(".seminar-description-text"),
        soup.select_one("#seminar-description"),
        soup.select_one(".seminar-content"),
        soup.select_one("main"),
    ]
    for candidate in candidates:
        if candidate and candidate.get_text(strip=True):
            return candidate.get_text(" ", strip=True)
    return soup.get_text(" ", strip=True)


def _extract_delivery_mode(text: str) -> DeliveryMode:
    for mode, pattern in DELIVERY_MODE_PATTERNS.items():
        if pattern.search(text):
            return mode
    return DeliveryMode.UNKNOWN


def _extract_registered_count(text: str) -> Optional[int]:
    for pattern in REGISTERED_PATTERNS:
        match = pattern.search(text)
        if match:
            return int(match.group(1))
    return None


def _extract_links(soup: BeautifulSoup) -> list[SeminarLink]:
    links: list[SeminarLink] = []
    for anchor in soup.find_all("a", href=True):
        label = anchor.get_text(strip=True) or "Link"
        links.append(SeminarLink(label=label, url=anchor["href"]))
    return links


def _extract_seminar_id(url: str) -> Optional[str]:
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    for key in ("seminar", "id", "seminarId"):
        if key in query and query[key]:
            return query[key][0]
    return None
