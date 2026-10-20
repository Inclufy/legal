#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bouwt het levende concept-whitepaper van MIT-28436.

Werkwijze:
  1. Leest de onderzoeksdata: lokaal (JSONL/JSON-bestanden of mappen) en/of
     rechtstreeks uit productie via het export-endpoint.
  2. Ververst in elk hoofdstukbestand de blokken tussen
     <!-- AUTO:naam begin --> en <!-- AUTO:naam einde -->.
     Alles buiten die markeringen (desk research, duiding, redactie) blijft
     onaangeroerd.
  3. Plakt de hoofdstukken aaneen tot Whitepaper_Concept_MIT_28436.md en
     rendert, als de benodigdheden aanwezig zijn, een PDF in huisstijl.

Gebruik:
    python3 bouw_whitepaper.py --data pad/naar/inzendingen.jsonl
    python3 bouw_whitepaper.py --url https://inclufy.com/api/onderzoek/export/ --token GEHEIM
    python3 bouw_whitepaper.py --data a.jsonl --data map/ --geen-pdf

Zonder --data en --url worden alleen de markeringen gecontroleerd en het
document samengesteld met de bestaande blokinhoud.
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

HIER = Path(__file__).resolve().parent
sys.path.insert(0, str(HIER.parent / "onderzoek" / "verwerking"))
import verwerk_enquete as vw  # noqa: E402  (gedeelde tel- en tabel-logica)

HOOFDSTUKKEN = HIER / "hoofdstukken"
UITVOER_MD = HIER / "Whitepaper_Concept_MIT_28436.md"
UITVOER_PDF = HIER / "Whitepaper_Concept_MIT_28436.pdf"

PDF_CSS = """
@page { size: A4; margin: 22mm 24mm 20mm 24mm; }
body { font-family: Cambria, Georgia, 'Times New Roman', serif; font-size: 10.5pt;
       line-height: 1.5; color: #000; margin: 0; }
h1 { font-size: 17pt; margin: 0 0 6px 0; color: #001F3A; }
h2 { font-size: 13pt; margin: 18px 0 6px 0; border-bottom: 2px solid #55A631;
     padding-bottom: 3px; color: #001F3A; page-break-after: avoid; }
h3 { font-size: 11pt; margin: 12px 0 4px 0; color: #001F3A; page-break-after: avoid; }
p { margin: 6px 0; }
table { border-collapse: collapse; width: 100%; margin: 8px 0; font-size: 9pt; }
td, th { border: 1px solid #999; padding: 4px 7px; text-align: left; vertical-align: top; }
th { background: #F2F8EE; }
blockquote { border-left: 3px solid #55A631; margin: 10px 0; padding: 4px 12px;
             background: #f7f7f7; color: #333; }
em { color: #333; }
hr { border: 0; border-top: 1px solid #ccc; margin: 14px 0; }
.hoofdstuk { page-break-before: always; }
.hoofdstuk:first-child { page-break-before: avoid; }
"""


# ---------- data inlezen ----------

def laad_van_url(url, token):
    verzoek = urllib.request.Request(url, headers={"X-Onderzoek-Token": token})
    with urllib.request.urlopen(verzoek, timeout=30) as antwoord:
        tekst = antwoord.read().decode("utf-8").strip()
    if tekst.startswith("["):
        ruwe = json.loads(tekst)
    else:
        ruwe = [json.loads(r) for r in tekst.splitlines() if r.strip()]
    inz = []
    for r in ruwe:
        schoon = {k: v for k, v in r.items()
                  if k not in vw.PERSOONSVELDEN and not k.startswith("_")}
        schoon["_bron"] = "interview" if schoon.get("type") == "interview" else "enquete"
        inz.append(schoon)
    return inz


# ---------- blokgeneratoren ----------

def blok_deelnemers(inz):
    ne = sum(1 for i in inz if i["_bron"] == "enquete")
    ni = len(inz) - ne
    return (f"**{len(inz)} deelnemers verwerkt** ({ne} enquête-inzendingen, "
            f"{ni} gecodeerde bedrijfsinterviews). Dit aantal en alle tabellen in "
            "hoofdstuk 1 en 4 tot en met 8 worden automatisch ververst uit de "
            "onderzoeksdatabase.")


