# Projektuppgift 2 (avancerad)


### Beskrivning:

Det här projektet är en end‑to‑end data‑ och maskininlärningspipeline för att upptäcka malware i IoT‑nätverkstrafik. Målet är att skapa en/flera modeller som kan upptäcka malware ENDAST från trafikmönster och inte enhets-identifierande information (sånt som en IP-Adress) samtidigt som jag skapat en pipeline för att automatisera processen. 



# Pipeline:

Alla delar och deras funktion!

## 1. Kaggle — Datainsamling

Datasetet IoT Network Traffic (Malware) hämtas från Kaggle och innehåller rå nätverkstrafik från CTU‑IoT‑miljöer.

- Rådata i CSV‑format

- Innehåller trafikflöden, metadata och malware‑klassificeringar

- Används som grund för hela pipeline

## Snowflake — Databas & Feature‑lagring

Rådatasetet laddas upp till Snowflake och lagras i en RAW‑tabell.

Snowflake används för:

- Lagring av rådata

- Lagring av dbt‑genererade feature‑tabeller

- Central datakälla för Databricks

## dbt Cloud — Data Transformation & Feature Engineering

dbt Cloud ansvarar för att transformera rådata till ett ML‑redo dataset.

Modeller:

- sources.yml — definierar datakällor

- staging.sql — rensar, typkonverterar och normaliserar rådata

- feature_model.sql — skapar ML‑features (ratio‑features, binära       flaggor, labels)

Pipeline:

- dbt run → genererar en feature‑tabell i Snowflake

- Resultatet används direkt av Databricks för modellträning

## 4. Databricks — Modellträning & Dashboard


 Databricks laddar feature‑tabellen från Snowflake och tränar två modeller:

- Random Forest (supervised)

- Isolation Forest (unsupervised)

Databricks utför:

- Feature‑loading

- Modellträning

- KPI‑generering

- ROC‑kurvor, feature importance, confusion matrix

- Skapande av en visuell dashboard

- Export av Slack‑rapport (slack_report.json)

## 5. Lokalt Python‑script — Slack & Grok AI‑integration

Ett lokalt Python‑script tar hand om rapportering och AI‑sammanfattningar.

Scriptet:

- Läser slack_report.json

- Skickar rapporten till Slack

- Kommunicerar med Grok API

- Genererar:

-- AI‑sammanfattning

-- Meta‑sammanfattning

- Skickar båda sammanfattningarna till Slack

## 6. Grok API — AI‑genererade sammanfattningar

Grok AI används för att skapa:

- En sammanfattning av modellernas prestanda

- En meta‑sammanfattning som förklarar resultaten på ett högre abstraktionsplan

Detta ger en automatiserad, AI‑driven analys av ML‑resultaten.

## 7. Slack — Automatiserad rapportering

Slack fungerar som slutdestination för:

- Modellrapport

- KPI‑tabell

- AI‑sammanfattning

- Meta‑sammanfattning

Det gör att hela pipeline kan övervakas och bedömas direkt i Slack.

# Resultat

## Random forest modell
Modellen visa hög precision även om jag tränade den med mindre data, färre träd eller deras djup. Denna höga precision betydde dock inte att modellen var speciellt "bra". Det stämmer att modellen hade hög precision men den hade också ganska många falskt positiva resultat som betyder att modellen flaggade mycket vanlig trafik som "MALICIOUS". Modellen i sig skulle vara effektiv på att fånga trafik innehållande malware men skulle också inkludera mycket vanlig trafik, som skulle kräva en manuell review för att bedöma om trafiken faktiskt är skadlig.

## Isolation forest modell
Isolation modellen var betydligt sämre på att upptäcka malware trafiken liggande i testdatan. Precisionen ligger under förväntan och modellen var opålitligt i sitt omdöme. Detta var dock att förvänta sig med en unsupervised modell. Just därför skulle denna modell inte passa bra för användning som den är och kräver mer träning för att uppnå en bättre standard.
