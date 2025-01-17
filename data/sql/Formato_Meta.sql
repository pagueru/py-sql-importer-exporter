--BASE_SOCIAL_MIT_BASE_DE_EMPLACAMENTOS_DO_ULTIMO_ANO_META
SELECT DISTINCT
	   email
	  ,phone
	  ,fn
	  ,ln
	  ,ct
	  ,st
	  ,country
	  ,zip
	  ,dob
	  ,doby
	  ,gen
	  ,age  
  FROM Hpe_001_DBM..TMP_BASE_SOCIAL_MIT_BASE_EMPLACAMENTOS_2023_2024_20240805
 WHERE PERFIL = 'EMPLACAMENTOS 2023'

--BASE_SOCIAL_MIT_BASE_DO_PRIMEIRO_SEMESTRE_META
SELECT DISTINCT
	   email
	  ,phone
	  ,fn
	  ,ln
	  ,ct
	  ,st
	  ,country
	  ,zip
	  ,dob
	  ,doby
	  ,gen
	  ,age  
  FROM Hpe_001_DBM..TMP_BASE_SOCIAL_MIT_BASE_EMPLACAMENTOS_2023_2024_20240805
 WHERE PERFIL = 'EMPLACAMENTOS 1° SEMESTRE 2024'

--BASE_SOCIAL_MIT_BASE_DO_PRIMEIRO_SEMESTRE_E_ULTIMO_ANO_META
SELECT DISTINCT
	   email
	  ,phone
	  ,fn
	  ,ln
	  ,ct
	  ,st
	  ,country
	  ,zip
	  ,dob
	  ,doby
	  ,gen
	  ,age  
  FROM Hpe_001_DBM..TMP_BASE_SOCIAL_MIT_BASE_EMPLACAMENTOS_2023_2024_20240805