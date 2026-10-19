#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verwerking enquête-inzendingen en interviewuitkomsten MIT-28436 naar
concept-whitepaper.

Twee gegevensstromen, één uitkomstenset (zie Analysekader):
  1. Enquête-inzendingen van inclufy.com/ai-onderzoek (veldnamen van het
     webformulier), automatisch verzameld.
  2. Interviewuitkomsten: na elk interview codeert de analist de antwoorden
     in dezelfde veldnamen via interview_invoer_template.json (één
     JSON-bestand per interview, "type": "interview"). Open antwoorden
     letterlijk, zonder naam of bedrijfsnaam.

Het script telt beide bronnen op in dezelfde tabellen (kolommen Enquête,
Interviews, Totaal) en vult de interviewspecifieke onderdelen (gap-register,
regelkennis spontaan tegenover aangereikt, aansprakelijkheidsopvattingen,
prijsvorm) automatisch. Wat alleen uit menselijke duiding kan komen, blijft
als invulblok [DUIDING DOOR ANALIST] staan.

Gebruik:
    python3 verwerk_enquete.py INVOER... [UITVOER.md]
    # INVOER: een of meer .jsonl/.json-bestanden of mappen met .json-bestanden;
    # enquête en interviews mogen door elkaar staan (interviews herkenbaar aan
    # "type": "interview"). Het laatste argument dat op .md eindigt is de uitvoer.

Voorbeeld:
    python3 verwerk_enquete.py enquete.jsonl interviews/ Concept.md

