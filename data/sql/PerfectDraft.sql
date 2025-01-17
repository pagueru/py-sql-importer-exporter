--20240930-adhoc-newbacon-retencao-cashback
SELECT CAST(EMAIL AS NVARCHAR(255)) AS email,
       CAST(PRIMEIRO_NOME AS NVARCHAR(255)) AS nome,
       CAST(HASH_CLIENTE AS NVARCHAR(255)) AS hash_cliente,
       CAST(SALDO_ATUAL AS nvarchar(255)) AS saldo_cashback,
       CAST('20240930-adhoc-newbacon-retencao-cashback' AS NVARCHAR(255)) AS campanha_perfectdraft 
  FROM Ambev_001_DBM..TMP_BASE_EMKT_RETENCAO_CASHBACK_20240930