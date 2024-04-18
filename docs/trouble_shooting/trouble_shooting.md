# Trouble Shooting

2024.04.24

## 문제

커밋을 했는데 계속 Push가 거부되는 문제가 발생함

## 원인

git log를 통해 확인해보니 GitHub Personal Access Token이 커밋에 포함되어 있었기 때문에 GitHub에서 Push를 거부한 것으로 확인됨

## 해결

환경변수를 저장하는 .env 파일을 추가하여 GitHub Personal Access Token을 저장하고, python에서는 environ을 통해 .env 파일을 읽어오도록 설정함으로써 문제를 해결함

```bash
PAT=MY_PAT
```

```python
import os

env = os.environ
pat = env.get('PAT')
```
