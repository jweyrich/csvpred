# csvpred

Query a CSV file using simple predicates.

## How to install

```shell
cd csvpred
brew install pipenv
pipenv install
```

## How to use

Examples:

```shell
pipenv run python3 -m csvpred -i samples/hurricanes.csv -q '.Month == Aug' --debug-ast | jq
pipenv run python3 -m csvpred -i samples/hurricanes.csv -q '.Average == 0.5' --debug-ast | jq
pipenv run python3 -m csvpred -i samples/hurricanes.csv \
  -f month,avg,2005,2006,2007,2008,2009,2010,2011,2012,2013,2014,2015 \
  -q '.month == Aug'
pipenv run python3 -m csvpred -i samples/hurricanes.csv \
  -f month,avg,2005,2006,2007,2008,2009,2010,2011,2012,2013,2014,2015 \
  -q '.avg == 0.5'
```
