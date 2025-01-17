--20250116-adhoc-newbacon-repique_feriado_rio_de_janeiro_clientes
SELECT CAST(ISNULL(NULLIF(first_name,''),'Olá') AS NVARCHAR(255)) AS first_name,
       CAST(external_id AS NVARCHAR(255)) AS external_id,
	   CAST(email  AS NVARCHAR(255)) AS email
  FROM Ambev_001_DBM..TMP_BASE_EMKT_FERIADO_RIO_DE_JANEIRO_20250116
 WHERE segment = '20250116-adhoc-newbacon-repique_feriado_rio_de_janeiro_clientes'

--20250116-adhoc-newbacon-repique_feriado_rio_de_janeiro_leads
SELECT CAST(ISNULL(NULLIF(first_name,''),'Olá') AS NVARCHAR(255)) AS first_name,
       CAST(external_id AS NVARCHAR(255)) AS external_id,
	   CAST(email  AS NVARCHAR(255)) AS email
  FROM Ambev_001_DBM..TMP_BASE_EMKT_FERIADO_RIO_DE_JANEIRO_20250116
 WHERE segment = '20250116-adhoc-newbacon-repique_feriado_rio_de_janeiro_leads'
