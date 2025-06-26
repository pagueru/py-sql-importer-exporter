--20250625-adhoc-newbacon-wpp_choppback
SELECT AdAgency_ADDB.dbo.fc_hash_sha2_256(EMAIL) AS external_id
  FROM Ambev_001_DBM.dbo.TMP_BASE_WHATS_CHOPPBACK_20250625
