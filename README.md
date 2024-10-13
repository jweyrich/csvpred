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
pipenv run python3 -m csvpred -i samples/hurricanes.csv -f 'Month == Aug'
pipenv run python3 -m csvpred -i samples/hurricanes.csv -f 'Average == "0.5"'
```
