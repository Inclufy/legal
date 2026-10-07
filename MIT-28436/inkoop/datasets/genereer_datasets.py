#!/usr/bin/env python3
"""Generator synthetische datasets MIT-28436 — case 1 (cashflow) en case 2 (marketing).
Reproduceerbaar met vaste seed. Bewust beperkte datavolumes: typerend MKB."""
import csv, math, random, os
random.seed(28436)

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'datasets')
os.makedirs(OUT, exist_ok=True)

SECTOREN = ['bouw','installatie','energie','it_diensten','zakelijke_diensten','logistiek','industrie','food']

# ---------------- CASE 1: CASHFLOW ----------------
# 12 gesimuleerde MKB-bedrijven, 30 maanden weekdata (130 weken)
N_BEDRIJVEN1, N_WEKEN = 12, 130

def bedrijf_profiel(i):
    sector = SECTOREN[i % len(SECTOREN)]
    omvang = random.choice(['micro','klein','middel'])
    basis_omzet = {'micro': 9000, 'klein': 30000, 'middel': 90000}[omvang]  # per maand
    return {
        'bedrijf_id': f'B{i+1:02d}', 'sector': sector, 'omvang': omvang,
        'mnd_omzet_basis': basis_omzet,
        'seizoen_amp': round(random.uniform(0.05, 0.35), 2),           # seizoenseffect
        'projectmatig': round(random.uniform(0.1, 0.7), 2),            # aandeel lompe projectfacturen
        'betaaltermijn_dagen': random.choice([14, 30, 30, 45, 60]),
        'late_betaling_kans': round(random.uniform(0.1, 0.45), 2),
        'vaste_lasten_pm': round(basis_omzet * random.uniform(0.35, 0.6)),
        'personeel_pm': round(basis_omzet * random.uniform(0.2, 0.45)),
    }

