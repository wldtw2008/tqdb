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
#include <sys/time.h>
#include <stdarg.h>
#include <vector>
#include <map>
#include <string>
#include "common.h"
char g_szDBStr[128];
const char* szDb2Str(char *pszDB, double* pdbVal)
{
        int iLen;
	if (pszDB == NULL)
		pszDB = pszDB;
        sprintf(pszDB, "%f", *pdbVal);
        if (strchr(pszDB, '.') == NULL)
                return pszDB;
	iLen=strlen(pszDB)-1;
        for (;iLen>0;iLen--)
        {
                if (pszDB[iLen] == '0')
	                pszDB[iLen] = '\0';
		else if (pszDB[iLen] == '.')
		{
			pszDB[iLen+1] = '0';
			pszDB[iLen+2] = '\0';
			break;
		}
		else
			break;
        }
        return pszDB;
}
void vEpoch2DateTime(const double* pdbEpoch, int* piDate, int* piTime, int* piMSec)
{
	time_t tt = (int)*pdbEpoch;
	struct tm t;
	t = *localtime(&tt);
	if (piDate != NULL)
	*piDate = (t.tm_year+1900)*10000+(t.tm_mon+1)*100+t.tm_mday;
	if (piTime != NULL)
	*piTime = t.tm_hour*10000+t.tm_min*100+t.tm_sec;
	if (piMSec != NULL)
	*piMSec = ((*pdbEpoch)-(int)(*pdbEpoch))*1000;
}
long long llGetCurrentEpoch()
{
	struct timeval tp;
	long long mslong = 0;
	gettimeofday(&tp, NULL);
	mslong = (long long) tp.tv_sec * 1000L + tp.tv_usec / 1000; //get current timestamp in milliseconds
	//return (double)mslong;
	return mslong;
}
char* szGetValueByKey(const char* szLine, const char* szKey, char* szValue, const char* szDefaultVal)
{
        char szFindKey[128];
        const char *pszBeg, *pszEnd;
	int iFindKeyLen;
        szFindKey[0] = '\0';
        strcat(szFindKey, szKey);
        strcat(szFindKey, "=");
	iFindKeyLen = strlen(szFindKey);
        szValue[0] = '\0';
	pszBeg = szLine;
	while(1)
	{
		if (strncasecmp(pszBeg, szFindKey, iFindKeyLen) == 0)
		{
			pszBeg += iFindKeyLen;
			pszEnd = strchr(pszBeg, ',');
		        if (pszEnd == NULL)
                		pszEnd = szLine + strlen(szLine);
		        while(pszEnd>pszBeg)
		        {
		                if (*pszEnd == ',' || *pszEnd == '\n' || *pszEnd == '\r')
		                        pszEnd--;
		                else
		                        break;
		        }
		        strncat(szValue, pszBeg, pszEnd-pszBeg+1);
		        return szValue;
		}
		pszBeg = strchr(pszBeg, ',');
		if (pszBeg == NULL)
			break;
		pszBeg++;
	}
	strcpy(szValue, szDefaultVal);
	return szValue;
}
char* szGetValueByKeyX(const char* szLine, const char* szKey, char* szValue, const char* szDefaultVal)
{
	char szFindKey[128];
	const char *pszBeg, *pszEnd;
	szFindKey[0] = '\0';
	strcat(szFindKey, szKey);
	strcat(szFindKey, "=");

	szValue[0] = '\0';
	pszBeg = strstr(szLine, szFindKey);
	if (pszBeg == NULL)
	{
		strcpy(szValue, szDefaultVal);
		return szValue;
	}
	pszBeg += strlen(szFindKey);
	pszEnd = strchr(pszBeg, ',');
	if (pszEnd == NULL)
		pszEnd = szLine + strlen(szLine);
	while(pszEnd>pszBeg)
	{
		if (*pszEnd == ',' || *pszEnd == '\n' || *pszEnd == '\r')
			pszEnd--;
		else
			break;
	}
	strncat(szValue, pszBeg, pszEnd-pszBeg+1);
	return szValue;
}

