# json-log-search

Search and filter JSON logs. 

```
  --where ['NAME=VALUE'] [['NAME=VALUE'] ...]
                        Filter to lines which contain NAME[=VALUE]
  --where-not ['NAME=VALUE'] [['NAME=VALUE'] ...]
                        Filter to lines which do not contain NAME[=VALUE].
                        Overrides --where.
  --show PARAM [PARAM ...]
                        Show only parameter PARAM in output
  --delimiter DELIMITER
                        Delimiter between parameters in output, default tab.
                        Only used together with --show parameter
  --squash-typeinfo SQUASH_TYPEINFO
                        Change parameters on the form blah : {"int" : 12345}
                        to blah : 12345. Types are int, string, array
  --add-type ADD_TYPE   Add type TYPE to types to squash.
```

## Example

Example data

```
{ 'campaign_id' : {'int' : 12345}, 'ip' : {'string' : '10.0.0.1'}, 'user_agent' : {'string' : 'Mozilla/5.0 (Windows NT 6.1; rv:41.0) Gecko/20100101 Firefox/41.0'}, 'browser' : {'string' : 'Firefox' } }
{ 'campaign_id' : {'int' : 12345}, 'ip' : {'string' : '127.0.0.1'}, 'user_agent' : {'string' : 'Mozilla/5.0 (iPad; CPU OS 9_2_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13D15 Safari/601.1'}, 'browser' : {'string' : 'Mobile Safari' } }
```


`prositen@home>./json-log-search example.json --where campaign_id=12345 --show ip user_agent`

```
ip=10.0.0.1 user_agent=Mozilla/5.0 (Windows NT 6.1; rv:41.0) Gecko/20100101 Firefox/41.0
ip=127.0.0.1  user_agent=Mozilla/5.0 (iPad; CPU OS 9_2_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13D15 Safari/601.1
```

`prositen@home>./json-log-search example.json --where ip=10.0.0.1`

```
{ 'campaign_id' : 12345, 'ip' : '10.0.0.1', 'user_agent' : 'Mozilla/5.0 (Windows NT 6.1; rv:41.0) Gecko/20100101 Firefox/41.0', 'browser' : 'Firefox' } }
```
