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
#include <cassandra.h>
#include <time.h>
#include <stdint.h>
#include <string.h>
#include <stdlib.h>
#include "common.h"
void vCheckSystex(int argc, char *argv[]) {
	if (argc >= 6)
	{
		//good
	}
	else
	{
		vMyLog(stdout, 1, "Systex Error");
		vMyLog(stdout, 1, "Systex: %s IP Port dbname dbgflag isQuote", argv[0]);
		vMyLog(stdout, 1, "        *The flag 'isQuote' means insert the quote or not.");
		vMyLog(stdout, 1, "    Ex: %s 127.0.0.1 9042 tqdb1 1 0", argv[0]);
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

int iCassConnect(CassSession* session, const CassCluster* cluster)
{
    CassFuture* connect_future = cass_session_connect(session, cluster);
    int iRet = 0;
    if (cass_future_error_code(connect_future) == CASS_OK) {
        iRet = 1;
    } else {
        const char* pszMsg;
        int iMsgLen;
        cass_future_error_message(connect_future, &pszMsg, &iMsgLen);
        fprintf(stderr, "Unable to connect: '%.*s'\n", iMsgLen, pszMsg);
    }
    cass_future_free(connect_future);
    return iRet;
}
int iCassExecuteInsertStatement(const CassSession* session, const char* pszInsert)
{
    CassStatement* statement = cass_statement_new(pszInsert, 0);
    CassFuture* result_future = cass_session_execute(session, statement);
    int iRet = 0;
    if(cass_future_error_code(result_future) == CASS_OK) {
        iRet = 1;
    } else {
        const char* pszMsg;
        int iMsgLen;
        cass_future_error_message(result_future, &pszMsg, &iMsgLen);
        fprintf(stderr, "Unable to execute statement: '%.*s'\n", iMsgLen, pszMsg);
    }
    cass_future_free(result_future);
    cass_statement_free(statement);
    return iRet;
}

int main(int argc, char *argv[]) {
	char *pszIP, *pszPort, *pszDBName;
	char szTQDBKeyVal[2048], szInsStr[4096];
        int i, iDBGFlag, isQuote;
	ST_TickData objTickData;
	/* Setup and connect to cluster */
	CassCluster* cluster = cass_cluster_new();
	CassSession* session = cass_session_new();

	vCheckSystex(argc, argv);
        i = 1;
	pszIP = argv[i++];
	pszPort = argv[i++];
        pszDBName = argv[i++];
	iDBGFlag = atoi(argv[i++]);
	isQuote = atoi(argv[i++]);

	//iEPIDFilter = atoi(argv[i++]);

        cass_cluster_set_port(cluster, atoi(pszPort));
        cass_cluster_set_contact_points(cluster, pszIP);//"192.168.1.217");
        cass_cluster_set_connect_timeout(cluster, 10000);
        cass_cluster_set_request_timeout(cluster, 600000);
        cass_cluster_set_num_threads_io(cluster, 2);
	if (iCassConnect(session, cluster) == 0)
	{
		exit(0);
	}
	char szLine[2048];
	int iLen, iQuoteOrTick;
	char tmpC;
	int iInsertCnt = 0;
	vMyLog(stdout, 1, "Getting data from stdin.");
	fflush(stdout);
	while(fgets(szLine, sizeof(szLine), stdin))
	{
		szLine[sizeof(szLine)] = '\0';
		iLen = strlen(szLine);
		while(1)
		{
			tmpC = szLine[iLen-1];
			if (tmpC == '\r' || tmpC == '\n')
			{
				iLen--;
				szLine[iLen] = '\0';
			}
			else
				break;
		}
		iQuoteOrTick = -1;
		/*
		{'ASK': 9533, 'BID': 9532, 'EPID': 3, 'V': 13403}
		{'C': 9532, 'EPID': 3, 'TC': 3194, 'V': 1}
		*/
		if (strncmp(szLine, "01_ID=", 6) == 0)
                {
			char szSymbol[32], szClose[32], szVol[32], szTC[32], szEPID[32];
			szGetValueByKey(szLine+3, "ID", szSymbol, "");
			
			szGetValueByKey(szLine+3, "C", szClose, "0");
			szGetValueByKey(szLine+3, "V", szVol, "0");
			szGetValueByKey(szLine+3, "TC", szTC, "0");
			szGetValueByKey(szLine+3, "EPID", szEPID, "0");

			sprintf(szTQDBKeyVal, "{'C':%s,'V':%s,'TC':%s,'EPID':%s}", szClose, szVol, szTC, szEPID);
//strcpy(szSymbol,"KK");
			sprintf(szInsStr, "insert into %s.tick (symbol, datetime, type, keyval) values ('%s', %lld, %d, %s);",
				pszDBName, szSymbol, llGetCurrentEpoch(), 1, szTQDBKeyVal);

			if (iDBGFlag==1)
				fprintf(stdout,"%s\n", szInsStr);
			if (iCassExecuteInsertStatement(session, szInsStr) == 0)
			{
				exit(0);
			}
			iInsertCnt++;
                        iQuoteOrTick = 1;
                }
		if (isQuote==1 && strncmp(szLine, "00_ID=", 6) == 0)//quote
		{
			char szSymbol[32], szTmp[32];
			char *szAllowKey[] = {"BID", "ASK", "V", "EPID", NULL};
			char *pKey;
			int j, iFoundKeyCnt;
			szGetValueByKey(szLine+3, "ID", szSymbol, "");
			szTQDBKeyVal[0] = '\0';
			sprintf(szTQDBKeyVal+strlen(szTQDBKeyVal), "{");
			iFoundKeyCnt = 0;
			for (j=0;szAllowKey[j]!=NULL;j++)
			{
				pKey = szAllowKey[j];
				szGetValueByKey(szLine+3, pKey, szTmp, "");
				if (szTmp[0] == '\0')
					continue;
				sprintf(szTQDBKeyVal+strlen(szTQDBKeyVal), "%c'%s':%s", (iFoundKeyCnt==0?' ':','), pKey, szTmp);
				iFoundKeyCnt++;
			}
			sprintf(szTQDBKeyVal+strlen(szTQDBKeyVal), "}");
//strcpy(szSymbol,"KK");
			sprintf(szInsStr, "insert into %s.tick (symbol, datetime, type, keyval) values ('%s', %lld, %d, %s);",
                                pszDBName, szSymbol, llGetCurrentEpoch(), 0, szTQDBKeyVal);
			
			if (iDBGFlag==1)
	                        vMyLog(stdout, 1, "Statement: %s", szInsStr);
                        if (iCassExecuteInsertStatement(session, szInsStr) == 0)
                        {
                                exit(0);
                        }
			iInsertCnt++;
			iQuoteOrTick = 0;
		}
		if (iQuoteOrTick == -1)
			continue;
		if (iInsertCnt == 1||
		    (iInsertCnt>=100 && iInsertCnt<1000 && (iInsertCnt%100) == 0) ||
		    (iInsertCnt>=1000 && (iInsertCnt%1000) == 0) )
		{
			vMyLog(stdout, 1, "Inserted %d data", iInsertCnt);
			fflush(stdout);
		}
	}
	
	vMyLog(stdout, 1, "Graceful Exit.");
	fflush(stdout);
	if (1)//Close the session
	{
	    CassFuture* close_future = cass_session_close(session);
	    cass_future_wait(close_future);
	    cass_future_free(close_future);
	}
	cass_cluster_free(cluster);
	cass_session_free(session);
	exit(0);
/*
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
		* /

		CassStatement* statement = cass_statement_new(szQStr, 0);
		const int page_size = 40000;
		cass_statement_set_paging_size(statement, page_size);
		int iIsMorePage = 0;
		do{
			iIsMorePage = 0;
			time_t t1 = time(NULL);
			CassFuture* result_future = cass_session_execute(session, statement);
			if(cass_future_error_code(result_future) == CASS_OK) {
				/* Retrieve result set and iterator over the rows * /
				CassResult* result = cass_future_get_result(result_future);
				CassIterator* rows = cass_iterator_from_result(result);
				time_t t2 = time(NULL);
				if (iDBGFlag) 
					printf("page: %d, execute time=%d Secs\n", ++iPage, t2-t1);
				char kk[32];
				//scanf("%s",kk);

				while(cass_iterator_next(rows)) {
					const CassRow* row = cass_iterator_get_row(rows);
					const CassValue* sym = cass_row_get_column_by_name(row, "symbol");
					cass_int64_t datetime;
					cass_value_get_int64(cass_row_get_column_by_name(row, "datetime"), (cass_int64_t*)&datetime);
					cass_int32_t type;
					cass_value_get_int32(cass_row_get_column_by_name(row, "type"), (cass_int32_t*)&type);

					if (type!=1) continue;

					//CassString keyspace_name;
					//cass_value_get_string(value, &keyspace_name);

					const char* pszSym;
					int iSymLen;
					cass_value_get_string(sym, &pszSym, &iSymLen);

					if (type ==1)
					{
						CassIterator* iterMap = cass_iterator_from_map(cass_row_get_column_by_name(row, "keyval"));
						uint64_t i64DateTime = datetime;
						objTickData.dbDateTime = i64DateTime/1000.0;
						while (cass_iterator_next(iterMap)) {
							const char* pszMapKey;
							int iMapKeyLen;
							cass_double_t mapValue;
							cass_value_get_string(cass_iterator_get_map_key(iterMap), &pszMapKey, &iMapKeyLen);
							cass_value_get_double(cass_iterator_get_map_value(iterMap), &mapValue);
							if (strncmp(pszMapKey, "EPID", max(iMapKeyLen,4)) == 0)
								objTickData.iEPID = (int)mapValue;
							else if(strncmp(pszMapKey, "C", max(iMapKeyLen,1)) == 0)
								objTickData.dbPrc = mapValue;
							else if(strncmp(pszMapKey, "V", max(iMapKeyLen,1)) == 0)
								objTickData.iVol = (int)mapValue;
						}
						if (iEPIDFilter==-1 || iEPIDFilter==objTickData.iEPID)
						{
							int iDate, iTime, iMSec;
							vEpoch2DateTime(&objTickData.dbDateTime, &iDate, &iTime, &iMSec);
							if (iDBGFlag)
							{
								if (iFirstLine==0)
								{
									printf("Date,Time,TickPrc,TickVol,EPID\n");
									iFirstLine=1;
								}
								printf("%d,%06d.%03d,%s,%d,%d\n",iDate, iTime, iMSec, szDb2Str(NULL, &objTickData.dbPrc), objTickData.iVol,objTickData.iEPID);
							}
							else

								printf("%d,%06d.%03d,%s,%d\n", iDate, iTime, iMSec, szDb2Str(NULL, &objTickData.dbPrc), objTickData.iVol);	
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
				/* Handle error * /
				const char* pszMsg;
				int iMsgLen;
				cass_future_error_message(result_future, &pszMsg, &iMsgLen);
				fprintf(stderr, "Unable to run query: '%.*s'\n", iMsgLen, pszMsg);
			} 
			cass_future_free(result_future);
			
		}while(iIsMorePage);
		cass_statement_free(statement);

		/* Close the session * /
		close_future = cass_session_close(session);
		cass_future_wait(close_future);
		cass_future_free(close_future);

	} else {
		/* Handle error * /
:q!                const char* pszMsg;
                int iMsgLen;
                cass_future_error_message(connect_future, &pszMsg, &iMsgLen);
		fprintf(stderr, "Unable to connect: '%.*s'\n", iMsgLen, pszMsg);
	}

	cass_future_free(connect_future);
	cass_cluster_free(cluster);
	time_t tEnd = time(NULL);
	if (iDBGFlag)
		printf("total info> page: %d, data cnt: %d, execute time=%d Secs\n", iPage, iDataCnt, tEnd-tBeg);
*/		
	return 0;
}
