# notes

# 1st time install

remember to run `pdm install --plugins`

## bump version and deploy:

```bash
pdm bump patch --commit --tag
pdm publish
git push
```