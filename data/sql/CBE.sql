--20250701-adhoc-newbacon-wpp_ativos_com_time
SELECT CAST(AdAgency_ADDB.dbo.fc_hash_sha2_256(EMAIL) AS NVARCHAR(255)) AS external_id
  FROM Ambev_001_DBM.dbo.TMP_BASE_WHATS_ATIVOS_COM_TIME_20250701
 WHERE EMAIL IS NOT NULL
