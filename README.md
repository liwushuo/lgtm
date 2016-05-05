# lgtm

## Introduction

`lgtm` is a simple pull request approval system.
`lgtm` can auto merge pull request, if there are enough workmates commenting `lgtm` in the pull request.

## Usage

Add `lgtm.yml` in your root directory:

```yaml
logging:
  level: info
github:
  token: REPLACE_YOUR_TOKEN
  url: https://github-enterprise.your-company.com/api/v3
  terms:
    - lgtm
    - ':shipit:'
  include_self: true
  approve_number: 3
  repos:
    org/repo:
      - maintainer1
      - maintainer2
      - maintainer3
      - maintainer4
```

Run:

    $ virtualenv venv
    $ source venv/bin/activate
    (venv) $ pip install -r requirements.txt
    (venv)$ python app.py 8888
    INFO:lgtm:lws/cambridge pull 1077 merged.
    DEBUG:lgtm:lws/cambridge pull 1058 has not been approved.
    DEBUG:lgtm:lws/cambridge pull 888 is not mergeable.
    DEBUG:lgtm:scanned lws/cambridge at 2016-05-05 04:51:55.671038
