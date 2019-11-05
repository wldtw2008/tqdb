#include <string>
#include <map>
#include <vector>

const char* szDb2Str(char *pszDB, double* pdbVal);
void vEpoch2DateTime(const double* pdbEpoch, int* piDate, int* piTime, int* piMSec);
char* szGetValueByKey(const char* szLine, const char* szKey, char* szValue, const char* szDefaultValue);
long long llGetCurrentEpoch();
long long llGetEpoch(int iYYYYMMDD, int iHHmmSSsss);
void vMyLog(FILE*fp, int iLogType, const char* cmd, ...);

typedef struct {
    std::string symbol;
    std::map<std::string, std::string> mapKeyVal;
}ST_SymbolInfo;
int iQAllSymbol(std::vector<ST_SymbolInfo>* pvecSymbolInfo, const char *pszTQDB, CassSession* session, CassCluster* cluster);
int iUpdateSymbol(ST_SymbolInfo* pSymbolInfo, const char *pszTQDB, CassSession* session, CassCluster* cluster);




#define max(a,b) ((a)>(b)?(a):(b))
