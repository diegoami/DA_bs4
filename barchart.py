import requests


financial = requests.get("https://core-api.barchart.com/v1/options/chain?symbol=SPY&fields=strikePrice%2ClastPrice%2CpercentFromLast%2CbidPrice%2Cmidpoint%2CaskPrice%2CpriceChange%2CpercentChange%2Cvolatility%2Cvolume%2CopenInterest%2CoptionType%2CdaysToExpiration%2CexpirationDate%2CsymbolCode%2CsymbolType&groupBy=optionType&expirationDate=2017-08-04&raw=1&meta=field.shortName%2Cfield.type%2Cfield.description)")

print(financial.json().keys())
