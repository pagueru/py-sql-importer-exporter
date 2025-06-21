--1-20250620-adhoc-wpp-arraia_de_ofertas_NEWBACON
SELECT CAST(CONCAT('55',CELULAR) AS NVARCHAR(20)) AS phone
      ,CAST(PRIMEIRO_NOME AS NVARCHAR(20)) AS chicoFirstName
      ,CAST([HASH] AS NVARCHAR(5)) AS chicoLinkHash
      ,CAST('https://unilevertrade.s3.dualstack.sa-east-1.amazonaws.com/WhatsApp_Botmaker/000_Trade_UFS_Promos_de_junho_00-00_wpp.png' AS VARCHAR(1000)) AS imageURL
  FROM Unilever_000_DBM.dbo.[20250620-adhoc-wpp-arraia_de_ofertas]
 WHERE ORIGEM LIKE '%CONTROLE%'
   AND CELULAR IN ('11991371931','18996698725')

--1-20250620-adhoc-wpp-arraia_de_ofertas_CLIENTE
SELECT CAST(CONCAT('55',CELULAR) AS NVARCHAR(20)) AS phone
      ,CAST(PRIMEIRO_NOME AS NVARCHAR(20)) AS chicoFirstName
      ,CAST([HASH] AS NVARCHAR(5)) AS chicoLinkHash
      ,CAST('https://unilevertrade.s3.dualstack.sa-east-1.amazonaws.com/WhatsApp_Botmaker/000_Trade_UFS_Promos_de_junho_00-00_wpp.png' AS VARCHAR(1000)) AS imageURL
  FROM Unilever_000_DBM.dbo.[20250620-adhoc-wpp-arraia_de_ofertas]
 WHERE ORIGEM LIKE '%CONTROLE%'
   AND CELULAR IN ('11991371931','18996698725'
                  ,'38998310055','11945790149','11964920611')

--1-20250620-adhoc-wpp-arraia_de_ofertas_FINAL
SELECT CAST(CONCAT('55',CELULAR) AS NVARCHAR(20)) AS phone
      ,CAST(PRIMEIRO_NOME AS NVARCHAR(20)) AS chicoFirstName
      ,CAST([HASH] AS NVARCHAR(5)) AS chicoLinkHash
      ,CAST('https://unilevertrade.s3.dualstack.sa-east-1.amazonaws.com/WhatsApp_Botmaker/000_Trade_UFS_Promos_de_junho_00-00_wpp.png' AS VARCHAR(1000)) AS imageURL
  FROM Unilever_000_DBM.dbo.[20250620-adhoc-wpp-arraia_de_ofertas]