def blok_methode(inz):
    d = [blok_deelnemers(inz), ""]
    d.append(vw.tabel(inz, "sector", "Spreiding naar sector"))
    d.append(vw.tabel(inz, "omvang", "Spreiding naar bedrijfsomvang"))
    d.append(vw.tabel(inz, "regio", "Spreiding naar regio"))
    intv = vw.deel(inz, "interview")
    if intv:
        zicht = vw.tel(intv, "onvoldoende_zicht")
        kaart = sum(1 for i in intv if i.get("voorbeeldkaart_gebruikt"))
        d.append(f"Methodenotities interviews: voorbeeldkaart gebruikt bij {kaart} van de "
                 f"{len(intv)}; blokken met vinkje \"onvoldoende zicht\": "
                 + (", ".join(f"{vw.label('onvoldoende_zicht', s)} ({c}x)" for s, c in zicht.items()) or "geen") + ".")
    return "\n".join(d)


def blok_resultaten(inz):
    intv = vw.deel(inz, "interview")
    d = []
    a = d.append
    a("### 4.1 Huidig AI-gebruik\n")
    a(vw.tabel(inz, "ai_gebruik", "Werkt het bedrijf al met AI-tools?"))
    a("Toelichtingen (gebruik of reden om niet te gebruiken):\n")
    a(vw.citatenblok(vw.open_antwoorden(inz, "ai_toelichting"), "Geen toelichtingen gegeven."))
    a("### 4.2 Taken: wat mag een AI-agent wel en niet\n")
    a(vw.tabel(inz, "taken", "Taken die men een AI-agent zelfstandig zou laten uitvoeren", meerkeuze=True))
    a("Wat men een AI-agent nooit zelfstandig zou laten doen:\n")
    a(vw.citatenblok(vw.open_antwoorden(inz, "nooit"), "Geen open antwoorden."))
    a("### 4.3 Menselijke controle en voorwaarden\n")
    a(vw.tabel(inz, "controle", "Gewenste mate van menselijke controle"))
    a(vw.tabel(inz, "waarborgen", "Wat minimaal geregeld moet zijn", meerkeuze=True))
    a("### 4.4 Drempels, regelkennis en betalingsbereidheid\n")
    a(vw.tabel(inz, "drempel", "Grootste drempel"))
    a(vw.tabel(inz, "regels_bekend", "Bekendheid met AVG en AI-verordening"))
    if intv:
        spontaan, aangereikt = vw.tel(intv, "regels_spontaan"), vw.tel(intv, "regels_aangereikt")
        alle = sorted(set(spontaan) | set(aangereikt))
        if alle:
            a("Regelkennis in de interviews, spontaan genoemd tegenover pas na aanreiken herkend:\n")
            a("| Regel | Spontaan genoemd | Na aanreiken |\n|---|---|---|")
            for r in alle:
                a(f"| {r} | {spontaan.get(r, 0)} | {aangereikt.get(r, 0)} |")
            a("")
    a(vw.tabel(inz, "budget", "Betalingsbereidheid per maand"))
    prijsvorm = vw.tel(intv, "prijsvorm")
    if prijsvorm:
        a("Genoemde prijsvorm in de interviews: "
          + ", ".join(f"{s} ({c}x)" for s, c in prijsvorm.most_common()) + ".\n")
    a(vw.tabel(inz, "ondersteuning", "Gewenste externe ondersteuning", meerkeuze=True))
    a("### 4.5 Kansen en zorgen\n")
    a(vw.citatenblok(vw.open_antwoorden(inz, "kans_zorg"), "Geen open antwoorden."))
    return "\n".join(d)


def _kerncijfers(inz):
    n = len(inz)
    ai = vw.tel(inz, "ai_gebruik")
    controle = vw.tel(inz, "controle")
    regels = vw.tel(inz, "regels_bekend")
    budget = vw.tel(inz, "budget")
    return {
        "n": n,
        "gebruikt_ai": ai.get("dagelijks", 0) + ai.get("soms", 0),
        "wil_mens": controle.get("alles_vooraf", 0) + controle.get("belangrijk_vooraf", 0),
        "regels_onduidelijk": regels.get("onbekend", 0) + regels.get("gehoord", 0),
        "betaalt": sum(a for s, a in budget.items()
                       if s not in ("Niets",) and not s.startswith("Dat hangt")),
        "taken": vw.tel(inz, "taken"),
        "drempel": vw.tel(inz, "drempel"),
        "waarborgen": vw.tel(inz, "waarborgen"),
        "ondersteuning": vw.tel(inz, "ondersteuning"),
    }


