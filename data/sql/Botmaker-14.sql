--1-20250414-adhoc-wpp-receitas_produtos_pascoa_NEWBACON
SELECT CAST(CONCAT('55',CELULAR) AS NVARCHAR(20)) AS phone
	  ,CAST(PRIMEIRO_NOME AS NVARCHAR(20)) AS chicoFirstName
	  ,[HASH] AS hashSMS
	  ,[IMAGE URL]
  FROM Unilever_000_DBM.dbo.[20250414-adhoc-wpp-receitas_produtos_pascoa]
 WHERE ORIGEM LIKE '%CONTROLE%'
   AND CELULAR IN ('11991371931','18996698725','11998055353')

--1-20250414-adhoc-wpp-receitas_produtos_pascoa_CLIENTE
SELECT CAST(CONCAT('55',CELULAR) AS NVARCHAR(20)) AS phone
	  ,CAST(PRIMEIRO_NOME AS NVARCHAR(20)) AS chicoFirstName
	  ,[HASH] AS hashSMS
	  ,[IMAGE URL]
  FROM Unilever_000_DBM.dbo.[20250414-adhoc-wpp-receitas_produtos_pascoa]
 WHERE ORIGEM LIKE '%CONTROLE%'
   AND CELULAR IN ('11991371931','18996698725','11998055353'
				  ,'38998310055','11964920611','11945790149')

--1-20250414-adhoc-wpp-receitas_produtos_pascoa_FINAL
SELECT CAST(CONCAT('55',CELULAR) AS NVARCHAR(20)) AS phone
	  ,CAST(PRIMEIRO_NOME AS NVARCHAR(20)) AS chicoFirstName
	  ,[HASH] AS hashSMS
	  ,[IMAGE URL]
  FROM Unilever_000_DBM.dbo.[20250414-adhoc-wpp-receitas_produtos_pascoa]
