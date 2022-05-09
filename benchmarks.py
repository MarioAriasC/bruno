import time


def _measure(body):
    start = time.perf_counter()
    result = body()
    diff = time.perf_counter() - start
    print(f"{result.value!r}, duration={diff}")


def _fast_input(size):
    return """
    let fibonacci = fn(x) {
    if (x < 2) {
    	return x;
    } else {
    	fibonacci(x - 1) + fibonacci(x - 2);
    }
};
fibonacci(""" + size + """);"""
