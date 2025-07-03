--NB_full_semOptin_20250703
SELECT CAST(email AS nvarchar(255)) AS email,
       CAST(operatorGroup AS nvarchar(255)) AS operator_group,
	   CAST(HASH_CLIENTE AS nvarchar(255))  AS hash_cliente
  FROM ##OPERADOR
