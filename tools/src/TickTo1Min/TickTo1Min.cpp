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


// TickTo1Min.cpp : Defines the entry point for the console application.
//
#ifdef _WINDOWS
#include "stdafx.h"
#else
#include <stdio.h>
#include <stdlib.h>
#include <string>
#include <string.h>
#include <unistd.h>
#endif
#include "TickTo1Min.h"
#include <vector>
#include <map>



#ifdef _DEBUG
#define new DEBUG_NEW
#undef THIS_FILE
static char THIS_FILE[] = __FILE__;
#endif

/////////////////////////////////////////////////////////////////////////////
// The one and only application object
#ifdef _WINDOWS
CWinApp theApp;
#endif

#include <stdarg.h>  // For va_start, etc.
std::string string_format(const std::string fmt, ...) {
    int size = ((int)fmt.size()) * 2 + 50;   // Use a rubric appropriate for your code
    std::string str;
    va_list ap;
    while (1) {     // Maximum two passes on a POSIX system...
        str.resize(size);
        va_start(ap, fmt);
        int n = vsnprintf((char *)str.data(), size, fmt.c_str(), ap);
        va_end(ap);
        if (n > -1 && n < size) {  // Everything worked
            str.resize(n);
            return str;
        }
        if (n > -1)  // Needed size returned
            size = n + 1;   // For null char
        else
            size *= 2;      // Guess at a larger size (OS specific)
    }
    return str;
}

using namespace std;

class CTradeData
{
public:
	double dbOpen;
	double dbHigh;
	double dbLow;
	double dbClose;
	double dbVol;
	CTradeData()
	{
		dbOpen = dbHigh = dbLow = dbClose = dbVol = 0;
	}
};

string cszCutDouble(double& dbPrice)
{
	string cszTmp;
	if (double(int(dbPrice)) == dbPrice)
	{	
		cszTmp = string_format("%.1f", dbPrice);
	}
	else
	{	
		cszTmp = string_format("%f", dbPrice);
		for (int j=cszTmp.length()-1;j>=1;--j)
		{
			if (cszTmp[j] == '0' && cszTmp[j-1] != '.')
				cszTmp[j] = '\0';
			else
				break;
		}
		//cszTmp.TrimRight("0");
	}
	return cszTmp;
}

int getMinEpochFromDateTime(int iDateYYYYMMDD, int iTimeHHMMSS)
{
	struct tm t = {0};  // Initalize to all 0's
	t.tm_year = iDateYYYYMMDD/10000-1900;  // This is year-1900, so 112 = 2012
	t.tm_mon = ((iDateYYYYMMDD/100)%100)-1;
	t.tm_mday = iDateYYYYMMDD%100;
	t.tm_hour = iTimeHHMMSS/10000;
	t.tm_min = (iTimeHHMMSS/100)%100;
	t.tm_sec = iTimeHHMMSS%100;
	time_t timeSinceEpoch = mktime(&t);
	return timeSinceEpoch/60;
}

void vGetDateTimeFromMinEpoch(int iMinEpoch, int *piDateYYYYMMDD, int *piTimeHHMMSS)
{
	time_t timeSinceEpoch = iMinEpoch*60;
	struct tm* tmTime = localtime(&timeSinceEpoch);
	*piDateYYYYMMDD = (tmTime->tm_year+1900)*10000+(tmTime->tm_mon+1)*100+tmTime->tm_mday;
	*piTimeHHMMSS = tmTime->tm_hour*10000+tmTime->tm_min*100+tmTime->tm_sec;
}

