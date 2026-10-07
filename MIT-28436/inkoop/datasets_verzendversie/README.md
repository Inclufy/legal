# Synthetische datasets — technisch haalbaarheidsonderzoek MIT-28436 (kandidaatversie)

Gegenereerd op 7 oktober 2026. Bewust beperkte datavolumes: dit is typerend voor het MKB
en precies wat het onderzoek toetst. De specialist mag de sets beoordelen, bewerken,
aanvullen of gemotiveerd vervangen (zie casusbeschrijving, deel A).

## Case 1 — 90-dagen cashflowvoorspelling

| Bestand | Inhoud |
|---|---|
| `case1_bedrijven.csv` | 12 gesimuleerde MKB-profielen: sector, omvang, basisomzet p/m, seizoensamplitude, aandeel projectmatige facturatie, betaaltermijn, kans op late betaling, vaste lasten en personeelskosten p/m |
| `case1_cashflow_weekly.csv` | 130 weken (±30 maanden) per bedrijf: inkomsten, uitgaven, netto cashflow, kaspositie (1.560 regels) |

De reeksen bevatten realistische structuur (seizoenseffecten, projectmatige pieken,
betalingsgedrag, incidentele uitgaven) met ruis. Beoogd gebruik: voorspel per bedrijf de
laatste 13 weken (±90 dagen) op basis van de voorgaande historie; train/test-splitsing in
de tijd, MAPE over de horizon, vergelijking met naïeve en seizoensbaseline. Exacte opzet
wordt bij de intake vastgesteld.

## Case 2 — next-best-action-aanbevelingen marketing

| Bestand | Inhoud |
|---|---|
| `case2_bedrijven.csv` | 15 gesimuleerde MKB-profielen: sector, omvang, marketingbudget p/m |
| `case2_campagnes.csv` | 800 campagnes over 24 maanden: kanaal (7), segment (4), doel, budget, duur, bereik, kliks, conversies, omzet |

In de uitkomsten is per bedrijf een verborgen voorkeursstructuur verwerkt (welke
kanaal×segment-combinaties werken), met ruime ruis. Beoogd gebruik: laat het model per
bedrijf een top-5 van kanaal×segment-acties aanbevelen op basis van de campagnehistorie.
De evaluatie (precision@5) vindt plaats tegen een referentie die bij de opdrachtgever
berust en na gunning in de evaluatieprocedure wordt vastgelegd — deze maakt bewust geen
deel uit van dit pakket.

## Integriteit

- Volledig synthetisch: geen echte bedrijfs-, klant- of persoonsgegevens.
- Het generatiescript en de evaluatiereferentie worden na gunning gedeeld conform de
  afspraken in het technisch onderzoeksplan.
- Omvang en ruis zijn bewust zo gekozen dat de onderzoeksvraag ("werkt dit op beperkte
  MKB-data?") echt getoetst wordt — de drempels zijn niet gegarandeerd haalbaar.