def blok_conclusies(inz):
    if not inz:
        return "*Nog geen data verwerkt.*"
    k = _kerncijfers(inz)
    n = k["n"]
    d = ["**Automatisch voorstel op basis van de huidige data; validatie volgt hieronder.**", ""]
    d.append(f"- {k['gebruikt_ai']} van de {n} deelnemers ({round(100*k['gebruikt_ai']/n)}%) gebruikt al AI; "
             f"meest genoemde zelfstandige taak: {', '.join(vw.top(k['taken'], 'taken')) or 'geen'}.")
    d.append(f"- {k['wil_mens']} van de {n} ({round(100*k['wil_mens']/n)}%) wil menselijke goedkeuring vooraf "
             "(volledig of bij belangrijke beslissingen).")
    d.append(f"- Meest genoemde drempel: {', '.join(vw.top(k['drempel'], 'drempel')) or 'geen'}; "
             f"meest gevraagde voorwaarde: {', '.join(vw.top(k['waarborgen'], 'waarborgen')) or 'geen'}.")
    d.append(f"- {k['regels_onduidelijk']} van de {n} ({round(100*k['regels_onduidelijk']/n)}%) kent de relevante "
             "regels (AVG, AI-verordening) niet of weet niet wat ze voor het eigen bedrijf betekenen.")
    d.append(f"- {k['betaalt']} van de {n} ({round(100*k['betaalt']/n)}%) noemt een concreet maandbedrag boven nul "
             "als betalingsbereidheid bij aantoonbare tijdsbesparing.")
    return "\n".join(d)


def blok_aanbevelingen(inz):
    if not inz:
        return "*Nog geen data verwerkt.*"
    k = _kerncijfers(inz)
    n = max(k["n"], 1)
    d = ["**Automatisch voorstel op basis van vaste drempelregels; uitwerking volgt hieronder.**", ""]
    if k["waarborgen"].get("goedkeuring", 0) * 2 >= n:
        d.append("- Ontwerp agentic AI voor het MKB standaard met menselijke goedkeuring op belangrijke acties; "
                 "dit is de meest gevraagde voorwaarde.")
    if k["regels_onduidelijk"] * 2 >= n:
        d.append("- Zet in op praktische voorlichting over AVG en AI-verordening voor het MKB; de meerderheid "
                 "kent de regels niet of begrijpt de eigen verplichtingen niet.")
    if k["ondersteuning"]:
        d.append(f"- Richt ondersteuning op wat bedrijven zelf vragen: {', '.join(vw.top(k['ondersteuning'], 'ondersteuning', 3))}.")
    if k["drempel"]:
        d.append(f"- Adresseer de grootste drempel ({', '.join(vw.top(k['drempel'], 'drempel'))}) expliciet in "
                 "productontwerp en communicatie.")
    return "\n".join(d)


def blok_gaps(inz):
    if not inz:
        return "*Nog geen data verwerkt.*"
    intv = vw.deel(inz, "interview")
    k = _kerncijfers(inz)
    n = k["n"]
    d = []
    a = d.append
    a("**Gap-register uit de interviews**\n")
    gaps = [(f"interview {i.get('interviewnummer', '?')}", g)
            for i in intv for g in vw.als_lijst(i.get("gap_signalen"))]
    if gaps:
        a("| Bron | Signaal |\n|---|---|")
        for bron, g in gaps:
            a(f"| {bron} | {g} |")
        a("")
    else:
        a("*Nog geen interview-gap-signalen ingevoerd.*\n")
    a("**Gemiste regels en gewenste duidelijkheid**\n")
    a(vw.citatenblok(vw.open_antwoorden(inz, "regels_gemist"),
                     "Geen open antwoorden; toets in de interviews of regelkennis werkelijk dekkend is."))
    a("Opvattingen over aansprakelijkheid (O, geen juridische conclusies):\n")
    a(vw.citatenblok(vw.open_antwoorden(intv, "aansprakelijkheid_opvatting"), "Nog geen interviewdata."))
    a("Gewenste duidelijkheid vanuit overheid of wetgeving:\n")
    a(vw.citatenblok(vw.open_antwoorden(inz, "duidelijkheid_overheid"), "Nog geen antwoorden."))
    a("**Automatische signalen uit de gesloten vragen**\n")
    a(f"- Regelkennis-gap: {k['regels_onduidelijk']} van de {n} kent AVG/AI-verordening niet of onvoldoende.")
    a(f"- Aansprakelijkheid als grootste drempel: {k['drempel'].get('aansprakelijkheid', 0)} van de {n}; "
      f"privacy/AVG: {k['drempel'].get('privacy', 0)}; vertrouwen/uitlegbaarheid: {k['drempel'].get('vertrouwen', 0)}.")
    return "\n".join(d)


