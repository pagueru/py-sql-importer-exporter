--20250307-adhoc-generation_inscricoes_meio_de_funil
SELECT CAST(AdAgency_ADDB.DBO.fc_hash_sha256(EMAIL) AS NVARCHAR(255)) AS [external_id],
	   CAST(EMAIL AS NVARCHAR(255)) AS [email],
	   CAST(PRIMEIRO_NOME AS NVARCHAR(255)) AS [first_name],
	   CAST('Bora Ze' AS NVARCHAR(255)) AS [origem]
  FROM Ambev_001_DBM..TMP_BASE_EMKT_GENERATION_INSCRICOES_MEIO_DE_FUNIL_20250307
