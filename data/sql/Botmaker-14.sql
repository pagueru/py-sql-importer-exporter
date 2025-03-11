--1-20250310_adhoc_wpp_vendas_reenvio_familia_maionese_tradicional_NEWBACON
SELECT CAST(CONCAT('55',CELULAR) AS NVARCHAR(20)) AS phone
      ,CAST(PRIMEIRO_NOME AS NVARCHAR(50)) AS  chicoFirstName
	  ,url_imagem
  FROM Unilever_000_DBM..[20250310-adhoc-wpp-vendas_reenvio_familia_maionese_tradicional]
 WHERE ORIGEM = 'GRUPO CONTROLE'
   AND CELULAR IN ('11991371931','18996698725','11998055353')

--1-20250310_adhoc_wpp_vendas_reenvio_familia_maionese_tradicional_CLIENTE
SELECT CAST(CONCAT('55',CELULAR) AS NVARCHAR(20)) AS phone
      ,CAST(PRIMEIRO_NOME AS NVARCHAR(50)) AS  chicoFirstName
	  ,url_imagem
  FROM Unilever_000_DBM..[20250310-adhoc-wpp-vendas_reenvio_familia_maionese_tradicional]
 WHERE ORIGEM = 'GRUPO CONTROLE'
   AND CELULAR IN ('11991371931','18996698725','11998055353'
				  ,'38998310055','11964920611')

--1-20250310_adhoc_wpp_vendas_reenvio_familia_maionese_tradicional_FINAL
SELECT CAST(CONCAT('55',CELULAR) AS NVARCHAR(20)) AS phone
      ,CAST(PRIMEIRO_NOME AS NVARCHAR(50)) AS  chicoFirstName
	  ,url_imagem
  FROM Unilever_000_DBM..[20250310-adhoc-wpp-vendas_reenvio_familia_maionese_tradicional]
