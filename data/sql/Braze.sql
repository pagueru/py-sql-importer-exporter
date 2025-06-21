--20250428-adhoc-newbacon-disparo_generation
SELECT CAST(AdAgency_ADDB.DBO.fc_hash_sha256(EMAIL) AS NVARCHAR(255)) AS [external_id],
	   CAST(EMAIL AS NVARCHAR(255)) AS [email],
	   CAST(PRIMEIRO_NOME AS NVARCHAR(255)) AS [first_name],
	   CAST('Bora Ze' AS NVARCHAR(255)) AS [origem],
       CAST(HASH_CLIENTE AS NVARCHAR(255)) AS [hash_cliente]
  FROM Ambev_001_DBM..TMP_BASE_EMKT_DISPARO_GENERATION_20250424
