--20250618-adhoc-newbacon-wpp_feriado_corpus
SELECT AdAgency_ADDB.dbo.fc_hash_sha2_256(EMAIL) AS [external_id]
  FROM Ambev_001_DBM.dbo.TMP_BASE_WHATS_FERIADO_CORPUS_20250618
