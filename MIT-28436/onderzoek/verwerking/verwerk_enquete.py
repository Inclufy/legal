#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verwerking enquête-inzendingen MIT-28436 naar concept-whitepaper.

Leest inzendingen van de enquête op inclufy.com/ai-onderzoek (versie 2 van de
vragen, 19 oktober 2026) en genereert een concept-whitepaper in Markdown met
de vijf vaste onderdelen: resultaten, conclusies, aanbevelingen, gaps en
risico's, en vervolgonderzoek. Op elke plek waar de interviews dezelfde
uitkomst verdiepen, staat een invulblok met verwijzing naar de
interviewvraag (zie Analysekader en Interviewvragenlijst v2).

Gebruik:
    python3 verwerk_enquete.py inzendingen.jsonl [uitvoer.md]
    python3 verwerk_enquete.py map_met_json_bestanden/ [uitvoer.md]

Invoer: JSON Lines (één inzending per regel), een JSON-array, of een map met
losse .json-bestanden (één inzending per bestand). De veldnamen zijn die van
het webformulier: sector, omvang, regio, ai_gebruik, ai_toelichting, taken,
nooit, controle, drempel, waarborgen, regels_bekend, regels_gemist, budget,
ondersteuning, kans_zorg, ingevuld_op. Meerkeuzevelden mogen een lijst of een
enkele string zijn.

