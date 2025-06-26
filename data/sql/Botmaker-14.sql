--1-20250625_adhoc_wpp_relacionamento_incentivo_cadastro_NEWBACON
SELECT CAST(CONCAT('55',CELULAR) AS NVARCHAR(20)) AS phone
      ,CAST(PRIMEIRO_NOME AS NVARCHAR(20)) AS chicoFirstName
  FROM Unilever_000_DBM.dbo.[20250625_adhoc_wpp_relacionamento_incentivo_cadastro]
 WHERE ORIGEM LIKE '%CONTROLE%'
   AND CELULAR IN ('11991371931','18996698725','11998055353')

--1-20250625_adhoc_wpp_relacionamento_incentivo_cadastro_CLIENTE
SELECT CAST(CONCAT('55',CELULAR) AS NVARCHAR(20)) AS phone
      ,CAST(PRIMEIRO_NOME AS NVARCHAR(20)) AS chicoFirstName
  FROM Unilever_000_DBM.dbo.[20250625_adhoc_wpp_relacionamento_incentivo_cadastro]
 WHERE ORIGEM LIKE '%CONTROLE%'
   AND CELULAR IN ('11991371931','18996698725','11998055353'
                  ,'38998310055','11945790149','11964920611')

--1-20250625_adhoc_wpp_relacionamento_incentivo_cadastro_FINAL
SELECT CAST(CONCAT('55',CELULAR) AS NVARCHAR(20)) AS phone
      ,CAST(PRIMEIRO_NOME AS NVARCHAR(20)) AS chicoFirstName
  FROM Unilever_000_DBM.dbo.[20250625_adhoc_wpp_relacionamento_incentivo_cadastro]