Privacy: persoonsgegevens (naam, bedrijf, email, telefoon) worden bij het
inlezen verwijderd en komen nooit in de uitvoer. Open antwoorden vóór
publicatie controleren op herleidbaarheid.
"""

import json
import sys
from collections import Counter
from datetime import date
from pathlib import Path

PERSOONSVELDEN = {"naam", "bedrijf", "email", "telefoon"}

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
    "onvoldoende_zicht": {"projectmanagement": "Projectmanagement", "marketing": "Marketing",
                          "ai_agents": "AI-agents voor het mkb"},
}

DUIDING = "> **[DUIDING DOOR ANALIST: {wie}]** {wat}\n"


def lees_bestand(p: Path):
    tekst = p.read_text(encoding="utf-8").strip()
    if not tekst:
        return []
    if tekst.startswith("["):
        return json.loads(tekst)
    if tekst.startswith("{") and "\n{" not in tekst:
        return [json.loads(tekst)]
    return [json.loads(r) for r in tekst.splitlines() if r.strip()]


def lees_inzendingen(paden):
    alle = []
    for pad in paden:
        p = Path(pad)
        ruwe = []
        if p.is_dir():
            for sub in sorted(p.glob("*.json*")):
                ruwe.extend(lees_bestand(sub))
        else:
            ruwe = lees_bestand(p)
        for r in ruwe:
            schoon = {k: v for k, v in r.items()
                      if k not in PERSOONSVELDEN and not k.startswith("_")}
            schoon["_bron"] = "interview" if schoon.get("type") == "interview" else "enquete"
            alle.append(schoon)
    return alle


def als_lijst(waarde):
    if waarde is None:
        return []
    if isinstance(waarde, list):
        return [str(w) for w in waarde]
    w = str(waarde).strip()
    return [w] if w else []


def deel(inz, bron):
    return [i for i in inz if i["_bron"] == bron]


def tel(inz, veld):
    c = Counter()
    for i in inz:
        for w in als_lijst(i.get(veld)):
            c[w] += 1
    return c


def label(veld, sleutel):
    return LABELS.get(veld, {}).get(sleutel, sleutel)


def tabel(inz, veld, titel, meerkeuze=False):
    enq, intv = deel(inz, "enquete"), deel(inz, "interview")
    n = len(inz)
    ct, ce, ci = tel(inz, veld), tel(enq, veld), tel(intv, veld)
    orde = ORDES.get(veld) or [k for k, _ in ct.most_common()]
    regels = [f"**{titel}**", "",
              "| Antwoord | Enquête | Interviews | Totaal | Aandeel |", "|---|---|---|---|---|"]
    for s in orde:
        t = ct.get(s, 0)
        pct = f"{round(100 * t / n)}%" if n else "-"
        regels.append(f"| {label(veld, s)} | {ce.get(s, 0)} | {ci.get(s, 0)} | {t} | {pct} |")
    noot = ("meerdere antwoorden mogelijk; aandelen op basis van alle "
            f"{n} deelnemers" if meerkeuze else
            f"beantwoord door {sum(1 for i in inz if als_lijst(i.get(veld)))} van {n}")
    regels.append(f"\n*({noot})*\n")
    return "\n".join(regels)


def bronlabel(i):
    if i["_bron"] == "interview":
        return f"interview {i.get('interviewnummer', '?')}"
    return "enquête"


def open_antwoorden(inz, veld):
    uit = []
    for i in inz:
        w = str(i.get(veld) or "").strip()
        if w:
            profiel = (f"{i.get('sector', 'sector onbekend')}, "
                       f"{i.get('omvang', 'omvang onbekend')}, {bronlabel(i)}")
            uit.append((profiel, w))
    return uit


def citatenblok(antwoorden, leeg):
    if not antwoorden:
        return f"*{leeg}*\n"
    return "\n".join(f'- "{t}" *({p})*' for p, t in antwoorden) + "\n"


def top(c: Counter, veld, k=1):
    return [f"{label(veld, s)} ({a}x)" for s, a in c.most_common(k)]


def genereer(inz):
    enq, intv = deel(inz, "enquete"), deel(inz, "interview")
    n, ne, ni = len(inz), len(enq), len(intv)
    vandaag = date.today().strftime("%d-%m-%Y")

    ai = tel(inz, "ai_gebruik")
    taken = tel(inz, "taken")
    controle = tel(inz, "controle")
    drempel = tel(inz, "drempel")
    waarborgen = tel(inz, "waarborgen")
    regels = tel(inz, "regels_bekend")
    budget = tel(inz, "budget")
    onderst = tel(inz, "ondersteuning")

    gebruikt_ai = ai.get("dagelijks", 0) + ai.get("soms", 0)
    regels_onduidelijk = regels.get("onbekend", 0) + regels.get("gehoord", 0)
    wil_mens = controle.get("alles_vooraf", 0) + controle.get("belangrijk_vooraf", 0)
    betaalt = sum(a for s, a in budget.items() if s not in ("Niets",) and not s.startswith("Dat hangt"))

    gemist = open_antwoorden(inz, "regels_gemist")
    nooit = open_antwoorden(inz, "nooit")
    kans_zorg = open_antwoorden(inz, "kans_zorg")
    toelichting = open_antwoorden(inz, "ai_toelichting")
    aanspr = open_antwoorden(intv, "aansprakelijkheid_opvatting")
    duidelijk = open_antwoorden(inz, "duidelijkheid_overheid")
    spontaan = tel(intv, "regels_spontaan")
    aangereikt = tel(intv, "regels_aangereikt")
    prijsvorm = tel(intv, "prijsvorm")
    zicht = tel(intv, "onvoldoende_zicht")
    gaps = []
    for i in intv:
        for g in als_lijst(i.get("gap_signalen")):
            gaps.append((f"interview {i.get('interviewnummer', '?')}", g))

    weet_niet = []
    for i in inz:
        for veld in ("nooit", "ai_toelichting", "regels_gemist",
                     "aansprakelijkheid_opvatting", "kans_zorg"):
            w = str(i.get(veld) or "").strip().lower()
            if "weet ik niet" in w or "weet niet" == w:
                weet_niet.append((bronlabel(i), veld))

    d = []
    a = d.append
    a("# Concept-whitepaper: Juridische kaders voor agentic AI in het MKB\n")
    a(f"**CONCEPT, automatisch gegenereerd op {vandaag}** uit {ne} enquête-inzendingen "
      f"(inclufy.com/ai-onderzoek) en {ni} gecodeerde bedrijfsinterviews "
      "(Interviewvragenlijst v2, ingevoerd via interview_invoer_template.json). "
      "Beide bronnen zijn gecodeerd op dezelfde uitkomstenset (Analysekader) en "
      "worden in de tabellen naast elkaar en opgeteld getoond. Automatisch "
      "gegenereerde conclusies en aanbevelingen zijn voorstellen; de blokken "
      "[DUIDING DOOR ANALIST] vullen Amin (vraag 1 t/m 4), Ayah (5 t/m 8) en "
      "Reda (9 t/m 12) met context, voorbeelden en citaten uit hun interviews. "
      "De hoofdonderzoeker valideert het geheel vóór enige publicatie.\n")
    a("Onderzoeksproject \"Haalbaarheid AI PM+Marketing\", MIT Haalbaarheid, provincie "
      "Flevoland, zaaknummer 28436. Mede mogelijk gemaakt door een subsidie van de "
      "provincie Flevoland.\n")

    a("## 1. Inleiding en methode\n")
    a(f"Deelnemers: {n} totaal ({ne} enquête, {ni} interviews). Interviews van "
      "15 tot 21 bedrijven gepland; de enquête loopt door tot het einde van de "
      "veldwerkperiode, waarna dit concept opnieuw wordt gegenereerd.\n")
    a(tabel(inz, "sector", "Spreiding naar sector"))
    a(tabel(inz, "omvang", "Spreiding naar bedrijfsomvang"))
    a(tabel(inz, "regio", "Spreiding naar regio"))
    if intv:
        kaart = sum(1 for i in intv if i.get("voorbeeldkaart_gebruikt"))
        a(f"Methodenotities interviews: voorbeeldkaart gebruikt bij {kaart} van de {ni}; "
          "blokken met vinkje \"onvoldoende zicht\": "
          + (", ".join(f"{label('onvoldoende_zicht', s)} ({c}x)" for s, c in zicht.items()) or "geen") + ".\n")

    a("## 2. Resultaten\n")
    a("### 2.1 Huidig AI-gebruik\n")
    a(tabel(inz, "ai_gebruik", "Werkt het bedrijf al met AI-tools?"))
    a("Toelichtingen (gebruik of reden om niet te gebruiken):\n")
    a(citatenblok(toelichting, "Geen toelichtingen gegeven."))
    a(DUIDING.format(wie="Amin en Ayah", wat="Context bij het huidige gebruik uit interviewvraag 1 en 5; huidige praktijk (H) scheiden van verwachting (V)."))
    a("### 2.2 Taken: wat mag een AI-agent wel en niet\n")
    a(tabel(inz, "taken", "Taken die men een AI-agent zelfstandig zou laten uitvoeren", meerkeuze=True))
    a("Wat men een AI-agent nooit zelfstandig zou laten doen:\n")
    a(citatenblok(nooit, "Geen open antwoorden."))
    a(DUIDING.format(wie="Amin, Ayah en Reda", wat="Concrete voorbeelden per domein uit interviewvraag 2, 6 en 9; benoem patronen die de tellingen verklaren."))
    a("### 2.3 Menselijke controle en waarborgen\n")
    a(tabel(inz, "controle", "Gewenste mate van menselijke controle"))
    a(tabel(inz, "waarborgen", "Minimaal gewenste waarborgen", meerkeuze=True))
    a(DUIDING.format(wie="Amin", wat="Beslisgrenzen en foutherstel uit interviewvraag 3 en 4; welke beslissingen men expliciet zelf wil blijven nemen."))
    a("### 2.4 Drempels, regelkennis en betalingsbereidheid\n")
    a(tabel(inz, "drempel", "Grootste drempel"))
    a(tabel(inz, "regels_bekend", "Bekendheid met AVG en AI-verordening"))
    if intv:
        a("Regelkennis in de interviews, spontaan genoemd tegenover pas na aanreiken herkend:\n")
        alle_regels = sorted(set(spontaan) | set(aangereikt))
        if alle_regels:
            a("| Regel | Spontaan genoemd | Na aanreiken |\n|---|---|---|")
            for r in alle_regels:
                a(f"| {r} | {spontaan.get(r, 0)} | {aangereikt.get(r, 0)} |")
            a("")
        else:
            a("*Nog geen regels geregistreerd.*\n")
    a(tabel(inz, "budget", "Betalingsbereidheid per maand"))
    if prijsvorm:
        a("Genoemde prijsvorm in de interviews: "
          + ", ".join(f"{s} ({c}x)" for s, c in prijsvorm.most_common()) + ".\n")
    a(tabel(inz, "ondersteuning", "Gewenste externe ondersteuning", meerkeuze=True))
    a(DUIDING.format(wie="Ayah en Reda", wat="Nuance bij drempels, investeringsvoorwaarden en leverancierseisen uit interviewvraag 8, 10, 11 en 12."))
    a("### 2.5 Kansen en zorgen\n")
    a(citatenblok(kans_zorg, "Geen open antwoorden."))
    a(DUIDING.format(wie="Reda", wat="Patronen in kansen en zorgen; koppel aan sector en omvang waar dat betekenisvol is."))

    a("## 3. Conclusies (automatisch voorstel, te valideren)\n")
    if n:
        a(f"- {gebruikt_ai} van de {n} deelnemers ({round(100*gebruikt_ai/n)}%) gebruikt al AI; "
          f"meest genoemde zelfstandige taak: {', '.join(top(taken, 'taken')) or 'geen'}.")
        a(f"- {wil_mens} van de {n} ({round(100*wil_mens/n)}%) wil menselijke goedkeuring vooraf "
          "(volledig of bij belangrijke beslissingen).")
        a(f"- Meest genoemde drempel: {', '.join(top(drempel, 'drempel')) or 'geen'}; "
          f"meest gevraagde waarborg: {', '.join(top(waarborgen, 'waarborgen')) or 'geen'}.")
        a(f"- {regels_onduidelijk} van de {n} ({round(100*regels_onduidelijk/n)}%) kent de relevante "
          "regels niet of weet niet wat ze voor het eigen bedrijf betekenen.")
        if intv and aangereikt:
            a("- In de interviews werden regels vaker pas na aanreiken herkend dan spontaan "
          "genoemd; dat wijst op een voorlichtingsgap eerder dan bewuste afweging.")
        a(f"- {betaalt} van de {n} ({round(100*betaalt/n)}%) noemt een concreet maandbedrag boven nul.\n")
    a(DUIDING.format(wie="hoofdonderzoeker", wat="Valideer, schrap of herformuleer; benoem per conclusie het aantal dragende deelnemers en noem opvallende verschillen tussen enquête en interviews."))

    a("## 4. Aanbevelingen (automatisch voorstel, te valideren)\n")
    if waarborgen.get("goedkeuring", 0) * 2 >= max(n, 1):
        a("- Ontwerp agentic AI voor het MKB standaard met menselijke goedkeuring op belangrijke acties.")
    if regels_onduidelijk * 2 >= max(n, 1):
        a("- Zet in op praktische voorlichting over AVG en AI-verordening voor het MKB.")
    if onderst:
        a(f"- Richt ondersteuning op wat bedrijven zelf vragen: {', '.join(top(onderst, 'ondersteuning', 3))}.")
    if drempel:
        a(f"- Adresseer de grootste drempel ({', '.join(top(drempel, 'drempel'))}) expliciet in product en communicatie.\n")
    a(DUIDING.format(wie="hoofdonderzoeker", wat="Splits naar MKB-bedrijven, leveranciers en ondersteunende partijen; onderbouw vanuit hoofdstuk 2 en 3."))

    a("## 5. Gaps en risico's\n")
    a("### 5.1 Gap-register uit de interviews\n")
    if gaps:
        a("| Bron | Signaal |\n|---|---|")
        for bron, g in gaps:
            a(f"| {bron} | {g} |")
        a("")
    else:
        a("*Nog geen interview-gap-signalen ingevoerd.*\n")
    a("### 5.2 Gemiste regels en gewenste duidelijkheid\n")
    a(citatenblok(gemist, "Geen open antwoorden; toets in de interviews of regelkennis werkelijk dekkend is."))
    a("Opvattingen over aansprakelijkheid (O, geen juridische conclusies):\n")
    a(citatenblok(aanspr, "Nog geen interviewdata."))
    a("Gewenste duidelijkheid vanuit overheid of wetgeving:\n")
    a(citatenblok(duidelijk, "Nog geen antwoorden."))
    a("### 5.3 Automatische signalen\n")
    if n:
        a(f"- Regelkennis-gap: {regels_onduidelijk} van de {n} kent AVG/AI-verordening niet of onvoldoende.")
        a(f"- Aansprakelijkheid als grootste drempel: {drempel.get('aansprakelijkheid', 0)} van de {n}; "
          f"privacy/AVG: {drempel.get('privacy', 0)}; vertrouwen/uitlegbaarheid: {drempel.get('vertrouwen', 0)}.")
        a(f"- Letterlijke \"weet ik niet\"-antwoorden: {len(weet_niet)}"
          + (" (" + ", ".join(f"{b}: {v}" for b, v in weet_niet) + ")" if weet_niet else "") + ".\n")
    a(DUIDING.format(wie="hoofdonderzoeker", wat="Dedupliceer 5.1 t/m 5.3 en duid elk juridisch signaal in het bureauonderzoek: voorlichtingsgap (kader bestaat maar is onbekend) of wetgevingsgap (kader ontbreekt of is niet eenduidig)."))

    a("## 6. Vervolgonderzoek\n")
    a("Automatische aanzetten op basis van de signalen hierboven:\n")
    if regels_onduidelijk * 2 >= max(n, 1):
        a("- Juridisch vervolgonderzoek: welke verplichtingen uit de AI-verordening raken "
          "MKB-gebruikers van agentic AI concreet, en waar is de uitleg voor kleine "
          "organisaties niet eenduidig.")
    if drempel.get("aansprakelijkheid", 0) or aanspr:
        a("- Aansprakelijkheidsonderzoek: verdeling tussen gebruiker en leverancier bij "
          "zelfstandig handelende agents; volstaan bestaande kaders voor het MKB.")
    a("- Vervolgmeting: herhaal de enquête na publicatie van de whitepaper om verschuiving "
      "in regelkennis en adoptie te meten.\n")
    a(DUIDING.format(wie="hoofdonderzoeker", wat="Formuleer per gap uit hoofdstuk 5 één onderzoeksvraag met beoogde methode en de juridische kaders of wetgeving die duiding vragen."))

    a("---\n*Gegenereerd met verwerk_enquete.py (MIT-28436). Persoonsgegevens worden bij "
      "het inlezen verwijderd. Open antwoorden en citaten vóór publicatie controleren op "
      "herleidbaarheid; citeren alleen bij vastgelegde toestemming (veld citaat_toestemming).*")
    return "\n".join(d)


def main():
    argv = sys.argv[1:]
    if not argv:
        print(__doc__)
        sys.exit(1)
    uitvoer = None
    invoer = []
    for arg in argv:
        if arg.endswith(".md"):
            uitvoer = Path(arg)
        else:
            invoer.append(arg)
    if not invoer:
        print("Geen invoerbestanden opgegeven.")
        sys.exit(1)
    inzendingen = lees_inzendingen(invoer)
    if not inzendingen:
        print("Geen inzendingen gevonden.")
        sys.exit(1)
    if uitvoer is None:
        uitvoer = Path(f"Concept_Whitepaper_MIT_28436_{date.today().isoformat()}.md")
    uitvoer.write_text(genereer(inzendingen), encoding="utf-8")
    ne = sum(1 for i in inzendingen if i["_bron"] == "enquete")
    ni = len(inzendingen) - ne
    print(f"{ne} enquête-inzendingen en {ni} interviews verwerkt -> {uitvoer}")


if __name__ == "__main__":
    main()
