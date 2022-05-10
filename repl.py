from evaluator import Environment, evaluate
from lexer import Lexer
from parser import Parser

PROMPT = ">>"


def main():
    env = Environment()
    # print(PROMPT)
    while True:
        code = input(PROMPT)
        lexer = Lexer(code)
        parser = Parser(lexer)
        program = parser.parse_program()

        if len(parser.errors()) > 0:
            print("Whoops! we ran into some monkey business here")
            print("parser errors:")
            for error in parser.errors():
                print(f"\t{error}")

        evaluated = evaluate(program, env)
        if evaluated is not None:
            print(f"{evaluated!r}")


if __name__ == "__main__":
    main()
