--1-20241224-adhoc-wpp-relacionamento-boas_festas_natal_NEWBACON
SELECT CAST(CONCAT('55',CELULAR) AS NVARCHAR(20)) AS phone
      ,CAST(PRIMEIRO_NOME AS NVARCHAR(50)) AS  chicoFirstName
	  ,CAST('https://storage.googleapis.com/storage.botmaker.com/public/res/newbaconchicodaunilever/20241219-ov17g0vkEMeCEeUQgw7OfhY917f2-B6CI4-MzQwX0VNS1RfVUZTX1RSQURFX0JPQVNfRkVTVEFTX1dQUA==.png' AS NVARCHAR(1000)) as url_imagem
  FROM Unilever_000_DBM..[20241224-adhoc-wpp-relacionamento-boas_festas_natal]
 WHERE ORIGEM = 'GRUPO CONTROLE'
   AND CELULAR IN ('11991371931','11992484883','18996698725')

--1-20241224-adhoc-wpp-relacionamento-boas_festas_natal_CLIENTE
SELECT CAST(CONCAT('55',CELULAR) AS NVARCHAR(20)) AS phone
      ,CAST(PRIMEIRO_NOME AS NVARCHAR(50)) AS  chicoFirstName
	  ,CAST('https://storage.googleapis.com/storage.botmaker.com/public/res/newbaconchicodaunilever/20241219-ov17g0vkEMeCEeUQgw7OfhY917f2-B6CI4-MzQwX0VNS1RfVUZTX1RSQURFX0JPQVNfRkVTVEFTX1dQUA==.png' AS NVARCHAR(1000)) as url_imagem
  FROM Unilever_000_DBM..[20241224-adhoc-wpp-relacionamento-boas_festas_natal]
 WHERE ORIGEM = 'GRUPO CONTROLE'
   AND CELULAR IN ('11991371931','11992484883','18996698725','38998310055','11996924646')

--1-20241224-adhoc-wpp-relacionamento-boas_festas_natal_FINAL
SELECT CAST(CONCAT('55',CELULAR) AS NVARCHAR(20)) AS phone
      ,CAST(PRIMEIRO_NOME AS NVARCHAR(50)) AS  chicoFirstName
	  ,CAST('https://storage.googleapis.com/storage.botmaker.com/public/res/newbaconchicodaunilever/20241219-ov17g0vkEMeCEeUQgw7OfhY917f2-B6CI4-MzQwX0VNS1RfVUZTX1RSQURFX0JPQVNfRkVTVEFTX1dQUA==.png' AS NVARCHAR(1000)) as url_imagem
  FROM Unilever_000_DBM..[20241224-adhoc-wpp-relacionamento-boas_festas_natal]
