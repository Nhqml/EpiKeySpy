# EpiSpyKey

*A toy keylogger written in Python*

---

This software is for **education/research purposes only**. The author takes no
responsibility and/or liability for how you choose to use it.

---

## How to run

Download the project and simple run the module:

```bash
# Run the server
python -m epikeyspy server

python -m epikeyspy client 127.0.0.1:9999
```

## Customize what's printed

By default, the server will only print received events (e.g. keystrokes).
However, you can add your own event *consumer* by editing the file
`epikeyspy/consumers.py`.
