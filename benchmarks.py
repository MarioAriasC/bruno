import time

from evaluator import Environment, evaluate
from lexer import Lexer
from parser import Parser


def _measure(body):
    start = time.perf_counter()
    result = body()
    diff = time.perf_counter() - start
    print(f"{result.value!r}, duration={diff}")


def _fast_input(size):
    return (
            """
            let fibonacci = fn(x) {
            if (x < 2) {
                return x;
            } else {
                fibonacci(x - 1) + fibonacci(x - 2);
            }
        };
        fibonacci("""
            + str(size)
            + """);"""
    )


def _tab(size):
    return (
            """
            let fibRec = fn(n, buf) {
          if(n > 2) {
            let res = buf[0] + buf[1];
            return fibRec(n - 1, [res, buf[0]]);  
          }
          return buf;
        }                        
                                
                                
        let fibonacci = fn(x) {
          let res = [1,1]
          return fibRec(x, res)[0]
        }
        
        fibonacci("""
            + str(size)
            + """);"""
    )


def _parse(input_source):
    lexer = Lexer(input_source)
    parser = Parser(lexer)
    return parser.parse_program()


def main():
    env = Environment()
    _measure(lambda: evaluate(_parse(_fast_input(35)), env))


if __name__ == "__main__":
    main()
