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

#include "common.h"
void vCheckSystex(int argc, char *argv[]) {
	if (argc >= 8)
	{
		//good
	}
	else
	{
		printf("Systex Error\n");
		printf("Systex: %s IP Port dbname dbgflag Symbol DateTimeBeg DateTimeEnd\n", argv[0]);
		printf("    Ex: %s 127.0.0.1 9042 tqdb1.minbar 1 WTX 2015-03-05 2015-03-06\n", argv[0]);
		exit(0);
	}
}
int main(int argc, char *argv[]) {
	char *pszIP, *pszPort, *pszDBName, *pszQSym, *pszQDateBeg, *pszQDateEnd;
	char szQStr[2048];
        int i, iDBGFlag, iEPIDFilter;
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
	pszQDateBeg = argv[i++];
	pszQDateEnd = argv[i++];
	iEPIDFilter = -1;//atoi(argv[i++]);
	sprintf(szQStr, "SELECT datetime,open,high,low,close,vol from %s where symbol='%s' and  datetime>='%s' and datetime<'%s' order by datetime; ",
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
				CassResult* result = cass_future_get_result(result_future);
				CassIterator* rows = cass_iterator_from_result(result);
				time_t t2 = time(NULL);
				if (iDBGFlag) 
					printf("page: %d, execute time=%d Secs\n", ++iPage, t2-t1);
				char kk[32];
				//scanf("%s",kk);

				cass_int64_t datetime;
				cass_double_t open,high,low,close,vol;
				char szOpen[32], szHigh[32], szLow[32], szClose[32], szVol[32];
				int iDate, iTime, iMSec;
				double dbDateTime;
				while(cass_iterator_next(rows)) {
					const CassRow* row = cass_iterator_get_row(rows);
					cass_value_get_int64(cass_row_get_column_by_name(row, "datetime"), (cass_int64_t*)&datetime);
					dbDateTime = ((uint64_t)datetime)/1000.0;
					cass_value_get_double(cass_row_get_column_by_name(row, "open"), (cass_double_t*)&open);
					cass_value_get_double(cass_row_get_column_by_name(row, "high"), (cass_double_t*)&high);
					cass_value_get_double(cass_row_get_column_by_name(row, "low"), (cass_double_t*)&low);
					cass_value_get_double(cass_row_get_column_by_name(row, "close"), (cass_double_t*)&close);
					cass_value_get_double(cass_row_get_column_by_name(row, "vol"), (cass_double_t*)&vol);

					vEpoch2DateTime(&dbDateTime, &iDate, &iTime, &iMSec);
					if (iDBGFlag)
                                        {
	                                        if (iFirstLine==0)
                                                {
        	                                        printf("Date,Time,TickPrc,TickVol,EPID\n");
                                                        iFirstLine=1;
                                                }
                                        }
					printf("%d,%06d,%s,%s,%s,%s,%s\n",iDate, iTime,
						szDb2Str(szOpen, &open),szDb2Str(szHigh, &high),szDb2Str(szLow, &low),szDb2Str(szClose, &close),szDb2Str(szVol, &vol));
					iDataCnt++;
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
				int iMsgLen;
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
                int iMsgLen;
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
