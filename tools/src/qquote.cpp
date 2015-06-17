/*
  Copyright (c) 2015 WLDTW2008@gmail.com

  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.
*/

#include <stdio.h>
#include <stdlib.h>
#include <cassandra.h>
#include <time.h>
#include <stdint.h>
#include <string.h>
#include "common.h"

void vCheckSystex(int argc, char *argv[]) {
	if (argc >= 10)
	{
		//good
	}
	else
	{
		printf("Systex Error\n");
		printf("Systex: %s IP Port dbname dbgflag Symbol QuoteItem DateTimeBeg DateTimeEnd EPID\n", argv[0]);
		printf("    Ex: %s 127.0.0.1 9042 tqdb1.tick 1 WTX BID 2015-03-05 2015-03-06 0\n", argv[0]);
		exit(0);
	}
}
typedef struct _ST_TICKDATA
{
      double dbDateTime;//float is microsec
      int iEPID;
      double dbPrc;
      int iVol;
}ST_TickData;

int main(int argc, char *argv[]) {
	char *pszIP, *pszPort, *pszDBName, *pszQSym, *pszQItem, *pszQDateBeg, *pszQDateEnd;
	char szQStr[2048];
        int i, iDBGFlag, iEPIDFilter, iQItemLen;
	ST_TickData objTickData;
	/* Setup and connect to cluster */
	CassFuture* connect_future = NULL;
	CassCluster* cluster = cass_cluster_new();
	CassSession* session = cass_session_new();

	vCheckSystex(argc, argv);
        i = 1;
	pszIP = argv[i++];
	pszPort = argv[i++];
        pszDBName = argv[i++];
	iDBGFlag = atoi(argv[i++]);
	pszQSym = argv[i++];
	pszQItem = argv[i++];
	iQItemLen = atoi(pszQItem);
	pszQDateBeg = argv[i++];
	pszQDateEnd = argv[i++];
	iEPIDFilter = atoi(argv[i++]);
	sprintf(szQStr, "SELECT * from %s where symbol='%s' and  datetime>='%s' and datetime<'%s' order by datetime; ",
                pszDBName,
	pszQSym, pszQDateBeg, pszQDateEnd);
	if (iDBGFlag)
		printf("ready to query '%s'\n", szQStr);
	cass_cluster_set_port(cluster, atoi(pszPort));
	cass_cluster_set_contact_points(cluster, pszIP);//"192.168.1.217");
	cass_cluster_set_connect_timeout(cluster, 10000);
	cass_cluster_set_request_timeout(cluster, 600000);
	cass_cluster_set_num_threads_io(cluster, 2);
	//cass_cluster_set_protocol_version(cluster, protocol_version);


	connect_future = cass_session_connect(session, cluster);
	time_t tBeg = time(NULL);
	int iPage = 0;
	int iDataCnt = 0;
	int iFirstLine = 0;
	if (cass_future_error_code(connect_future) == CASS_OK) {
		CassFuture* close_future = NULL;

		/* Build statement and execute query */
		/*    CassString query = cass_string_init("SELECT keyspace_name "
										"FROM system.schema_keyspaces;");
		*/

		CassStatement* statement = cass_statement_new(szQStr, 0);
		const int page_size = 40000;
		cass_statement_set_paging_size(statement, page_size);
		int iIsMorePage = 0;
		do{
			iIsMorePage = 0;
			time_t t1 = time(NULL);
			CassFuture* result_future = cass_session_execute(session, statement);
			if(cass_future_error_code(result_future) == CASS_OK) {
				/* Retrieve result set and iterator over the rows */
				const CassResult* result = cass_future_get_result(result_future);
				CassIterator* rows = cass_iterator_from_result(result);
				time_t t2 = time(NULL);
				if (iDBGFlag) 
					printf("page: %d, execute time=%d Secs\n", ++iPage, t2-t1);
				char kk[32];
				//scanf("%s",kk);
				char szPrc[32];
				while(cass_iterator_next(rows)) {
					const CassRow* row = cass_iterator_get_row(rows);
					const CassValue* sym = cass_row_get_column_by_name(row, "symbol");
					cass_int64_t datetime;
					cass_value_get_int64(cass_row_get_column_by_name(row, "datetime"), (cass_int64_t*)&datetime);
					cass_int32_t type;
					cass_value_get_int32(cass_row_get_column_by_name(row, "type"), (cass_int32_t*)&type);

					if (type!=0) continue;

					//CassString keyspace_name;
					//cass_value_get_string(value, &keyspace_name);

					const char* pszSym;
					size_t iSymLen;
					cass_value_get_string(sym, &pszSym, &iSymLen);

					if (1)
					{
						CassIterator* iterMap = cass_iterator_from_map(cass_row_get_column_by_name(row, "keyval"));
						uint64_t i64DateTime = datetime;
						objTickData.dbDateTime = i64DateTime/1000.0;
						while (cass_iterator_next(iterMap)) {
							const char* pszMapKey;
							size_t iMapKeyLen;
							cass_double_t mapValue;
							cass_value_get_string(cass_iterator_get_map_key(iterMap), &pszMapKey, &iMapKeyLen);
							cass_value_get_double(cass_iterator_get_map_value(iterMap), &mapValue);
							if (strncmp(pszMapKey, "EPID", max(iMapKeyLen,4)) == 0)
							objTickData.iEPID = (int)mapValue;
							else if(strncmp(pszMapKey, pszQItem, max(iMapKeyLen, iQItemLen)) == 0)
							objTickData.dbPrc = mapValue;
							//else if(strncmp(szMapKey, "V") == 0)
							//objTickData.iVol = (int)mapValue;
						}
						if (iEPIDFilter==-1 || iEPIDFilter==objTickData.iEPID)
						{
							int iDate, iTime, iMSec;
							vEpoch2DateTime(&objTickData.dbDateTime, &iDate, &iTime, &iMSec);
							if (iDBGFlag)
							{
								if (iFirstLine==0)
								{
									printf("Date,Time,%s.Value,EPID\n", pszQItem);
									iFirstLine=1;
								}
								printf("%d,%06d.%03d,%s,%d\n",iDate, iTime, iMSec, szDb2Str(szPrc, &objTickData.dbPrc), objTickData.iEPID);
							}
							else

								printf("%d,%06d.%03d,%s\n", iDate, iTime, iMSec, szDb2Str(szPrc, &objTickData.dbPrc) );	
						}
						iDataCnt++;
					}
				}

				iIsMorePage = cass_result_has_more_pages(result);
				if (iIsMorePage) {
					cass_statement_set_paging_state(statement, result);
				}
				cass_result_free(result);
				cass_iterator_free(rows);
			} else {
				/* Handle error */
				const char* pszMsg;
				size_t iMsgLen;
				cass_future_error_message(result_future, &pszMsg, &iMsgLen);
				fprintf(stderr, "Unable to run query: '%.*s'\n", iMsgLen, pszMsg);
			} 
			cass_future_free(result_future);
			
		}while(iIsMorePage);
		cass_statement_free(statement);

		/* Close the session */
		close_future = cass_session_close(session);
		cass_future_wait(close_future);
		cass_future_free(close_future);

	} else {
		/* Handle error */
                const char* pszMsg;
                size_t iMsgLen;
                cass_future_error_message(connect_future, &pszMsg, &iMsgLen);
		fprintf(stderr, "Unable to connect: '%.*s'\n", iMsgLen, pszMsg);
	}

	cass_future_free(connect_future);
	cass_cluster_free(cluster);
	time_t tEnd = time(NULL);
	if (iDBGFlag)
		printf("total info> page: %d, data cnt: %d, execute time=%d Secs\n", iPage, iDataCnt, tEnd-tBeg);
		
	return 0;
}
