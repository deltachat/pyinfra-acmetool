# pyinfra module to deploy acmetool

This module deploys [acmetool]

It can be used from the Python code like this:
```python
from pyinfra_acmetool import deploy_acmetool

deploy_acmetool()
```

It can also be used to deploy acmetool with an ad-hoc command like this:
```
pyinfra --ssh-user root example.org pyinfra_acmetool.deploy_acmetool
```

[acmetool]: https://hlandau.github.io/acmetool/