def blok_vervolg(inz):
    if not inz:
        return "*Nog geen data verwerkt.*"
    k = _kerncijfers(inz)
    n = max(k["n"], 1)
    d = ["**Automatische aanzetten op basis van de signalen in hoofdstuk 7; uitwerking volgt hieronder.**", ""]
    if k["regels_onduidelijk"] * 2 >= n:
        d.append("- Juridisch vervolgonderzoek: welke verplichtingen uit de AI-verordening raken MKB-gebruikers "
                 "van agentic AI concreet, en waar is de uitleg voor kleine organisaties niet eenduidig "
                 "(wetgevingsgap tegenover voorlichtingsgap).")
    if k["drempel"].get("aansprakelijkheid", 0):
        d.append("- Aansprakelijkheidsonderzoek: hoe verdeelt aansprakelijkheid zich tussen gebruiker en "
                 "leverancier bij zelfstandig handelende agents, en volstaan de bestaande kaders voor het MKB.")
    d.append("- Vervolgmeting: herhaal de enquête na publicatie van de whitepaper om verschuiving in "
             "regelkennis en adoptie te meten.")
    return "\n".join(d)


BLOKKEN = {
    "deelnemers": blok_deelnemers,
    "methode": blok_methode,
    "resultaten": blok_resultaten,
    "conclusies": blok_conclusies,
    "aanbevelingen": blok_aanbevelingen,
    "gaps": blok_gaps,
    "vervolg": blok_vervolg,
}

MARKERING = re.compile(r"(<!-- AUTO:(\w+) begin -->)(.*?)(<!-- AUTO:\2 einde -->)", re.DOTALL)


def ververs_hoofdstukken(inz):
    ververst = []
    for pad in sorted(HOOFDSTUKKEN.glob("*.md")):
        tekst = pad.read_text(encoding="utf-8")

        def vervang(m):
            naam = m.group(2)
            if naam not in BLOKKEN:
                return m.group(0)
            ververst.append(f"{pad.name}:{naam}")
            return f"{m.group(1)}\n{BLOKKEN[naam](inz)}\n{m.group(4)}"

        nieuw = MARKERING.sub(vervang, tekst)
        if nieuw != tekst:
            pad.write_text(nieuw, encoding="utf-8")
    return ververst


def stel_samen():
    delen = [p.read_text(encoding="utf-8").strip() for p in sorted(HOOFDSTUKKEN.glob("*.md"))]
    UITVOER_MD.write_text("\n\n".join(delen) + "\n", encoding="utf-8")
    return UITVOER_MD


def render_pdf():
    try:
        import markdown
    except ImportError:
        print("PDF overgeslagen: python-pakket 'markdown' niet beschikbaar (pip install markdown).")
        return None
    chrome = None
    for kandidaat in (shutil.which("chromium"), shutil.which("google-chrome"), shutil.which("headless_shell")):
        if kandidaat:
            chrome = kandidaat
            break
    if not chrome:
        import glob
        treffers = glob.glob("/opt/pw-browsers/**/headless_shell", recursive=True)
        chrome = treffers[0] if treffers else None
    if not chrome:
        print("PDF overgeslagen: geen Chromium gevonden.")
        return None
    delen = []
    for p in sorted(HOOFDSTUKKEN.glob("*.md")):
        html_deel = markdown.markdown(p.read_text(encoding="utf-8"), extensions=["tables"])
        delen.append(f'<div class="hoofdstuk">{html_deel}</div>')
    html = ("<!DOCTYPE html><html lang=\"nl\"><head><meta charset=\"utf-8\">"
            f"<style>{PDF_CSS}</style></head><body>" + "\n".join(delen) + "</body></html>")
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as f:
        f.write(html)
        tijdelijk = f.name
    subprocess.run([chrome, "--headless", "--disable-gpu", "--no-sandbox",
                    f"--print-to-pdf={UITVOER_PDF}", "--no-pdf-header-footer", tijdelijk],
                   check=True, capture_output=True)
    return UITVOER_PDF


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", action="append", default=[],
                        help="JSONL/JSON-bestand of map met inzendingen (herhaalbaar)")
    parser.add_argument("--url", help="export-endpoint, bijv. https://inclufy.com/api/onderzoek/export/")
    parser.add_argument("--token", help="waarde voor de X-Onderzoek-Token header")
    parser.add_argument("--geen-pdf", action="store_true", help="alleen Markdown bouwen")
    args = parser.parse_args()

    inz = []
    if args.data:
        inz.extend(vw.lees_inzendingen(args.data))
    if args.url:
        if not args.token:
            sys.exit("--url vereist --token")
        inz.extend(laad_van_url(args.url, args.token))

    if inz:
        ververst = ververs_hoofdstukken(inz)
        print(f"{len(inz)} inzendingen verwerkt; blokken ververst: {', '.join(ververst) or 'geen'}")
    else:
        print("Geen data opgegeven; hoofdstukken ongewijzigd samengesteld.")

    md = stel_samen()
    print(f"Samengesteld: {md}")
    if not args.geen_pdf:
        pdf = render_pdf()
        if pdf:
            print(f"PDF: {pdf}")


if __name__ == "__main__":
    main()