char g_szLogBuf[1024];
char g_szLogBuf2[1024];
void vMyLog(FILE*fp, int iLogType, const char* cmd, ...)
{
	va_list args;
	va_start(args, cmd);
	vsprintf(g_szLogBuf2, cmd, args);
	va_end(args);
	time_t t = time(NULL);
	struct tm* tmTime = localtime(&t);
	sprintf(g_szLogBuf, "%04d%02d%02d %02d:%02d:%02d> %s\n",
                                tmTime->tm_year+1900,
                                tmTime->tm_mon+1,
                                tmTime->tm_mday,
                                tmTime->tm_hour,
                                tmTime->tm_min,
                                tmTime->tm_sec,
				g_szLogBuf2);
	fprintf(fp, "%s", g_szLogBuf);
}
ST_SymbolInfo objSymInfoForSwap;
void vSwapSymbolInfo(std::vector<ST_SymbolInfo>* pvecSymbolInfo, int i, int j)
{
    objSymInfoForSwap.symbol = (*pvecSymbolInfo)[j].symbol;
    objSymInfoForSwap.mapKeyVal = (*pvecSymbolInfo)[j].mapKeyVal;
    (*pvecSymbolInfo)[j].symbol = (*pvecSymbolInfo)[i].symbol;
    (*pvecSymbolInfo)[j].mapKeyVal = (*pvecSymbolInfo)[i].mapKeyVal;
    (*pvecSymbolInfo)[i].symbol = objSymInfoForSwap.symbol;
    (*pvecSymbolInfo)[i].mapKeyVal = objSymInfoForSwap.mapKeyVal;

}
int iCompareSymbolInfo(std::vector<ST_SymbolInfo>* pvecSymbolInfo, int iLHS, int iRHS)
{
    ST_SymbolInfo* pLHS = &(*pvecSymbolInfo)[iLHS];
    ST_SymbolInfo* pRHS = &(*pvecSymbolInfo)[iRHS];
    return strcmp(pLHS->symbol.c_str(), pRHS->symbol.c_str());
}
void SlowSort(std::vector<ST_SymbolInfo>* pvecSymbolInfo)
{
    int iLen = pvecSymbolInfo->size();
    ST_SymbolInfo objSymInfo;
    if (iLen <= 1) return;
    for (int i=0;i<iLen-1;++i)
        for (int j=0;j<iLen-1;++j)
        {
            if (iCompareSymbolInfo(pvecSymbolInfo, j, j+1)>0)
            {
                vSwapSymbolInfo(pvecSymbolInfo, j, j+1);
            }
        }
}
void QuickSort(std::vector<ST_SymbolInfo>* pvecSymbolInfo, int left, int right)
{
    int pivot, i, j;

    if (left >= right) { return; }

    pivot = left;

    i = left + 1;
    j = right;

    while (1)
    {
        while (i <= right)
        {
            if (iCompareSymbolInfo(pvecSymbolInfo, i, pivot) > 0)
            {
                break;
            }

            i = i + 1;
        }

        while (j > left)
        {
            if (iCompareSymbolInfo(pvecSymbolInfo, j, pivot) < 0)
            {
                break;
            }

            j = j - 1;
        }

        if (i > j) { break; }

        vSwapSymbolInfo(pvecSymbolInfo, i, j);
    }

    vSwapSymbolInfo(pvecSymbolInfo, left, j);

    QuickSort(pvecSymbolInfo, left, j - 1);
    QuickSort(pvecSymbolInfo, j + 1, right);
}
int iQAllSymbol(std::vector<ST_SymbolInfo>* pvecSymbolInfo, const char *pszTQDB, CassSession* session, CassCluster* cluster)
{
    char szQStr[128];
    pvecSymbolInfo->clear();

    /*
    CassFuture* connect_future = cass_session_connect(session, cluster);
    if (cass_future_error_code(connect_future) != CASS_OK)
    {
	const char* pszMsg;
        size_t iMsgLen;
        cass_future_error_message(connect_future, &pszMsg, &iMsgLen);
        fprintf(stderr, "Unable to connect: '%.*s'\n", (int)iMsgLen, pszMsg);
        cass_future_free(connect_future);
        return pvecSymbolInfo->size();
    }*/

    sprintf(szQStr, "SELECT * from %s.symbol;", pszTQDB);

    const char* pszSym;
    size_t iSymLen;
    if (1) {
        CassStatement* statement = cass_statement_new(szQStr, 0);
        const int page_size = 40000;
        cass_statement_set_paging_size(statement, page_size);
        int iIsMorePage = 0;
        do{
            iIsMorePage = 0;
            CassFuture* result_future = cass_session_execute(session, statement);
            if(cass_future_error_code(result_future) == CASS_OK) {
                const CassResult* result = cass_future_get_result(result_future);
                CassIterator* rows = cass_iterator_from_result(result);
                while(cass_iterator_next(rows)) 
                {
                    const CassRow* row = cass_iterator_get_row(rows);
                    const CassValue* sym = cass_row_get_column_by_name(row, "symbol");
                    cass_value_get_string(sym, &pszSym, &iSymLen);
                    ST_SymbolInfo tmpSymbolInfo;
                    tmpSymbolInfo.symbol.assign(pszSym, iSymLen);
                    while (1)
                    {
                        CassIterator* iterMap = cass_iterator_from_map(cass_row_get_column_by_name(row, "keyval"));
                        if (iterMap == NULL)
                        break;
                        while (cass_iterator_next(iterMap)) {
                            const char* pszMapKey, *pszMapVal;
                            size_t iMapKeyLen, iMapValLen;
                            cass_value_get_string(cass_iterator_get_map_key(iterMap), &pszMapKey, &iMapKeyLen);
                            cass_value_get_string(cass_iterator_get_map_value(iterMap), &pszMapVal, &iMapValLen);
                            std::string strKey, strVal;
                            strKey.assign(pszMapKey, iMapKeyLen);
                            strVal.assign(pszMapVal, iMapValLen);
                            tmpSymbolInfo.mapKeyVal[strKey] = strVal;
                        }
                        break;
                    }
                    pvecSymbolInfo->push_back(tmpSymbolInfo);
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
                fprintf(stderr, "Unable to run query: '%.*s'\n", (int)iMsgLen, pszMsg);
            }
            cass_future_free(result_future);

        }while(iIsMorePage);
        cass_statement_free(statement);
    } else {
    }
    QuickSort(pvecSymbolInfo, 0, pvecSymbolInfo->size()-1);
    //SlowSort(pvecSymbolInfo);    
    return pvecSymbolInfo->size();
}
int iUpdateSymbol(ST_SymbolInfo* pSymbolInfo, const char *pszTQDB, CassSession* session, CassCluster* cluster)
{
    char szQStr[2048];
    int iRet = 0;
    /*
    CassFuture* connect_future = cass_session_connect(session, cluster);
    if (cass_future_error_code(connect_future) != CASS_OK)
    {
        const char* pszMsg;
        size_t iMsgLen;
        cass_future_error_message(connect_future, &pszMsg, &iMsgLen);
        fprintf(stderr, "Unable to connect: '%.*s'\n", (int)iMsgLen, pszMsg);
        cass_future_free(connect_future);
        return pvecSymbolInfo->size();
    }*/

    sprintf(szQStr, "insert into %s.symbol (symbol,keyval) values ('%s',{", pszTQDB, pSymbolInfo->symbol.c_str());
    int iKeyValCnt = 0;
    std::map<std::string, std::string>::iterator iter;
    for (iter=pSymbolInfo->mapKeyVal.begin( ); iter != pSymbolInfo->mapKeyVal.end( ); ++iter)
    {
        sprintf(szQStr+strlen(szQStr), "%c'%s':'%s'", (iKeyValCnt!=0?',':' '), iter->first.c_str(), iter->second.c_str());
        iKeyValCnt++;
    }
    sprintf(szQStr+strlen(szQStr), "});");
printf("---->%s\n", szQStr);

    if (1) {
        CassStatement* statement = cass_statement_new(szQStr, 0);
        const int page_size = 40000;
        cass_statement_set_paging_size(statement, page_size);
        int iIsMorePage = 0;
        do{
            iIsMorePage = 0;
            CassFuture* result_future = cass_session_execute(session, statement);
            if(cass_future_error_code(result_future) == CASS_OK) {
                iRet = 1;
            } else {
                /* Handle error */
                const char* pszMsg;
                size_t iMsgLen;
                cass_future_error_message(result_future, &pszMsg, &iMsgLen);
                fprintf(stderr, "Unable to run query: '%.*s'\n", (int)iMsgLen, pszMsg);
                iRet = -1;
            }
            cass_future_free(result_future);

        }while(iIsMorePage);
        cass_statement_free(statement);
    } else {
        iRet = -2;
    }

    return iRet;
}
