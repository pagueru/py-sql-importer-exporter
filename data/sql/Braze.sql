--20250118-adhoc-newbacon-10off_em_corona_3_por_2
SELECT DISTINCT
	   CAST(HASH_SHA256 AS NVARCHAR(255)) AS external_id
	  ,CAST(CLUSTER AS NVARCHAR(255)) AS cluster_newbacon
  FROM ##ZEXPRESS_GERAL