bedrijven1 = [bedrijf_profiel(i) for i in range(N_BEDRIJVEN1)]
with open(f'{OUT}/case1_bedrijven.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=bedrijven1[0].keys()); w.writeheader(); w.writerows(bedrijven1)

rows = []
for b in bedrijven1:
    kas = b['mnd_omzet_basis'] * random.uniform(0.5, 2.0)  # startsaldo
    for wk in range(N_WEKEN):
        seiz = 1 + b['seizoen_amp'] * math.sin(2*math.pi*(wk % 52)/52 + (1.2 if b['sector'] in ('bouw','installatie') else 0))
        trend = 1 + 0.0015 * wk * random.uniform(0.5, 1.5)
        wkomzet = b['mnd_omzet_basis']/4.33 * seiz * trend
        # inkomsten: mix regulier + projectmatig (lomperig), met betalingsvertraging-ruis
        regulier = wkomzet * (1-b['projectmatig']) * random.uniform(0.75, 1.25)
        project = 0.0
        if random.random() < b['projectmatig']*0.35:  # af en toe een grote projectfactuur betaald
            project = wkomzet * random.uniform(2.0, 6.0)
        if random.random() < b['late_betaling_kans']*0.3:  # wanbetalingsweek
            regulier *= random.uniform(0.2, 0.6)
        inkomsten = regulier + project
        # uitgaven
        uitgaven = (b['vaste_lasten_pm'] + b['personeel_pm'])/4.33 * random.uniform(0.92, 1.08)
        if wk % 52 in (21, 22): uitgaven += b['personeel_pm']/4.33 * 0.96  # vakantiegeld mei
        if random.random() < 0.06: uitgaven += wkomzet * random.uniform(0.5, 2.0)  # incidentele uitgave
        netto = inkomsten - uitgaven
        kas += netto
        rows.append({'bedrijf_id': b['bedrijf_id'], 'week': wk+1,
                     'inkomsten': round(inkomsten,2), 'uitgaven': round(uitgaven,2),
                     'netto_cashflow': round(netto,2), 'kaspositie': round(kas,2)})
with open(f'{OUT}/case1_cashflow_weekly.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
print(f'case 1: {len(bedrijven1)} bedrijven, {len(rows)} weekregels')

# ---------------- CASE 2: MARKETING ----------------
# 15 bedrijven, elk 40-70 campagnes over 24 maanden; verborgen structuur bepaalt wat werkt
N_BEDRIJVEN2 = 15
KANALEN = ['email','social_organisch','social_betaald','zoekmachine_adv','content_seo','event','direct_mail']
SEGMENTEN = ['bestaande_klanten','warme_leads','koude_prospects','churn_risico']
DOELEN = ['leadgen','conversie','retentie','merkbekendheid']

def affiniteit(sector, omvang):
    """Verborgen 'ground truth': welke kanaal/segment-combinaties werken voor dit profiel."""
    aff = {}
    for k in KANALEN:
        for s in SEGMENTEN:
            basis = random.uniform(0.2, 0.8)
            if sector in ('it_diensten','zakelijke_diensten') and k in ('content_seo','zoekmachine_adv'): basis += 0.25
            if sector in ('bouw','installatie','industrie') and k in ('event','direct_mail'): basis += 0.2
            if s == 'bestaande_klanten' and k == 'email': basis += 0.3
            if s == 'koude_prospects' and k == 'email': basis -= 0.25
            if omvang == 'micro' and k == 'social_betaald': basis -= 0.1
            aff[(k, s)] = max(0.05, min(1.0, basis))
    return aff

bedrijven2, camp_rows, truth_rows = [], [], []
cid = 0
for i in range(N_BEDRIJVEN2):
    sector = SECTOREN[(i*3) % len(SECTOREN)]
    omvang = random.choice(['micro','klein','middel'])
    b = {'bedrijf_id': f'M{i+1:02d}', 'sector': sector, 'omvang': omvang,
         'mkt_budget_pm': {'micro':600,'klein':2200,'middel':7500}[omvang]}
    bedrijven2.append(b)
    aff = affiniteit(sector, omvang)
    # ground truth: top-combinaties per bedrijf (voor evaluatie, apart bestand)
    top = sorted(aff.items(), key=lambda kv: -kv[1])[:8]
    for rang, ((k, s), score) in enumerate(top, 1):
        truth_rows.append({'bedrijf_id': b['bedrijf_id'], 'rang': rang, 'kanaal': k, 'segment': s,
                           'affiniteit': round(score, 3)})
    for _ in range(random.randint(40, 70)):
        cid += 1
        k, s = random.choice(KANALEN), random.choice(SEGMENTEN)
        doel = random.choice(DOELEN)
        budget = round(b['mkt_budget_pm'] * random.uniform(0.1, 0.8))
        duur = random.choice([7, 14, 21, 30])
        maand = random.randint(1, 24)
        a = aff[(k, s)]
        bereik = int(budget * random.uniform(8, 20) * (1.2 if k.startswith('social') else 1.0))
        ctr = max(0.001, random.gauss(0.02 + 0.03*a, 0.01))
        kliks = int(bereik * ctr)
        conv_rate = max(0.001, random.gauss(0.01 + 0.06*a, 0.015))
        conversies = max(0, int(kliks * conv_rate + random.gauss(0, 1)))
        omzet = round(conversies * random.uniform(80, 600) * (1.3 if doel=='conversie' else 1.0), 2)
        camp_rows.append({'campagne_id': f'C{cid:04d}', 'bedrijf_id': b['bedrijf_id'], 'maand': maand,
                          'kanaal': k, 'segment': s, 'doel': doel, 'budget_eur': budget,
                          'duur_dagen': duur, 'bereik': bereik, 'kliks': kliks,
                          'conversies': conversies, 'omzet_eur': omzet})
with open(f'{OUT}/case2_bedrijven.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=bedrijven2[0].keys()); w.writeheader(); w.writerows(bedrijven2)
with open(f'{OUT}/case2_campagnes.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=camp_rows[0].keys()); w.writeheader(); w.writerows(camp_rows)
with open(f'{OUT}/case2_ground_truth_NIET_DELEN_met_model.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=truth_rows[0].keys()); w.writeheader(); w.writerows(truth_rows)
print(f'case 2: {len(bedrijven2)} bedrijven, {len(camp_rows)} campagnes, {len(truth_rows)} ground-truth-regels')
