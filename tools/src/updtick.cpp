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
#include <sys/stat.h>
#include "common.h"
void vCheckSystex(int argc, char *argv[]) {
	if (argc >= 6)
	{
		//good
	}
	else
	{
		vMyLog(stdout, 1, "This util can update tick from stdin.");
		vMyLog(stdout, 1, "Input: yyyymmdd,hhmmss.sss,tickPrice,tickVol");
		vMyLog(stdout, 1, "");
		vMyLog(stdout, 1, "Systex Error");
		vMyLog(stdout, 1, "Systex: %s IP Port dbname symbol dbgflag", argv[0]);
		vMyLog(stdout, 1, "    Ex: %s 127.0.0.1 9042 tqdb1 WTX 1", argv[0]);
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
        size_t iMsgLen;
        cass_future_error_message(connect_future, &pszMsg, &iMsgLen);
        fprintf(stderr, "Unable to connect: '%.*s'\n", iMsgLen, pszMsg);
    }
    cass_future_free(connect_future);
    return iRet;
}
int iCassExecuteInsertStatement(CassSession* session, const char* pszInsert)
{
    CassStatement* statement = cass_statement_new(pszInsert, 0);
    CassFuture* result_future = cass_session_execute(session, statement);
    int iRet = 0;
    if(cass_future_error_code(result_future) == CASS_OK) {
        iRet = 1;
    } else {
        const char* pszMsg;
        size_t iMsgLen;
        cass_future_error_message(result_future, &pszMsg, &iMsgLen);
        fprintf(stderr, "Unable to execute statement: '%.*s'\n", iMsgLen, pszMsg);
    }
    cass_future_free(result_future);
    cass_statement_free(statement);
    return iRet;
}
int iGetSymbolIdx(std::vector<ST_SymbolInfo>* pvecSymbolInfo, const char* szSymbol)
{
	for (int i=0;i<pvecSymbolInfo->size();++i)
	{
		if (strcmp((*pvecSymbolInfo)[i].symbol.c_str(), szSymbol) == 0)
			return i;
	}
	return -1;
}
std::string& string_replace(std::string & strBig, const char* pszA, const char* pszB)
{
    int pos=0;
    int srclen=strlen(pszA);
    int dstlen=strlen(pszB);
    while( (pos=strBig.find(pszA, pos)) != std::string::npos)
    {
        strBig.replace(pos, srclen, pszB);
        pos += dstlen;
    }
}
std::string& strGetSymFilename(std::string& strSym)
{
	string_replace(strSym, "&", "\\&");
	return strSym;
}
int main(int argc, char *argv[]) {
	char *pszIP, *pszPort, *pszDBName, *pszSymbol;
	char szTQDBKeyVal[2048], szInsStr[4096];
        int i, iDBGFlag, isQuote;
	ST_TickData objTickData;
	std::vector<ST_SymbolInfo> vecSymbolInfo;
	/* Setup and connect to cluster */
	CassCluster* cluster = cass_cluster_new();
	CassSession* session = cass_session_new();

	vCheckSystex(argc, argv);
        i = 1;
	pszIP = argv[i++];
	pszPort = argv[i++];
        pszDBName = argv[i++];
	pszSymbol = argv[i++];
	iDBGFlag = atoi(argv[i++]);

	//iEPIDFilter = atoi(argv[i++]);

        cass_cluster_set_port(cluster, atoi(pszPort));
        cass_cluster_set_contact_points(cluster, pszIP);//"192.168.1.217");
        cass_cluster_set_connect_timeout(cluster, 10000);
        cass_cluster_set_request_timeout(cluster, 600000);
        cass_cluster_set_num_threads_io(cluster, 2);
	if (iCassConnect(session, cluster) == 0)
	{
		printf("Can't connect to cassandra\n");
		exit(0);
	}
	
	iQAllSymbol(&vecSymbolInfo, pszDBName, session, cluster);
	for (int k=0;k<vecSymbolInfo.size();++k)
	{
		if (k == 0)
			printf("All symbol count: %d\n", vecSymbolInfo.size());
		printf("   Sym#%d: %s\n", k+1, vecSymbolInfo[k].symbol.c_str());
	}

	char szLine[2048];
	int iLen;
	char tmpC;
	int iInsertCnt = 0;
	vMyLog(stdout, 1, "Getting data from stdin.");
	fflush(stdout);
	time_t tLastCheck = time(NULL);
	int iTickCnt = 0;
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
		/*
		{'ASK': 9533, 'BID': 9532, 'EPID': 3, 'V': 13403}
		{'C': 9532, 'EPID': 3, 'TC': 3194, 'V': 1}
		*/
		if (1)//tick
                {
			//20191104,082822.668,11406.0,23162,0
			int iDate;
			double date, time, price, vol;
			//customer symbol is begin at  ^^, so if the first 2 char of the symbol is ^^, we have to skip it.
			if (strstr(pszSymbol, "^^") == pszSymbol)
			{
				continue;
			}
			if (iGetSymbolIdx(&vecSymbolInfo, pszSymbol)<0)
			{
				ST_SymbolInfo tmpSymbolInfo;
				tmpSymbolInfo.symbol = pszSymbol;
				vecSymbolInfo.push_back(tmpSymbolInfo);
				int iUpdateRet = iUpdateSymbol(&tmpSymbolInfo, pszDBName, session, cluster);			
			}
			if (1)
			{
				char * pch;
				int iCnt = 0;
				while(iCnt<4)
				{
					if (iCnt == 0)
						pch = strtok(szLine, ",");
					else
						pch = strtok(NULL, ",");
					if (pch==NULL)
						break;
					switch(iCnt)
					{
						case 0:date=atof(pch);break;
						case 1:time=atof(pch);break;
						case 2:price=atof(pch);break;
						case 3:vol=atof(pch);break;
						default:break;
					}
					iCnt++;
				}
				if (iCnt!=4) continue;
				if (date<19700101) continue;
				sprintf(szTQDBKeyVal, "{'C':%f,'V':%f,'TC':%d,'EPID':0}", price, vol, ++iTickCnt);
				sprintf(szInsStr, "insert into %s.tick (symbol, datetime, type, keyval) values ('%s', %lld, %d, %s);",
					pszDBName, pszSymbol, llGetEpoch(date, time*1000), 1, szTQDBKeyVal);
			
				if (iDBGFlag==1)
					fprintf(stdout,"%s\n", szInsStr);
				if (iCassExecuteInsertStatement(session, szInsStr) == 0)
				{
					exit(0);
				}
				iInsertCnt++;
			}
                }
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
	return 0;
}
