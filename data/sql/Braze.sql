--20250630-adhoc-newbacon-disparo_futebol_superlitragens_sleepers_churn
SELECT CAST(external_id AS NVARCHAR(255)) AS external_id
  FROM Ambev_001_DBM.dbo.TMP_BASE_EMKT_FUTEBOL_SUPERLITRAGEM_20250627
 WHERE segment = '20250630-adhoc-newbacon-disparo_futebol_superlitragens_sleepers_churn'

--20250630-adhoc-newbacon-disparo_futebol_superlitragens_ativos
SELECT CAST(external_id AS NVARCHAR(255)) AS external_id
  FROM Ambev_001_DBM.dbo.TMP_BASE_EMKT_FUTEBOL_SUPERLITRAGEM_20250627
 WHERE segment = '20250630-adhoc-newbacon-disparo_futebol_superlitragens_ativos'

--20250630-adhoc-newbacon-disparo_futebol_superlitragens_leads
SELECT CAST(external_id AS NVARCHAR(255)) AS external_id
  FROM Ambev_001_DBM.dbo.TMP_BASE_EMKT_FUTEBOL_SUPERLITRAGEM_20250627
 WHERE segment = '20250630-adhoc-newbacon-disparo_futebol_superlitragens_leads'
