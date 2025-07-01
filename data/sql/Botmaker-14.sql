--20250630_adhoc_wpp_campanha_metade_ciclo3_bateu_1
SELECT CAST(CONCAT('55',CELULAR) AS NVARCHAR(20)) AS phone
      ,CAST(PRIMEIRO_NOME AS NVARCHAR(20)) AS chicoFirstName
  FROM Unilever_000_DBM.dbo.[20250630_adhoc_wpp_campanha_metade_ciclo3]
 WHERE ISNULL(PERFIL,'') IN ('','20250630_adhoc_wpp_campanha_metade_ciclo3_bateu_1')

--20250630_adhoc_wpp_campanha_metade_ciclo3_nao_bateu_1
SELECT CAST(CONCAT('55',CELULAR) AS NVARCHAR(20)) AS phone
      ,CAST(PRIMEIRO_NOME AS NVARCHAR(20)) AS chicoFirstName
  FROM Unilever_000_DBM.dbo.[20250630_adhoc_wpp_campanha_metade_ciclo3]
 WHERE ISNULL(PERFIL,'') IN ('','20250630_adhoc_wpp_campanha_metade_ciclo3_nao_bateu_1')
