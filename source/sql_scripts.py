#sql_scripts.py

# SQL scripts used to create and manipulate datasets in the data store

# Tabular Assets Store

initializeUUIDQuery = 'CREATE EXTENSION IF NOT EXISTS "uuid-ossp";'
getDataQuery =  getDataQuery = 'SELECT * FROM "{}";'
getDataModelQuery = "select column_name, data_type from INFORMATION_SCHEMA.COLUMNS where TABLE_NAME=N%s ORDER BY ORDINAL_POSITION"
getCountNumberOfRows = 'SELECT COUNT(*)  FROM {}'
deleteTableQuery =  "DROP TABLE {} ;"
getAllTableNames = "SELECT table_name FROM information_schema.tables WHERE table_schema = %s AND table_type = %s;"
copyTableQuery = "CREATE TABLE {} AS (SELECT * FROM {});"
insertIntoTableQuery = "INSERT INTO {} ({}) VALUES ({});"
getSortedFieldsFromTables = "SELECT {} from {} order by {} {}"
getFieldsFromTables = "SELECT {} from {}"

# getSummaryStatistics = " SELECT  {}, min({}) , percentile_disc(0.25) within group ( order by {} ) as Q1, percentile_disc(0.5) within group ( order by {} ) as Q2, percentile_disc(0.75) within group ( order by {} ) as Q3, max({}) FROM {} WHERE version_id = '{}' GROUP BY {} "
# insertCopyTableQuery = "INSERT INTO {} (SELECT * FROM {});"
# getCountsOfValues = "SELECT {}, COUNT(1) from {} where version_id = '{}' GROUP BY {}"
# updateTableQuery = "UPDATE {} SET version_id = '{}' WHERE version_id = '{}'"
# deleteRowsQuery = "DELETE FROM {} WHERE version_id = '{}'"
# selectAllVersions = "SELECT version_id from {} where version_id > '{}'"
# getVersionID = "SELECT MAX(version_id) FROM {};"
# checkVersionIDExists = "SELECT column_name FROM information_schema.columns WHERE table_name='{}' and column_name='version_id';"

# File Assets Store

tableExistsQuery = "SELECT EXISTS(SELECT * FROM information_schema.tables WHERE table_name='%s')"
createTableQuery = "CREATE TABLE IF NOT EXISTS {} (id uuid, file_name text, file bytea);"
insertFileQuery = "INSERT INTO {} (id, file_name, file) VALUES (%s, %s, %s);"
checkFileExists = "SELECT exists (SELECT 1 FROM {} WHERE id = %s LIMIT 1);"
getFileQuery = "SELECT file, file_name FROM {} WHERE id = %s;"
getAllIds = "SELECT DISTINCT id FROM {}"
getFileName = "SELECT id, file_name FROM {} WHERE id = %s;"
updateFileName = "UPDATE {} SET file_name = %s WHERE id = %s;"
deleteFileQuery = "DELETE FROM {} WHERE id = %s; "

# updateFileVersion = "UPDATE {} SET file = %s WHERE id = '{}';"
# deleteFileVersion = "DELETE FROM {} WHERE id = '{}' and version_id = '{}' ; "
# selectFileVersions = "SELECT version_id from {} where id = '{}' and version_id > '{}'"
#  updateVersionID = "UPDATE {} SET version_id = '{}' WHERE version_id = '{}' and id = '{}' "










         



         

