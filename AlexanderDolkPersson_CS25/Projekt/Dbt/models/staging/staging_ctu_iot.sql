{{ config(materialized='view') }}


-- STAGING MODEL (staging_ctu_iot)
-- Syfte:
--  - Rensa och typkonvertera rådata från Snowflake
--  - Trimma strängar, ersätta tomma värden med NULL
--  - Konvertera numeriska kolumner från text → number
--  - Förbereda datan för feature-modellen och ML-träning


with source as (

    select
        -- Tidsstämpel (när)
        ts,

        -- Unik session-ID från CTU IoT datasetet (vem/enhet)
        uid,

        -- Ursprunglig host och port (port är text i rådata → konverteras)
        id_orig_host,
        try_to_number(nullif(trim(id_orig_port), '')) as id_orig_port,

        -- Svarande host och port
        id_resp_host,
        try_to_number(nullif(trim(id_resp_port), '')) as id_resp_port,

        -- Protokoll och tjänst (t.ex. tcp, udp, dns, http)
        protocol,
        service,

        -- Grundläggande trafikmått (konverteras från text → number)
        try_to_number(nullif(trim(duration), '')) as duration,
        try_to_number(nullif(trim(orig_bytes), '')) as orig_bytes,
        try_to_number(nullif(trim(resp_bytes), '')) as resp_bytes,

        -- Connection state (t.ex. S0, SF, REJ)
        conn_state,

        -- Flagga om IP är lokal eller inte (text i rådata)
        local_orig,
        local_resp,

        -- Missade bytes (kan vara tomma strängar → konverteras)
        try_to_number(nullif(trim(missed_bytes), '')) as missed_bytes,

        -- Historik över TCP-flaggor (text)
        history,

        -- Paket- och IP-byte-räkningar (konverteras från text)
        try_to_number(nullif(trim(orig_pkts), '')) as orig_pkts,
        try_to_number(nullif(trim(orig_ip_bytes), '')) as orig_ip_bytes,
        try_to_number(nullif(trim(resp_pkts), '')) as resp_pkts,
        try_to_number(nullif(trim(resp_ip_bytes), '')) as resp_ip_bytes,

        -- Metadata om tunnlar (text)
        tunnel_parents,

        -- Label och detaljerad label (används senare för ML)
        label,
        detailed_label

    -- Rådata från Snowflake, definierad i sources.yml
    from {{ source('iot_malware', 'RAW') }}
)

-- Returnera den rensade och typkonverterade staging-datan
select * from source
