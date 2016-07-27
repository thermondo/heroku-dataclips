heroku-dataclips
========================

A way to interact with the heroku dataclips private API

Good way to check if a file dataclip contains a certain table:
```shell
ag MY_TABLE_NAME -c --ignore *.sql | awk -F "/" '{print "https://dataclips.heroku.com/"$1"/" }'
```
