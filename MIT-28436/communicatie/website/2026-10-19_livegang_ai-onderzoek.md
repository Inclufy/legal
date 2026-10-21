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

## Update 19 oktober 2026, ca. 21:45: enquête v2 en partnersectie live

Tweede deploy dezelfde avond: GitHub PR #27 (squash-commit `79e8ace`, CI groen) als cherry-pick `4d52787` op GitLab-`main` gezet; pipeline #2964760889 (validate, build_and_push, deploy_to_server) volledig geslaagd. Wijzigingen: de tien enquêtevragen gelijkgetrokken met Interviewvragenlijst v2 volgens het Analysekader (profielvragen apart; nieuw: menselijke controle, bekendheid AVG/AI-verordening met open veld gemiste regels, externe ondersteuning, grootste kans en zorg), en de partnersectie toont Provincie Flevoland, House of Digital, AI & Partners en ROC van Amsterdam en Flevoland (logokaarten; naamweergave zolang de logobestanden nog niet zijn geplaatst).

## Update 19 oktober 2026, ca. 22:15: interviewinvoer, mobiele fix en footer

Derde en vierde wijziging dezelfde avond, beide met groene pipeline gedeployed:

- **Besloten interviewinvoer** (GitHub PR #29, op GitLab als `b5f512f`): formulier voor het onderzoeksteam op /ai-onderzoek?invoer=interview (niet publiek gelinkt) voor gecodeerde interviewuitkomsten in de categorieën van het Analysekader; inzendingen dragen type "interview" zodat verwerking de bronnen gescheiden houdt. Bijbehorende werkinstructie voor het team: `MIT-28436/onderzoek/Werkinstructie_Interviews_Invoer_MIT_28436.pdf`.
- **Mobiele aanvink-fix en footer** (GitHub PR #30, op GitLab als `9645be2`): checkboxen en keuzerondjes 21px met de hele antwoordregel als tikvlak (opgelost: niet-aanvinkbare opties op telefoons, kritisch voor QR-verkeer); formele projectregel uit de footer, de verplichte provincievermelding blijft. PR #30 is gemerged met groene Validate-check (TypeScript, build, tests); de adviserende SonarCloud-check stond op "Maintainability B op nieuwe code" en is genoteerd voor latere opschoning. Aanvinken op telefoon na deploy door S. Loukile bevestigd.

## Update 20 en 21 oktober 2026: vraagverbetering, interviewplanning en agenda

Reeks wijzigingen, elk via GitHub-PR met validatie en daarna via de GitLab-pipeline gedeployed (vanaf 21 oktober met lokale validatie als poort, omdat de GitHub Actions-runners faalden zonder één stap uit te voeren; de blokkerende GitLab-validate bleef de productiepoort):

- **Scherpere vraagstelling** enquête (PR #33) en Interviewvragenlijst v2.1: expliciete benoeming in elke vraag, definitie van AI-agent boven de vragen, AVG als privacywet toegelicht.
- **Vraag 5 meerkeuze** (PR #34) met optie "Niets, we zouden zo kunnen starten", na feedback eerste tester.
- **Interviewplanning in de enquête** (PR #37): bij interviewbereidheid kiest de respondent vormvoorkeur (online, op locatie, geen voorkeur) en tot drie voorkeursmomenten (datum plus dagdeel).
- **Interview ook bij anonieme deelname** (PR #40): alleen een e-mailadres voor het plannen, los van de antwoorden opgeslagen; getest en werkend bevonden op 21 oktober.
- **Provincielogo** op de partnerkaart (PR #38) en in de footer naast de subsidievermelding (PR #39); partnersectie toont op verzoek alleen de provincie.
- **Backend**: mailnotificatie per inzending naar de hoofdonderzoeker (met vlag "WIL EEN INTERVIEW"), interviewagenda in de admin (Contactaanmeldingen met voorkeuren, interviewer-koppeling en status), token-beveiligd export-endpoint voor het concept-whitepaper, en beheerdersaccounts met beperkte rechten voor Amin, Ayah en Reda (groep Onderzoeksteam: alleen de agenda plus leesrechten op inzendingen).

## Context distributie

Pagina ondersteunt de wervingscampagne: LinkedIn-post (zie `2026-09-29_LinkedIn_post_onderzoek.md`), digitale flyer naar VBA Almere (400 ondernemers) en het ondernemersontbijt van woensdag 21 oktober 2026, 7:45 uur, Ondernemersplein Almere.
