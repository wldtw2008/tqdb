const char* szDb2Str(char *pszDB, double* pdbVal);
void vEpoch2DateTime(const double* pdbEpoch, int* piDate, int* piTime, int* piMSec);
char* szGetValueByKey(const char* szLine, const char* szKey, char* szValue, const char* szDefaultValue);
long long llGetCurrentEpoch();
void vMyLog(FILE*fp, int iLogType, const char* cmd, ...);
#define max(a,b) ((a)>(b)?(a):(b))
