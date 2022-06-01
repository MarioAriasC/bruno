# Bruno

[Python 3.10](https://www.python.org/) implementation of
the [Monkey Language](https://monkeylang.org/)

Bruno has many sibling implementations

* Kotlin: [monkey.kt](https://github.com/MarioAriasC/monkey.kt)
* Crystal: [Monyet](https://github.com/MarioAriasC/monyet)
* Scala 3: [Langur](https://github.com/MarioAriasC/langur)
* Ruby 3: [Pepa](https://github.com/MarioAriasC/pepa)

## Status

The book ([Writing An Interpreter In Go](https://interpreterbook.com/)) is fully implemented. Bruno will not have a
compiler implementation

## Commands

Run pip install first 

```shell
python -m pip install -r requirements.txt
```

| Script                                  | Description                                        |
|-----------------------------------------|----------------------------------------------------|
| `pytest`                                | Run tests                                          |
| [`python benchmarks.py`](benchmarks.py) | Run the classic monkey benchmark (`fibonacci(35)`) |
| [`python repl.py`](repl.py)             | Run the Bruno REPL                                 |