Privacy: persoonsgegevens (naam, bedrijf, email, telefoon) worden bij het
inlezen verwijderd en komen nooit in de uitvoer. Open antwoorden worden
integraal maar zonder afzender opgenomen; de hoofdonderzoeker controleert ze
vóór publicatie op herleidbaarheid.
"""

import json
import sys
from collections import Counter
from datetime import date
from pathlib import Path

PERSOONSVELDEN = {"naam", "bedrijf", "email", "telefoon"}

# Antwoordvolgorde per gesloten vraag (volgorde van het formulier).
ORDES = {
    "ai_gebruik": ["dagelijks", "soms", "interesse", "nee"],
    "controle": ["alles_vooraf", "belangrijk_vooraf", "achteraf", "zelfstandig"],
    "drempel": ["vertrouwen", "privacy", "aansprakelijkheid", "kosten", "kennis", "anders"],
    "regels_bekend": ["onbekend", "gehoord", "globaal", "goed"],
}

LABELS = {
    "ai_gebruik": {"dagelijks": "Ja, dagelijks", "soms": "Ja, af en toe",
                   "interesse": "Nee, maar wel interesse", "nee": "Nee, geen plannen"},
    "controle": {"alles_vooraf": "Alles vooraf goedkeuren",
                 "belangrijk_vooraf": "Alleen belangrijke beslissingen vooraf",
                 "achteraf": "Achteraf controleren is genoeg",
                 "zelfstandig": "Volledig zelfstandig is prima"},
    "drempel": {"vertrouwen": "Vertrouwen (zicht en correctie)", "privacy": "Privacy en bedrijfsdata (AVG)",
                "aansprakelijkheid": "Aansprakelijkheid", "kosten": "Kosten en onduidelijke opbrengst",
                "kennis": "Kennis (waar te beginnen)", "anders": "Anders"},
    "regels_bekend": {"onbekend": "Niet bekend", "gehoord": "Van gehoord, betekenis onduidelijk",
                      "globaal": "Globaal bekend", "goed": "Goed bekend"},
    "taken": {"planning": "Projectplanning bijhouden en bijsturen", "cashflow": "Cashflow en budgetten vooruit rekenen",
              "offertes": "Offertes of rapportages opstellen", "klantcommunicatie": "Klantvragen beantwoorden",
              "content": "Marketingcontent maken en plaatsen", "campagnes": "Campagnes starten en bijsturen",
              "geen": "Geen enkele taak volledig zelfstandig"},
    "waarborgen": {"goedkeuring": "Belangrijke acties eerst ter goedkeuring aan een mens",
                   "logboek": "Logboek van alle handelingen", "uitleg": "Uitleg waarom de agent iets doet",
                   "stoppen": "Altijd direct kunnen stoppen of terugdraaien",
                   "keurmerk": "Onafhankelijke toetsing of certificering"},
    "ondersteuning": {"advies": "Advies van een expert", "training": "Praktische training voor het team",
                      "subsidie": "Subsidie of financiering", "voorbeelden": "Voorbeelden van vergelijkbare bedrijven",
                      "kennisinstelling": "Samenwerking met een kennisinstelling", "geen": "Geen behoefte"},
}

INTERVIEWBLOK = ("> **[AANVULLEN UIT INTERVIEWS: {verwijzing}]** {instructie}\n")


def lees_inzendingen(pad: Path):
    """Lees JSONL, JSON-array of een map met .json-bestanden; strip persoonsgegevens."""
    ruwe = []
    if pad.is_dir():
        for p in sorted(pad.glob("*.json")):
            ruwe.append(json.loads(p.read_text(encoding="utf-8")))
    else:
        tekst = pad.read_text(encoding="utf-8").strip()
        if tekst.startswith("["):
            ruwe = json.loads(tekst)
        else:
            ruwe = [json.loads(r) for r in tekst.splitlines() if r.strip()]
    inzendingen = []
    for r in ruwe:
        schoon = {k: v for k, v in r.items() if k not in PERSOONSVELDEN}
        inzendingen.append(schoon)
    return inzendingen


def als_lijst(waarde):
    if waarde is None:
        return []
    if isinstance(waarde, list):
        return [str(w) for w in waarde]
    return [str(waarde)]


def tel(inzendingen, veld):
    c = Counter()
    for i in inzendingen:
        for w in als_lijst(i.get(veld)):
            c[w] += 1
    return c


def label(veld, sleutel):
    return LABELS.get(veld, {}).get(sleutel, sleutel)


def tabel(inzendingen, veld, titel, meerkeuze=False):
    n = len(inzendingen)
    c = tel(inzendingen, veld)
    orde = ORDES.get(veld) or [k for k, _ in c.most_common()]
    regels = [f"**{titel}**", "", "| Antwoord | Aantal | Aandeel |", "|---|---|---|"]
    for sleutel in orde:
        aantal = c.get(sleutel, 0)
        pct = f"{round(100 * aantal / n)}%" if n else "-"
        regels.append(f"| {label(veld, sleutel)} | {aantal} | {pct} |")
    beantwoord = sum(1 for i in inzendingen if als_lijst(i.get(veld)))
    noemer = ("meerdere antwoorden mogelijk; aandelen op basis van alle "
              f"{n} inzendingen" if meerkeuze else f"beantwoord door {beantwoord} van {n}")
    regels.append(f"\n*({noemer})*\n")
    return "\n".join(regels)


def open_antwoorden(inzendingen, veld):
    uit = []
    for i in inzendingen:
        w = str(i.get(veld) or "").strip()
        if w:
            profiel = f"{i.get('sector', 'sector onbekend')}, {i.get('omvang', 'omvang onbekend')}"
            uit.append((profiel, w))
    return uit


def citatenblok(antwoorden, leeg):
    if not antwoorden:
        return f"*{leeg}*\n"
    return "\n".join(f'- "{t}" *({p})*' for p, t in antwoorden) + "\n"


def top(c: Counter, veld, k=1):
    return [f"{label(veld, s)} ({a}x)" for s, a in c.most_common(k)]


def genereer(inzendingen):
    n = len(inzendingen)
    vandaag = date.today().strftime("%d-%m-%Y")
    ai = tel(inzendingen, "ai_gebruik")
    taken = tel(inzendingen, "taken")
    controle = tel(inzendingen, "controle")
    drempel = tel(inzendingen, "drempel")
    waarborgen = tel(inzendingen, "waarborgen")
    regels = tel(inzendingen, "regels_bekend")
    budget = tel(inzendingen, "budget")
    onderst = tel(inzendingen, "ondersteuning")

    gebruikt_ai = ai.get("dagelijks", 0) + ai.get("soms", 0)
    regels_onduidelijk = regels.get("onbekend", 0) + regels.get("gehoord", 0)
    wil_mens = controle.get("alles_vooraf", 0) + controle.get("belangrijk_vooraf", 0)
    betaalt = sum(a for s, a in budget.items() if s not in ("Niets",) and not s.startswith("Dat hangt"))

    gemist = open_antwoorden(inzendingen, "regels_gemist")
    nooit = open_antwoorden(inzendingen, "nooit")
    kans_zorg = open_antwoorden(inzendingen, "kans_zorg")
    toelichting = open_antwoorden(inzendingen, "ai_toelichting")

    d = []
    a = d.append
    a("# Concept-whitepaper: Juridische kaders voor agentic AI in het MKB\n")
    a(f"**CONCEPT, automatisch gegenereerd op {vandaag} uit {n} enquête-inzendingen** "
      "(inclufy.com/ai-onderzoek). Dit concept is de kwantitatieve basis; de blokken "
      "[AANVULLEN UIT INTERVIEWS] worden gevuld uit de 15 tot 21 bedrijfsinterviews "
      "(Interviewvragenlijst v2) volgens het Analysekader. Automatisch gegenereerde "
      "conclusies en aanbevelingen zijn voorstellen en worden door de hoofdonderzoeker "
      "gevalideerd vóór enige publicatie.\n")
    a("Onderzoeksproject \"Haalbaarheid AI PM+Marketing\", MIT Haalbaarheid, provincie "
      "Flevoland, zaaknummer 28436. Mede mogelijk gemaakt door een subsidie van de "
      "provincie Flevoland.\n")

    a("## 1. Inleiding en methode\n")
    a(f"Dit concept bundelt {n} enquête-inzendingen. De enquête (tien vragen, versie 2 "
      "van 19 oktober 2026) en de interviews (twaalf hoofdvragen, versie 2) zijn op "
      "hetzelfde analysekader gebouwd: elke uitkomstcategorie wordt door beide "
      "instrumenten gevoed, zodat resultaten optelbaar en vergelijkbaar zijn.\n")
    a(tabel(inzendingen, "sector", "Spreiding naar sector"))
    a(tabel(inzendingen, "omvang", "Spreiding naar bedrijfsomvang"))
    a(tabel(inzendingen, "regio", "Spreiding naar regio"))
    a(INTERVIEWBLOK.format(verwijzing="bedrijfsprofielen",
      instructie="Vul de spreidingstabellen aan met de interviewbedrijven en benoem de gezamenlijke dekking."))

    a("## 2. Resultaten\n")
    a("### 2.1 Huidig AI-gebruik\n")
    a(tabel(inzendingen, "ai_gebruik", "Werkt het bedrijf al met AI-tools? (enquêtevraag 1)"))
    a("Toelichtingen (gebruik of reden om niet te gebruiken):\n")
    a(citatenblok(toelichting, "Geen toelichtingen gegeven."))
    a(INTERVIEWBLOK.format(verwijzing="interviewvraag 1 en 5",
      instructie="Huidige werkwijze en AI-gebruik uit de interviews (H-notities), gescheiden van verwachtingen (V)."))
    a("### 2.2 Taken: wat mag een AI-agent wel en niet\n")
    a(tabel(inzendingen, "taken", "Taken die men een AI-agent zelfstandig zou laten uitvoeren (enquêtevraag 2)", meerkeuze=True))
    a("Wat men een AI-agent nooit zelfstandig zou laten doen (enquêtevraag 3):\n")
    a(citatenblok(nooit, "Geen open antwoorden."))
    a(INTERVIEWBLOK.format(verwijzing="interviewvraag 2, 6 en 9",
      instructie="Taken wel/niet per domein (projectmanagement, marketing, overige processen), met concrete voorbeelden."))
    a("### 2.3 Menselijke controle en waarborgen\n")
    a(tabel(inzendingen, "controle", "Gewenste mate van menselijke controle (enquêtevraag 4)"))
    a(tabel(inzendingen, "waarborgen", "Minimaal gewenste waarborgen (enquêtevraag 6)", meerkeuze=True))
    a(INTERVIEWBLOK.format(verwijzing="interviewvraag 3, 4 en 7",
      instructie="Beslisgrenzen, controle en herstel van fouten; opvattingen over verantwoordelijkheid (O-notities) apart houden."))
    a("### 2.4 Drempels, regelkennis en betalingsbereidheid\n")
    a(tabel(inzendingen, "drempel", "Grootste drempel (enquêtevraag 5)"))
    a(tabel(inzendingen, "regels_bekend", "Bekendheid met AVG en AI-verordening (enquêtevraag 7)"))
    a(tabel(inzendingen, "budget", "Betalingsbereidheid per maand (enquêtevraag 8)"))
    a(tabel(inzendingen, "ondersteuning", "Gewenste externe ondersteuning (enquêtevraag 9)", meerkeuze=True))
    a(INTERVIEWBLOK.format(verwijzing="interviewvraag 8, 10, 11 en 12",
      instructie="Regelkennis (spontaan tegenover aangereikt), belemmeringen, investeringsvoorwaarden, prijsvorm en ordegrootte, externe ondersteuning."))
    a("### 2.5 Kansen en zorgen\n")
    a(citatenblok(kans_zorg, "Geen open antwoorden."))
    a(INTERVIEWBLOK.format(verwijzing="afsluitvraag interviews",
      instructie="Grootste kans en zorg per interviewbedrijf, plus gewenste duidelijkheid vanuit overheid of wetgeving."))

    a("## 3. Conclusies (automatisch voorstel, te valideren)\n")
    if n:
        a(f"- {gebruikt_ai} van de {n} bedrijven ({round(100*gebruikt_ai/n)}%) gebruikt al AI; "
          f"meest genoemde zelfstandige taak: {', '.join(top(taken, 'taken')) or 'geen'}.")
        a(f"- {wil_mens} van de {n} ({round(100*wil_mens/n)}%) wil menselijke goedkeuring vooraf "
          "(volledig of bij belangrijke beslissingen); volledige autonomie is een minderheidspositie.")
        a(f"- Meest genoemde drempel: {', '.join(top(drempel, 'drempel')) or 'geen'}; "
          f"meest gevraagde waarborg: {', '.join(top(waarborgen, 'waarborgen')) or 'geen'}.")
        a(f"- {regels_onduidelijk} van de {n} ({round(100*regels_onduidelijk/n)}%) kent de relevante "
          "regels (AVG, AI-verordening) niet of weet niet wat ze voor het eigen bedrijf betekenen.")
        a(f"- {betaalt} van de {n} ({round(100*betaalt/n)}%) noemt een concreet maandbedrag boven nul "
          "als betalingsbereidheid bij aantoonbare tijdsbesparing.\n")
    a(INTERVIEWBLOK.format(verwijzing="alle interviewblokken",
      instructie="Toets elk voorstel hierboven aan de interviewmatrices; benoem per conclusie het aantal dragende bedrijven (enquête plus interviews)."))

    a("## 4. Aanbevelingen (automatisch voorstel, te valideren)\n")
    if waarborgen.get("goedkeuring", 0) * 2 >= max(n, 1):
        a("- Ontwerp agentic AI voor het MKB standaard met menselijke goedkeuring op belangrijke "
          "acties; dit is de meest gevraagde waarborg.")
    if regels_onduidelijk * 2 >= max(n, 1):
        a("- Zet in op praktische voorlichting over AVG en AI-verordening voor het MKB; de "
          "meerderheid kent de regels niet of begrijpt de eigen verplichtingen niet.")
    if onderst:
        a(f"- Richt ondersteuning op wat bedrijven zelf vragen: {', '.join(top(onderst, 'ondersteuning', 3))}.")
    if drempel:
        a(f"- Adresseer de grootste drempel ({', '.join(top(drempel, 'drempel'))}) expliciet in "
          "productontwerp en communicatie.\n")
    a(INTERVIEWBLOK.format(verwijzing="interviewvraag 10, 11 en 12",
      instructie="Vul aan met leverancierseisen en ondersteuningsbehoeften uit de interviews; splits aanbevelingen naar MKB-bedrijven, leveranciers en ondersteunende partijen."))

    a("## 5. Gaps en risico's\n")
    a("Gemiste regels of gewenste duidelijkheid (enquêtevraag 7, open deel):\n")
    a(citatenblok(gemist, "Geen open antwoorden; dit is zelf een signaal: toets in de interviews of "
                  "regelkennis werkelijk dekkend is of dat men niet weet wat men mist."))
    a("Automatische signalen uit de gesloten vragen:\n")
    if n:
        a(f"- Regelkennis-gap: {regels_onduidelijk} van de {n} kent AVG/AI-verordening niet of onvoldoende.")
        a(f"- Aansprakelijkheid als drempel: {drempel.get('aansprakelijkheid', 0)} van de {n} noemt dit als grootste drempel.")
        a(f"- Privacy/AVG als drempel: {drempel.get('privacy', 0)} van de {n}.")
        a(f"- Vertrouwen/uitlegbaarheid: drempel bij {drempel.get('vertrouwen', 0)}, waarborg 'uitleg' gevraagd door {waarborgen.get('uitleg', 0)}.\n")
    a(INTERVIEWBLOK.format(verwijzing="gap-register interviews",
      instructie="Voeg het gap-register toe (gap-regels per blok, 'weet ik niet'-antwoorden, vinkjes onvoldoende zicht) en dedupliceer met de signalen hierboven. Laat elk gemist of onduidelijk juridisch kader in het bureauonderzoek duiden: voorlichtingsgap (kader bestaat, maar is onbekend) of wetgevingsgap (kader ontbreekt of is niet eenduidig)."))

    a("## 6. Vervolgonderzoek\n")
    a("Per gap of risico dat dit onderzoek niet kan beantwoorden volgt één concreet voorstel. "
      "Automatische aanzetten op basis van de enquête:\n")
    if regels_onduidelijk * 2 >= max(n, 1):
        a("- Juridisch vervolgonderzoek: welke verplichtingen uit de AI-verordening raken "
          "MKB-gebruikers van agentic AI concreet, en waar is de uitleg voor kleine organisaties "
          "nog niet eenduidig (wetgevingsgap tegenover voorlichtingsgap).")
    if drempel.get("aansprakelijkheid", 0):
        a("- Aansprakelijkheidsonderzoek: hoe verdeelt aansprakelijkheid zich tussen gebruiker en "
          "leverancier bij zelfstandig handelende agents, en volstaan de bestaande kaders "
          "(contractenrecht, productaansprakelijkheid) voor het MKB.")
    a("- Vervolgmeting: herhaal de enquête na publicatie van de whitepaper om verschuiving in "
      "regelkennis en adoptie te meten.\n")
    a(INTERVIEWBLOK.format(verwijzing="gap-register interviews",
      instructie="Vul de lijst aan vanuit het gap-register; formuleer per item een onderzoeksvraag, beoogde methode en relevante juridische kaders of wetgeving."))

    a("---\n*Gegenereerd met verwerk_enquete.py (MIT-28436). Persoonsgegevens worden bij het "
      "inlezen verwijderd en staan niet in dit document. Open antwoorden vóór publicatie "
      "controleren op herleidbaarheid.*")
    return "\n".join(d)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    invoer = Path(sys.argv[1])
    inzendingen = lees_inzendingen(invoer)
    if not inzendingen:
        print("Geen inzendingen gevonden.")
        sys.exit(1)
    uitvoer = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(
        f"Concept_Whitepaper_MIT_28436_{date.today().isoformat()}.md")
    uitvoer.write_text(genereer(inzendingen), encoding="utf-8")
    print(f"{len(inzendingen)} inzendingen verwerkt -> {uitvoer}")


if __name__ == "__main__":
    main()
