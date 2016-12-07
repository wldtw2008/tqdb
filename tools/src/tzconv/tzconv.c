#include <time.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define NEWLINE "\n"
void vConv(int iDbgInfo, char* szSrcDateTime, char* szSrcTZ, char* szTrgTz, int iOutputFormat)
{
	char szEnv[64];
	
	struct tm mytm = {0};
	time_t mytime;
	char buf[100];

	if (iDbgInfo)
		printf("TZ from: %s to: %s"NEWLINE, szSrcTZ, szTrgTz);
	
	mytm.tm_isdst = -1;
	sprintf(szEnv, "TZ=%s", szSrcTZ);
	putenv(szEnv);
	tzset();
	strptime(szSrcDateTime, "%Y-%m-%d %H:%M:%S", &mytm);
	mytime = mktime(&mytm);

	if (iDbgInfo)
	{
		strftime(buf, 100, "%Y-%m-%d %H:%M:%S %z(%Z)", &mytm);		
		printf("%s --> %d(UnixEpoch) --> ", buf, (long)mytime);
	}
	
	
	sprintf(szEnv, "TZ=%s", szTrgTz);
	putenv(szEnv);
	tzset();
	localtime_r(&mytime, &mytm);
	if (iDbgInfo) {
		strftime(buf, 100, "%Y-%m-%d %H:%M:%S %z(%Z)", &mytm);
		printf("%s"NEWLINE, buf, (long)mytime);
	} 
	switch(iOutputFormat)
	{
		default:
		case 0:
			strftime(buf, 100, "%Y-%m-%d %H:%M:%S"NEWLINE, &mytm);
			break;
		case 1:
			strftime(buf, 100, "%Y%m%d %H%M%S"NEWLINE, &mytm);
			break;
	}
	printf(buf);
}
void trimRight(char* psz)
{
	char trim[] = " \t\r\n";
	for (int i=0;i<strlen(trim);++i)
	{
		char* pTmp = strchr(psz, trim[i]);
		if (pTmp != NULL)
			*pTmp = '\0';
	}
}
void vIfTZisLocal(char* psz)
{
	char szLocal[32];
	if (strcasecmp(psz, "local") == 0)
	{
		FILE* fp = fopen("/etc/timezone", "r");
		if (fp != NULL)
		{
			fread(szLocal, 1, sizeof(szLocal), fp);
			fclose(fp);
			strcpy(psz, szLocal);
		}
	}
	trimRight(psz);

}
int main (int argc, char *argv[])
{
	if (argc > 1 && strcmp(argv[1], "-h") == 0){
		printf("Systex Error!"NEWLINE);
		printf("%s -s SRC_TZ -t TRG_TZ DateTime"NEWLINE, argv[0]);
		printf("-h: Show this help"NEWLINE);
		printf("-s: Sourct TimeZone"NEWLINE);
		printf("-t: Target TimeZone"NEWLINE);
		printf("-v: Show Debug info"NEWLINE);
		printf("-f: Output datetime format"NEWLINE);
		printf("    -f 0: YYYY-mm-DD HH:MM:SS"NEWLINE);
		printf("    -f 1: YYYYmmDD HHMMSS"NEWLINE);
		printf("-tz: Show all support timezone"NEWLINE);
		printf("-stdin: get input from stdin"NEWLINE);
		printf("  ex: %s -f 1 -s 'America/New_York' -t 'Asia/Taipei' '2014-01-2 04:15'"NEWLINE, argv[0]);
		exit(0);
	}
	char szSrcTZ[32] = "UTC";
	char szTrgTz[32] = "UTC";
	char szSrcDateTime[32];
	int iDbgInfo=0;
	int iFromStdin=0;
	int iOutputFormat = 0;
	int i;
	for (i=0;i<argc;++i){
		if (strcmp(argv[i], "-s") == 0 && i<argc-1){
			strcpy(szSrcTZ, argv[i+1]);
			vIfTZisLocal(szSrcTZ);
			i++;
		} else if (strcmp(argv[i], "-t") == 0 && i<argc-1){
			strcpy(szTrgTz, argv[i+1]);
			vIfTZisLocal(szTrgTz);
			i++;
		} else if (strcmp(argv[i], "-v") == 0){
			iDbgInfo = 1;
		} else if (strcmp(argv[i], "-tz") == 0){
			char szCMD[] = "find /usr/share/zoneinfo/ -type f -follow |sed 's/\\/usr\\/share\\/zoneinfo\\///' | sed 's/^right\\///' | sed 's/^posix\\///' | sort | uniq";
			//char szCMD[] = "cat /usr/share/zoneinfo/zone.tab | awk '{if (substr($0,1,1)!=\"#\"){print $3}}' | sort";
			system(szCMD);
			exit(0);
		} else if (strcmp(argv[i], "-stdin") == 0){
			iFromStdin = 1;
		} else if (strcmp(argv[i], "-f") == 0 && i<argc-1){
			iOutputFormat = atoi(argv[i+1]);
			i++;
		}
	}
	trimRight(szSrcTZ);
	trimRight(szTrgTz);
	int iCount = 0;
	while(1)
	{
		if (iFromStdin == 0) {
			if (iCount>0)
				break;
			strcpy(szSrcDateTime, argv[argc-1]);
		} else {
			szSrcDateTime[0] = '\0';
			fgets(szSrcDateTime, sizeof(szSrcDateTime), stdin);
			szSrcDateTime[sizeof(szSrcDateTime)-1] = '\0';
			if (strlen(szSrcDateTime)<8)
				break;
		}
		char* pszSplit = strchr(szSrcDateTime, '\r');
		if (pszSplit!=NULL) *pszSplit = '\0';
		pszSplit = strchr(szSrcDateTime, '\n');
		if (pszSplit!=NULL) *pszSplit = '\0';
	
		vConv(iDbgInfo, szSrcDateTime, szSrcTZ, szTrgTz, iOutputFormat);
		iCount++;
	}
	return 0;
}
