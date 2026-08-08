{{ config(materialized='table') }}


-- FEATURE MODEL
-- Skapar feature‑tabellen som används av Databricks under ML‑träningen.
-- Hämtar staging‑datan, beräknar ratio‑features, binära flaggor osv...
-- Gör labels "läsbara" av ML modell


-- 1. Hämta staging‑datan från dbt-modellen 'staging_ctu_iot'
with base as (
    select *
    from {{ ref('staging_ctu_iot') }}
)

-- 2. Beräkna features och returnera ML‑redo dataset
select
    -- Unik session‑identifierare (vem/enhet)
    uid,

    -- Timestamp (när)
    ts,

    -- Grundläggande trafik‑features
    duration,
    orig_bytes,
    resp_bytes,
    orig_pkts,
    resp_pkts,
    orig_ip_bytes,
    resp_ip_bytes,

    -- Ratio mellan bytes skickade och mottagna
    -- Om resp_bytes är 0 eller null → returnera null för att undvika division by zero
    case 
        when resp_bytes = 0 or resp_bytes is null then null
        else orig_bytes / resp_bytes
    end as bytes_ratio,

    -- Ratio mellan paket skickade och mottagna
    case 
        when resp_pkts = 0 or resp_pkts is null then null
        else orig_pkts / resp_pkts
    end as pkts_ratio,

    -- Flagga: är origin‑IP lokal?
    case when local_orig = '-' then 0 else 1 end as is_local_orig,

    -- Flagga: är response‑IP lokal?
    case when local_resp = '-' then 0 else 1 end as is_local_resp,

    -- Protokoll och metadata
    protocol,
    service,
    conn_state,

    -- Binär label för ML-modellerna
    -- Alla varianter av "malicious" → 1
    -- Annars → 0
    case 
        when label ilike '%malicious%' then 1
        else 0
    end as is_malicious,

    -- Mer detaljerad label (används för analys, inte ML)
    detailed_label

from base
