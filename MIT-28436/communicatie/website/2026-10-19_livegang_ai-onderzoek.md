# Livegang onderzoekspagina inclufy.com/ai-onderzoek

**Project:** MIT Haalbaarheid, zaaknummer 28436 ("Haalbaarheid AI PM+Marketing")
**Datum livegang:** maandag 19 oktober 2026, ca. 17:00 uur
**URL:** https://inclufy.com/ai-onderzoek

## Wat er live staat

Publiekspagina met achtergrond van het onderzoek, partnervermelding (provincie Flevoland, House of Digital, ROC van Amsterdam | Flevoland, kennispartners AI-governance & machine learning), de aankondiging van de vrij toegankelijke whitepaper en de tweestaps-enquête (stap 1: deelname met gegevens of anoniem, whitepaper-aanmelding, interviewbereidheid "een half uur"; stap 2: tien inhoudelijke vragen). De footer draagt de vermelding "Mede mogelijk gemaakt door een subsidie van de provincie Flevoland" en de formele projectnaam.

De QR-code in de flyer, het pitchdeck en de LinkedIn-visual verwijst naar deze URL (zie `QR_inclufy_ai-onderzoek.png` in deze map).

## Technische route (reproduceerbaar)

1. Pagina ontwikkeld als React-route in de websitecodebase: GitHub `Inclufy/Inclufy-AI-ERP`, pull request #26, na groene CI (Validate: TypeScript + build + tests; SonarCloud) gesquash-merged naar `main` als commit `9e0589e` (bestanden: `src/pages/marketing/AIOnderzoekPage.tsx` nieuw, route in `src/App.tsx`).
2. Productie deployt vanuit GitLab `inclufy-ai-erp/inclufy-ai-erp-frontend`. Commit `9e0589e` is daar als cherry-pick `83765cd` op `main` gezet (één merge-conflictregel in `src/App.tsx` opgelost: beide routes behouden).
3. GitLab-pijplijn (validate → build_and_push → deploy_to_server) volledig groen; nieuwe frontend automatisch op de productieserver uitgerold.

Archiefversie van de pagina (standalone HTML, zelfde inhoud): `ai-onderzoek-pagina.html` in deze map.

## Openstaand bij livegang

- Formulieropslag: `FORM_ENDPOINT` is nog leeg; inzendingen lopen tijdelijk via de mailto-fallback naar sami@inclufy.com. Koppeling aan een backend (gescheiden opslag van antwoorden en contactgegevens, bewaartermijn uiterlijk maart 2027) volgt.
- Testinzendingen (met gegevens én anoniem) en QR-scan uitgevoerd door S. Loukile na livegang.

## Context distributie

Pagina ondersteunt de wervingscampagne: LinkedIn-post (zie `2026-09-29_LinkedIn_post_onderzoek.md`), digitale flyer naar VBA Almere (400 ondernemers) en het ondernemersontbijt van woensdag 21 oktober 2026, 7:45 uur, Ondernemersplein Almere.
