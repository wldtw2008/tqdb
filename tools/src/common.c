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
