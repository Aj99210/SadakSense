"""Grounded complaint drafting: the VLM phrases facts, it never invents them."""
import datetime as dt
import hashlib
import json
import re
import httpx
from app.config import settings
from app.schemas import ComplaintRequest, ComplaintResponse

AUTHORITY = {"National Highway": ("NHAI Helpdesk", "https://helpdesk.nhai.org"),
             "State Highway": ("State PWD", "https://pgportal.gov.in"),
             "default": ("Municipal Corporation", "https://pgportal.gov.in")}


def facts_of(req: ComplaintRequest) -> dict:
    r = req.result
    return {"rqi": r.rqi, "condition": r.condition, "est_speed_kmh": r.est_speed_kmh,
            "damage_counts": r.damage_counts, "address": req.address, "city": req.city,
            "state": req.state, "pin": req.pin_code, "damage_since": req.damage_since}


def numbers(text: str) -> set:
    return set(re.findall(r"\d+(?:\.\d+)?", text))


def grounded(letter: str, facts: dict) -> bool:
    """Every figure in the letter must come from the findings (or today's date)."""
    allowed = numbers(json.dumps(facts)) | numbers(dt.date.today().isoformat())
    return numbers(letter) <= allowed


async def draft(req: ComplaintRequest) -> ComplaintResponse:
    facts = facts_of(req)
    prompt = ("Write a formal road-damage complaint letter in English. Use ONLY these facts; "
              "do not add numbers.\n" + json.dumps(facts))
    async with httpx.AsyncClient(timeout=60) as c:
        r = await c.post(f"{settings.vlm_base_url}/chat/completions", json={
            "model": settings.vlm_model, "temperature": 0.2,
            "messages": [{"role": "user", "content": prompt}]})
        r.raise_for_status()
    letter = r.json()["choices"][0]["message"]["content"]
    if not grounded(letter, facts):
        raise ValueError("Letter contains figures not present in findings")
    name, portal = AUTHORITY.get(req.road_type, AUTHORITY["default"])
    tag = int(hashlib.sha1(req.address.encode()).hexdigest(), 16) % 10000
    return ComplaintResponse(reference=f"SADAKSENSE-{dt.date.today():%Y%m%d}-{tag:04d}",
                             recipient=name, portal_url=portal, letter=letter)