int iGoParse1MinFromStdin(char* pszSymbol, int iDebug, int iFmtId)
{
	char* pszDate;
	char* pszTime;
	char* pszTickPrc;
	char* pszTickVol;

	char szLine[4096];
	char delim[] = " ,";
	char* pszData[10];
	int iReadLine = 0;

	std::map<int, CTradeData> objTimeTradeData;
	typedef std::map<int, CTradeData>::iterator _MapItTimeTradeData;
	while(fgets(szLine, sizeof(szLine), stdin))
	{
		iReadLine++;
		char* pch = strtok(szLine, delim);
		int iIdx = 0;
		memset(pszData, 0x00, sizeof(pszData));
		while (pch != NULL)
		{
			pszData[iIdx++] = pch;
			pch = strtok(NULL, delim);
			if (iIdx >= 10)
				break;
		} 
		if (iDebug && iReadLine%5000 == 0)
		{
			printf("Parsed %d Lines...\n", iReadLine);
		}
		pszDate = pszData[0];
		pszTime = pszData[1];
		pszTickPrc = pszData[2];
		pszTickVol = pszData[3];
		int iDataTradeDate = atoi(pszDate);
		int iTradeTime = atof(pszTime);
		int iEncodeTradeDateTime = getMinEpochFromDateTime(iDataTradeDate, iTradeTime)+1;//+1min 
		double dbCurPrice = atof(pszTickPrc);
		if (dbCurPrice == 0.0)
		{
			continue;
		}
		CTradeData* pTradeData = &(objTimeTradeData[iEncodeTradeDateTime]);
		if (pTradeData->dbOpen == 0)
		{
			pTradeData->dbOpen = pTradeData->dbHigh = pTradeData->dbLow = pTradeData->dbClose = dbCurPrice;
			if (pszTickVol!=NULL)
				pTradeData->dbVol = atoi(pszTickVol);
			else
				pTradeData->dbVol = 0;
		}
		else
		{
			if (dbCurPrice > pTradeData->dbHigh)
				pTradeData->dbHigh = dbCurPrice;
			if (dbCurPrice < pTradeData->dbLow)
				pTradeData->dbLow = dbCurPrice;
			pTradeData->dbClose = dbCurPrice;
			if (pszTickVol!=NULL)
				pTradeData->dbVol += atoi(pszTickVol);
			else
                                pTradeData->dbVol = 0;
		}
	}

	_MapItTimeTradeData mapItTimeTradeData;
	if(!objTimeTradeData.empty())
	{
		for(mapItTimeTradeData = objTimeTradeData.begin();mapItTimeTradeData!=objTimeTradeData.end();mapItTimeTradeData++)
		{
			const int* piEncodeTradeDateTime = &(*mapItTimeTradeData).first;
			int iTradingDate,iTradingTime;
			vGetDateTimeFromMinEpoch(*piEncodeTradeDateTime, &iTradingDate, &iTradingTime);
			CTradeData* pTradeData = &(*mapItTimeTradeData).second;
			if (iFmtId == 1)
				fprintf(stdout, "%04d-%02d-%02d %02d:%02d:00,%s,%s,%s,%s,%d\n", iTradingDate/10000, (iTradingDate/100)%100, iTradingDate%100, iTradingTime/10000, (iTradingTime/100)%100, 
				cszCutDouble(pTradeData->dbOpen).c_str(), cszCutDouble(pTradeData->dbHigh).c_str(), cszCutDouble(pTradeData->dbLow).c_str(), cszCutDouble(pTradeData->dbClose).c_str(), (int)pTradeData->dbVol);
			else
				fprintf(stdout, "%04d%02d%02d,%02d%02d00,%s,%s,%s,%s,%d\n", iTradingDate/10000, (iTradingDate/100)%100, iTradingDate%100, iTradingTime/10000, (iTradingTime/100)%100,
        	                cszCutDouble(pTradeData->dbOpen).c_str(), cszCutDouble(pTradeData->dbHigh).c_str(), cszCutDouble(pTradeData->dbLow).c_str(), cszCutDouble(pTradeData->dbClose).c_str(), (int)pTradeData->dbVol);
		}
	} 
	if (iDebug)
		printf("Output: %s Done!\n", pszSymbol);
	return iReadLine;
}

#ifdef _WINDOWS
int _tmain(int argc, TCHAR* argv[], TCHAR* envp[])
#else
int main(int argc, char* argv[])
#endif
{
	int nRetCode = 0;
#ifdef _WINDOWS
	// initialize MFC and print and error on failure
	if (!AfxWinInit(::GetModuleHandle(NULL), NULL, ::GetCommandLine(), 0))
	{
		// TODO: change error code to suit your needs
		printf("Fatal Error: MFC initialization failed\r\n");
		nRetCode = 1;
	}
#else
	if (false)
	{}
#endif
	else
	{
		int iDebug = 0;
		int i = 0;
		int iFmtId = 0;
		for (i=1;i<argc;++i)
		{
			if (strcasecmp(argv[i], "-D") == 0)
				iDebug = 1;
			if (strcasecmp(argv[i], "-F1") == 0)
				iFmtId = 1;
			if (strcasecmp(argv[i], "-H") == 0 || strcasecmp(argv[i], "-HELP") == 0)
			{
				printf("Use stdin to input tick data.\n"
					"date,time,tickprice,tickvol\n"
					"ie: 20150525,132339.950,9614.000000,1\n\n");
				printf("-D: show debug info\n");
				printf("-F0: output 'YYYYMMDD,HHMMSS,OPEN,HIGH,LOW,CLOSE,VOL' *default\n");
				printf("-F1: output 'YYYY-MM-DD HH:MM:SS,OPEN,HIGH,LOW,CLOSE,VOL'\n");
				exit(0);
			}
		}
		// TODO: code your application's behavior here.
		iGoParse1MinFromStdin((char*)"", iDebug, iFmtId);
	}

//iGoParse1Min("c:\\try\\WEBPXTICK_DT-20110418.txt", 20110418);
	return nRetCode;
}


