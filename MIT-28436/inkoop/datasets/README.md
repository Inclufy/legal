# Synthetische datasets — technisch haalbaarheidsonderzoek MIT-28436

Gegenereerd op 7 oktober 2026, reproduceerbaar met `genereer_datasets.py` (vaste seed 28436).
Bewust beperkte datavolumes: dit is typerend voor het MKB en precies wat het onderzoek toetst.
De specialist mag de sets beoordelen, bewerken, aanvullen of gemotiveerd vervangen (zie casusbeschrijving, deel A).

## Case 1 — 90-dagen cashflowvoorspelling

| Bestand | Inhoud |
|---|---|
| `case1_bedrijven.csv` | 12 gesimuleerde MKB-profielen: sector, omvang (micro/klein/middel), basisomzet p/m, seizoensamplitude, aandeel projectmatige facturatie, betaaltermijn, kans op late betaling, vaste lasten en personeelskosten p/m |
| `case1_cashflow_weekly.csv` | 130 weken (±30 maanden) per bedrijf: inkomsten, uitgaven, netto cashflow, kaspositie (1.560 regels) |

**Ingebouwde realistische structuur:** seizoenseffect per sector (bouw/installatie uit fase met de rest), lichte groeitrend met ruis, lompe projectfacturen bovenop reguliere omzet, wanbetalingsweken, vakantiegeld in mei, incidentele uitgaven.

**Beoogd gebruik:** voorspel per bedrijf de laatste 13 weken (≈90 dagen) op basis van de voorgaande historie; train/test-splitsing in de tijd, MAPE over de horizon, vergelijking met naïeve en seizoensbaseline. Exacte opzet vast te stellen bij de intake.

## Case 2 — next-best-action-aanbevelingen marketing

| Bestand | Inhoud |
|---|---|
| `case2_bedrijven.csv` | 15 gesimuleerde MKB-profielen: sector, omvang, marketingbudget p/m |
| `case2_campagnes.csv` | 800 campagnes over 24 maanden: kanaal (7), segment (4), doel, budget, duur, bereik, kliks, conversies, omzet |
| `case2_ground_truth_NIET_DELEN_met_model.csv` | De verborgen affiniteitsstructuur per bedrijf (top-8 kanaal×segment-combinaties) waaruit de uitkomsten zijn gegenereerd — **uitsluitend voor evaluatie (precision@5), nooit als input voor het model** |

**Ingebouwde realistische structuur:** per bedrijf een verborgen affiniteit per kanaal×segment-combinatie (sector- en omvangsafhankelijk, bv. e-mail werkt op bestaande klanten en niet op koude prospects; events werken in bouw/industrie), die doorwerkt in CTR, conversie en omzet — met ruime ruis, zodat het signaal gevonden moet worden.

**Beoogd gebruik:** laat het model per bedrijf een top-5 van kanaal×segment-acties aanbevelen op basis van de campagnehistorie; meet precision@5 tegen de ground truth. De ground truth blijft bij de evaluator (hoofdonderzoeker of gescheiden evaluatiestap).

## Integriteit

- Volledig synthetisch: geen echte bedrijfs-, klant- of persoonsgegevens.
- Generatorscript wordt meegeleverd; de specialist kan de generatie controleren en mag de generatieaannames bekritiseren of aanpassen (gemotiveerd, vastgelegd in het onderzoeksplan).
- Omvang en ruis zijn bewust zo gekozen dat de onderzoeksvraag ("werkt dit op beperkte MKB-data?") echt getoetst wordt — de drempels zijn niet gegarandeerd haalbaar.
