-- GDELT GKG 2.0: haberlerde anılan yerler (BigQuery, Standard SQL)
-- Dönem: Meta duyuru penceresi, 20 Eylül – 11 Ekim 2022.
-- Seçim: DOC 2.0 anlık görüntüsündeki makale URL'leri (__URL_LIST__) VEYA
--        sayfa başlığı / URL içinde "doppelg(a|ä)nger" geçen makaleler.
-- Önce maliyeti görün:  bq query --dry_run --use_legacy_sql=false < bu_dosya
-- fetch_gdelt_map.py --bigquery bu dosyayı doldurup çalıştırır.
WITH docs AS (
  SELECT DocumentIdentifier AS url, SourceCommonName AS source, V2Locations
  FROM `gdelt-bq.gdeltv2.gkg_partitioned`
  WHERE _PARTITIONTIME >= TIMESTAMP('2022-09-20') AND _PARTITIONTIME < TIMESTAMP('2022-10-12')
    AND (
      DocumentIdentifier IN UNNEST(__URL_LIST__)
      OR REGEXP_CONTAINS(LOWER(DocumentIdentifier), r'doppelg(a|ä|ae)nger')
      OR REGEXP_CONTAINS(LOWER(Extras), r'<page_title>[^<]*doppelg(a|ä|ae)nger')
    )
),
loc AS (
  SELECT url, SPLIT(block, '#') AS p
  FROM docs, UNNEST(SPLIT(V2Locations, ';')) AS block
  WHERE block != ''
)
SELECT
  p[SAFE_OFFSET(1)] AS name,
  p[SAFE_OFFSET(2)] AS country_code,
  CAST(p[SAFE_OFFSET(0)] AS INT64) AS location_type,
  ROUND(SAFE_CAST(p[SAFE_OFFSET(5)] AS FLOAT64), 3) AS lat,
  ROUND(SAFE_CAST(p[SAFE_OFFSET(6)] AS FLOAT64), 3) AS lon,
  COUNT(DISTINCT url) AS articles
FROM loc
WHERE SAFE_CAST(p[SAFE_OFFSET(5)] AS FLOAT64) IS NOT NULL
GROUP BY name, country_code, location_type, lat, lon
HAVING articles >= 1
ORDER BY articles DESC
LIMIT 400;
