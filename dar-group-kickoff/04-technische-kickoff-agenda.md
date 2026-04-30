# Technische Kickoff Agenda — Morgen

> Eén-op-één met sales rep van Dar Group. **60–90 minuten. Operationeel, geen commercials.**
> Doel: pilot starten + intel verzamelen voor het Said-gesprek overmorgen.

---

## 1. Kennismaking en context (10 min)

- Wie zit er, wat zijn jullie rollen.
- Scope vandaag: **technische implementatie**.
- Expliciete framing:
  > *"Vandaag focussen we op de technische implementatie. De bredere partnership en JV-discussies zijn lopende trajecten op directieniveau die we apart voortzetten."*

---

## 2. Doel van de pilot (10 min)

- Wat moet aan einde implementatie werken: **finance core** (GL, AP, AR, banking, TVA).
- Welke users en rollen.
- Definitie van "go-live" voor Dar Group.
- Succes-criteria voor pilot (suggestie: maandafsluiting in systeem binnen 90 dagen, TVA-declaratie gegenereerd uit systeem).

---

## 3. Technische scope (20 min)

### On-prem deployment
- Linux Ubuntu Server 22.04 LTS
- Minimum: 8 cores, 16 GB RAM, 500 GB SSD
- Verifieer: hardware aanwezig of besteld?

### Netwerktoegang voor jou
- **Tailscale** aanbevelen — secure, makkelijk, behoudt hun gevoel van controle.
- Alternatief: SSH via vaste IP, of VPN naar hun netwerk.

### Outbound internet
- Voor AI-features (OpenAI). Optie: zij leveren eigen API-key.
- Voor Docker pulls (updates).
- Voor licentie-validatie.

### Backups
- Postgres dumps + file storage + configuratie.
- Voorstel: jij levert backup-script dagelijks naar hun storage; zij zorgen voor offsite kopie.

### Updates
- Maandelijks via `docker compose pull`.
- Security patches direct.
- Schriftelijk vastleggen wie verantwoordelijk is.

### Monitoring
- Health-check endpoint die jij kunt zien.
- Anders weet je pas dat het systeem down is als de accountant boos belt.

### Security
- SSL/TLS setup, firewall, OS-patches.
- Verantwoordelijkheid scheiden: hun IT voor netwerk/OS, jij voor applicatie-stack.

---

## 4. Data en configuratie (15 min)

- **CoA mapping** naar CGNC (Plan Comptable Marocain).
- **TVA setup**: 20% standaard, reduced rates, retenue à la source.
- **Bank-integraties**: welke banken? (Attijariwafa, BMCE/BoA, BCP, SGMB).
- **Bestaande data**: wat migreren, wat vanaf nul.
- **Openingsbalans**: aanleverdatum.

---

## 5. Planning en milestones (15 min)

| Week | Mijlpaal |
|---|---|
| 1–2 | Server setup, installatie, Tailscale verbinding |
| 3–4 | Configuratie, CoA mapping naar CGNC, TVA setup |
| 5–6 | Data migratie, openingsbalans, eerste tests |
| 7–8 | User training, parallel run met huidig systeem |
| 9–12 | Go-live, stabilisatie, eerste maandafsluiting |

---

## 6. Communicatie en cadans (10 min)

- **Wekelijkse standup** (30 min, video).
- **Tweewekelijkse stuurgroep** (kort, alleen besluiten, met Said).
- **ProjeXtPal-instantie** voor de implementatie zelf — meteen demo van het product.
- **Dagelijkse contactpersoon** aan hun kant?

---

## 7. Volgende stappen (5 min)

- Wie levert wat, wanneer.
- Installatie-datum vastleggen.
- Volgende sessie inplannen.
- Schriftelijke samenvatting volgt vanavond/morgen.

---

## Extra: luistervragen voor het Said-gesprek overmorgen

Stel deze losjes tijdens of na de technische sessie. **Niet als interview — als natuurlijke nieuwsgierigheid.**

- *"Hoeveel klanten bedient Dar Group nu actief? In welke segmenten?"*
- *"Wie zit er in jullie delivery- en consulting-team? Hoeveel mensen, welke achtergrond?"*
- *"Wat zien jullie als de grootste pijn bij jullie klanten op finance/ERP-gebied?"*
- *"Hoe positioneert Dar Group zich in de markt — premium, mid-market, breed?"*
- *"Wat heeft Said gezegd over wat hij wil bereiken met deze samenwerking?"*

**Sluit af met:**
> *"Ik zit overmorgen met Said. Is er iets wat hij belangrijk vindt dat ik vooraf zou moeten weten?"*

---

## Als commerciële vragen komen

De sales rep zal mogelijk vragen wat het kost, wanneer ze kunnen verkopen, hoe partnership werkt. Antwoord consistent:

> *"Goede vraag, en daar werken we momenteel aan op directieniveau. Said en ik nemen dat overmorgen verder op. Vandaag focus ik op het technisch zo goed mogelijk neerzetten — dan weten we straks ook waar we het over hebben."*

---

## Wat te NIET zeggen

- Geen prijzen voor toekomstige klanten
- Geen partnership-percentages of commissies
- Geen toezeggingen over wanneer ze kunnen verkopen
- Geen details over investeerder
- Geen termijnen voor JV-formalisatie

---

## Eindcheck

- [ ] Tailscale-account klaar voor uitnodiging?
- [ ] Hardware requirements lijst geprint of digitaal beschikbaar?
- [ ] On-prem deployment runbook bij de hand?
- [ ] Backup-script klaar om te delen?
- [ ] ProjeXtPal-instantie pre-created met Dar Group logo?
- [ ] Notitieboek voor luister-antwoorden?
