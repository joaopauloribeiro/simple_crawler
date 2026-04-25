"""
Interactive quiz: Python concepts introduced between 2012 and today.

Run:
    python quiz/python_concepts_quiz.py
    python quiz/python_concepts_quiz.py --shuffle
    python quiz/python_concepts_quiz.py --topic pathlib
"""
import argparse
import random
from dataclasses import dataclass, field


@dataclass
class Question:
    topic: str
    version: str
    question: str
    choices: list[str]
    correct: int          # 0-indexed
    explanation: str
    code_example: str


QUESTIONS: list[Question] = [
    # ── Python 3.4 ─────────────────────────────────────────────────────
    Question(
        topic="pathlib",
        version="3.4",
        question="Which expression reads a text file using pathlib (introduced in 3.4)?",
        choices=[
            "open('data.txt').read()",
            "Path('data.txt').read_text()",
            "pathlib.read('data.txt')",
            "file('data.txt').text()",
        ],
        correct=1,
        explanation=(
            "pathlib.Path gives files and directories a proper object interface. "
            "read_text() opens, reads, and closes the file in one call."
        ),
        code_example=(
            "from pathlib import Path\n\n"
            "content = Path('data.txt').read_text(encoding='utf-8')\n"
            "Path('output.txt').write_text('hello', encoding='utf-8')\n"
            "p = Path('html') / 'index.html'   # '/' joins paths"
        ),
    ),
    Question(
        topic="asyncio",
        version="3.4",
        question="What is the primary purpose of asyncio?",
        choices=[
            "Run Python on multiple CPU cores simultaneously",
            "Write concurrent I/O-bound code using a single thread and an event loop",
            "Replace the GIL with true parallelism",
            "Compile Python to machine code at runtime",
        ],
        correct=1,
        explanation=(
            "asyncio enables cooperative multitasking: coroutines voluntarily yield "
            "control while waiting for I/O (network, disk), letting other coroutines run. "
            "It does not bypass the GIL or use multiple threads."
        ),
        code_example=(
            "import asyncio\n\n"
            "async def fetch(url: str) -> str:\n"
            "    await asyncio.sleep(1)   # simulates I/O wait\n"
            "    return f'got {url}'\n\n"
            "async def main():\n"
            "    results = await asyncio.gather(\n"
            "        fetch('http://a.com'),\n"
            "        fetch('http://b.com'),\n"
            "    )\n"
            "    print(results)\n\n"
            "asyncio.run(main())"
        ),
    ),
    Question(
        topic="enum",
        version="3.4",
        question="What does Python's enum.Enum provide that a plain dict or set of constants does not?",
        choices=[
            "Faster lookup — O(1) vs O(n)",
            "Named, type-safe symbolic constants with iteration and comparison support",
            "Automatic serialisation to JSON",
            "Constants that can be used as dict keys",
        ],
        correct=1,
        explanation=(
            "Enum members are objects with a .name and .value, can be iterated, "
            "compared with 'is', and are recognised by type checkers — "
            "unlike bare strings or integers."
        ),
        code_example=(
            "from enum import Enum\n\n"
            "class Status(Enum):\n"
            "    OK      = 'ok'\n"
            "    FAILED  = 'failed'\n"
            "    SKIPPED = 'skipped'\n\n"
            "s = Status.OK\n"
            "print(s.name)   # 'OK'\n"
            "print(s.value)  # 'ok'\n"
            "print(s is Status.OK)  # True"
        ),
    ),
    # ── Python 3.5 ─────────────────────────────────────────────────────
    Question(
        topic="type hints",
        version="3.5",
        question="Which function signature uses correct Python type hints (PEP 484, 3.5)?",
        choices=[
            "def greet(name: String) -> String:",
            "def greet(name: str) -> str:",
            "def greet(name) -> 'str':",
            "def greet(@str name) -> @str:",
        ],
        correct=1,
        explanation=(
            "Type hints use Python's built-in types directly (str, int, list, etc.). "
            "They are not enforced at runtime but enable static analysis with mypy/pyright."
        ),
        code_example=(
            "def add(x: int, y: int) -> int:\n"
            "    return x + y\n\n"
            "def find(items: list[str], query: str) -> str | None:\n"
            "    return next((i for i in items if query in i), None)"
        ),
    ),
    # ── Python 3.6 ─────────────────────────────────────────────────────
    Question(
        topic="f-strings",
        version="3.6",
        question="Which is a valid f-string that produces 'Hello, Alice! You are 30.'?",
        choices=[
            '"Hello, {name}! You are {age}."',
            'f"Hello, {name}! You are {age}."',
            '"Hello, %s! You are %d." % (name, age)',
            '"Hello, {}! You are {}.".format(name, age)',
        ],
        correct=1,
        explanation=(
            "f-strings (formatted string literals) evaluate expressions inside {} "
            "at runtime. They are faster than .format() and more readable. "
            "Any valid Python expression works inside the braces."
        ),
        code_example=(
            "name, age = 'Alice', 30\n"
            "print(f'Hello, {name}! You are {age}.')   # Hello, Alice! You are 30.\n"
            "print(f'{2 + 2}')                          # 4\n"
            "print(f'{name.upper()!r}')                 # 'ALICE'"
        ),
    ),
    # ── Python 3.7 ─────────────────────────────────────────────────────
    Question(
        topic="dataclasses",
        version="3.7",
        question="What does @dataclass automatically generate for a class?",
        choices=[
            "Only __str__ and __repr__",
            "__init__, __repr__, and __eq__ based on annotated fields",
            "A full ORM mapping to a database table",
            "Thread-safe property accessors for every field",
        ],
        correct=1,
        explanation=(
            "@dataclass inspects class-level annotations and generates __init__, "
            "__repr__, and __eq__. Optional flags add __lt__/__gt__ (order=True), "
            "__hash__, and frozen (immutable) variants."
        ),
        code_example=(
            "from dataclasses import dataclass, field\n\n"
            "@dataclass\n"
            "class Seed:\n"
            "    url: str\n"
            "    depth: int = 2\n"
            "    tags: list[str] = field(default_factory=list)\n\n"
            "s = Seed('https://example.com')\n"
            "print(s)  # Seed(url='https://example.com', depth=2, tags=[])"
        ),
    ),
    Question(
        topic="breakpoint",
        version="3.7",
        question="What does the built-in breakpoint() function do?",
        choices=[
            "Raises a BreakpointException to pause execution",
            "Drops into the debugger (pdb by default) at the call site",
            "Prints a stack trace and exits",
            "Sets a performance checkpoint for profiling",
        ],
        correct=1,
        explanation=(
            "breakpoint() is equivalent to import pdb; pdb.set_trace() but shorter "
            "and configurable via the PYTHONBREAKPOINT env var "
            "(set it to '0' to disable all breakpoints in production)."
        ),
        code_example=(
            "def process(data):\n"
            "    result = transform(data)\n"
            "    breakpoint()   # drops into pdb here\n"
            "    return result\n\n"
            "# Disable in CI:\n"
            "# PYTHONBREAKPOINT=0 python script.py"
        ),
    ),
    # ── Python 3.8 ─────────────────────────────────────────────────────
    Question(
        topic="walrus operator",
        version="3.8",
        question="What does the walrus operator := do?",
        choices=[
            "Compares two values and returns the larger one",
            "Assigns a value and returns it as part of a larger expression",
            "Creates a deep copy of the right-hand operand",
            "Declares a constant that cannot be rebound",
        ],
        correct=1,
        explanation=(
            "The walrus operator (:=, PEP 572) assigns a value to a variable "
            "while also returning that value, enabling assignment inside "
            "conditions and comprehensions without extra lines."
        ),
        code_example=(
            "# Without walrus: read, check, use — three steps\n"
            "line = file.readline()\n"
            "while line:\n"
            "    process(line)\n"
            "    line = file.readline()\n\n"
            "# With walrus: one step\n"
            "while line := file.readline():\n"
            "    process(line)\n\n"
            "# Also useful in comprehensions\n"
            "results = [y for x in data if (y := expensive(x)) > 0]"
        ),
    ),
    Question(
        topic="f-string debugging",
        version="3.8",
        question="What does f'{value=}' print when value = 42?",
        choices=[
            "42",
            "value=42",
            "value == 42",
            "True",
        ],
        correct=1,
        explanation=(
            "The = specifier inside an f-string (3.8+) prints both the expression "
            "text and its value, making it ideal for quick debugging without typing "
            "the variable name twice."
        ),
        code_example=(
            "x = 42\n"
            "result = x * 2\n"
            "print(f'{x=}')       # x=42\n"
            "print(f'{result=}')  # result=84\n"
            "print(f'{x + 1=}')  # x + 1=43"
        ),
    ),
    # ── Python 3.9 ─────────────────────────────────────────────────────
    Question(
        topic="built-in generics",
        version="3.9",
        question="Which type hint syntax was made valid for plain annotations in Python 3.9?",
        choices=[
            "List[int] from typing",
            "list[int] directly (no import needed)",
            "Array<int> like Java",
            "[int] shorthand",
        ],
        correct=1,
        explanation=(
            "In 3.9 built-in types became generic: list[int], dict[str, int], "
            "tuple[str, ...], etc. The typing.List, typing.Dict equivalents still "
            "work but are no longer needed for annotations."
        ),
        code_example=(
            "# Before 3.9 — required import\n"
            "from typing import List, Dict, Optional\n"
            "def f(items: List[str]) -> Dict[str, int]: ...\n\n"
            "# 3.9+ — use built-ins directly\n"
            "def f(items: list[str]) -> dict[str, int]: ...\n"
            "def g(x: int | None) -> list[str]: ..."
        ),
    ),
    Question(
        topic="dict merge",
        version="3.9",
        question="What does dict_a | dict_b produce in Python 3.9+?",
        choices=[
            "The set of keys that appear in both dicts",
            "A new dict with entries from both; dict_b values win on conflicts",
            "An in-place update of dict_a",
            "A SyntaxError — | is only for sets",
        ],
        correct=1,
        explanation=(
            "The | operator creates a new merged dict (PEP 584). "
            "|= updates in-place. dict_b values take precedence for duplicate keys. "
            "This replaces the verbose {**a, **b} pattern."
        ),
        code_example=(
            "defaults = {'timeout': 10, 'retries': 3}\n"
            "overrides = {'timeout': 30, 'verbose': True}\n\n"
            "config = defaults | overrides\n"
            "# {'timeout': 30, 'retries': 3, 'verbose': True}\n\n"
            "defaults |= overrides   # in-place update"
        ),
    ),
    Question(
        topic="str.removeprefix",
        version="3.9",
        question="What does 'https://example.com'.removeprefix('https://') return?",
        choices=[
            "''",
            "'example.com'",
            "'https://'",
            "Raises ValueError",
        ],
        correct=1,
        explanation=(
            "removeprefix() (and removesuffix()) were added in 3.9. "
            "They are safer than lstrip() or manual slicing because they only "
            "remove the exact prefix/suffix, not individual characters."
        ),
        code_example=(
            "url = 'https://example.com'\n"
            "print(url.removeprefix('https://'))   # example.com\n"
            "print(url.removeprefix('http://'))    # https://example.com (no match)\n\n"
            "filename = 'test_crawler.py'\n"
            "print(filename.removesuffix('.py'))   # test_crawler"
        ),
    ),
    Question(
        topic="functools.cache",
        version="3.9",
        question="What is functools.cache (added in 3.9) equivalent to?",
        choices=[
            "functools.lru_cache() with no size limit (maxsize=None)",
            "functools.lru_cache(maxsize=128)",
            "A thread-safe dict for storing computed results",
            "A disk-backed cache that persists between runs",
        ],
        correct=0,
        explanation=(
            "@cache is a simpler spelling of @lru_cache(maxsize=None). "
            "It keeps all results forever (unbounded), making it slightly faster "
            "than lru_cache because there is no eviction overhead."
        ),
        code_example=(
            "from functools import cache\n\n"
            "@cache\n"
            "def fibonacci(n: int) -> int:\n"
            "    if n < 2:\n"
            "        return n\n"
            "    return fibonacci(n - 1) + fibonacci(n - 2)\n\n"
            "print(fibonacci(100))  # instant after first call"
        ),
    ),
    # ── Python 3.10 ────────────────────────────────────────────────────
    Question(
        topic="match/case",
        version="3.10",
        question="Which best describes Python's structural pattern matching (match/case)?",
        choices=[
            "A faster alternative to if/elif chains, compiled to a jump table",
            "Destructuring + conditional dispatch on the shape and content of a value",
            "A string pattern matching engine like regex",
            "Syntactic sugar for switch statements identical to C/Java",
        ],
        correct=1,
        explanation=(
            "match/case (PEP 634) does structural pattern matching — it can "
            "destructure sequences, mappings, and class instances, guard with 'if', "
            "and capture sub-values. Much richer than a switch statement."
        ),
        code_example=(
            "def handle(event: dict):\n"
            "    match event:\n"
            "        case {'type': 'click', 'button': btn}:\n"
            "            print(f'Clicked button {btn}')\n"
            "        case {'type': 'key', 'key': 'q'}:\n"
            "            print('Quit')\n"
            "        case {'type': str(t)}:\n"
            "            print(f'Unknown event: {t}')\n"
            "        case _:\n"
            "            print('Not an event dict')"
        ),
    ),
    Question(
        topic="union types",
        version="3.10",
        question="In Python 3.10+, how do you annotate a parameter that can be str or None?",
        choices=[
            "Optional[str]  (from typing)",
            "str | None",
            "Union[str, NoneType]",
            "str? (nullable shorthand)",
        ],
        correct=1,
        explanation=(
            "PEP 604 allows X | Y union syntax in annotations without importing "
            "from typing. str | None replaces Optional[str]; "
            "int | str | float replaces Union[int, str, float]."
        ),
        code_example=(
            "# Before 3.10\n"
            "from typing import Optional, Union\n"
            "def find(name: Optional[str]) -> Union[int, str]: ...\n\n"
            "# 3.10+\n"
            "def find(name: str | None) -> int | str: ..."
        ),
    ),
    # ── Python 3.11 ────────────────────────────────────────────────────
    Question(
        topic="ExceptionGroup",
        version="3.11",
        question="What problem does ExceptionGroup (3.11) solve?",
        choices=[
            "Grouping unrelated exceptions into a single printable message",
            "Raising and catching multiple concurrent exceptions from tasks",
            "Creating exception hierarchies with shared base classes",
            "Suppressing exceptions inside context managers",
        ],
        correct=1,
        explanation=(
            "ExceptionGroup (PEP 654) lets you raise several exceptions at once "
            "and catch subsets of them with 'except*'. This is essential for "
            "asyncio task groups where multiple tasks can fail independently."
        ),
        code_example=(
            "# Raise a group of errors\n"
            "raise ExceptionGroup('fetch errors', [\n"
            "    ValueError('bad URL'),\n"
            "    TimeoutError('host unreachable'),\n"
            "])\n\n"
            "# Catch only the ones you handle\n"
            "try:\n"
            "    ...\n"
            "except* ValueError as eg:\n"
            "    print('Value errors:', eg.exceptions)\n"
            "except* TimeoutError as eg:\n"
            "    print('Timeouts:', eg.exceptions)"
        ),
    ),
    Question(
        topic="tomllib",
        version="3.11",
        question="What does the tomllib module (3.11) provide?",
        choices=[
            "A YAML parser for config files",
            "A read-only TOML parser in the standard library",
            "A template engine for .toml-based HTML",
            "Serialisation of Python dicts to the TOML format",
        ],
        correct=1,
        explanation=(
            "tomllib (PEP 680) adds TOML reading to the stdlib. It is read-only — "
            "for writing TOML use the third-party 'tomli-w' library. "
            "pyproject.toml files are valid TOML and can be read with tomllib."
        ),
        code_example=(
            "import tomllib\n\n"
            "with open('pyproject.toml', 'rb') as f:  # must open in binary mode\n"
            "    config = tomllib.load(f)\n\n"
            "print(config['project']['name'])\n\n"
            "# Also accepts a string:\n"
            "data = tomllib.loads('[server]\\nport = 8080')\n"
            "print(data['server']['port'])  # 8080"
        ),
    ),
    Question(
        topic="Self type",
        version="3.11",
        question="What is typing.Self used for?",
        choices=[
            "Accessing the current instance inside a lambda",
            "Annotating methods that return an instance of their own class",
            "Creating recursive type aliases",
            "Preventing subclassing of a class",
        ],
        correct=1,
        explanation=(
            "Self (PEP 673) annotates methods that return the actual type of "
            "'self' — crucial for fluent APIs and subclasses. "
            "Without it, a method annotated as returning 'MyClass' would break "
            "type checking when called on a subclass."
        ),
        code_example=(
            "from typing import Self\n\n"
            "class Builder:\n"
            "    def set_timeout(self, t: int) -> Self:\n"
            "        self.timeout = t\n"
            "        return self\n\n"
            "class FastBuilder(Builder):\n"
            "    pass\n\n"
            "# Type checker knows this is FastBuilder, not Builder\n"
            "b: FastBuilder = FastBuilder().set_timeout(5)"
        ),
    ),
    # ── Python 3.12 ────────────────────────────────────────────────────
    Question(
        topic="itertools.batched",
        version="3.12",
        question="What does itertools.batched('ABCDEFG', 3) yield?",
        choices=[
            "['A', 'B', 'C'], ['D', 'E', 'F'], ['G']",
            "('ABC', 'DEF', 'G')",
            "('A', 'D', 'G'), ('B', 'E'), ('C', 'F')",
            "A flat iterator with a batch counter attached",
        ],
        correct=0,
        explanation=(
            "itertools.batched() (PEP 679) chunks an iterable into tuples of at "
            "most n items. The last batch may be shorter. Replaces common "
            "recipes like [lst[i:i+n] for i in range(0, len(lst), n)]."
        ),
        code_example=(
            "from itertools import batched\n\n"
            "for batch in batched(range(10), 3):\n"
            "    print(batch)\n"
            "# (0, 1, 2)\n"
            "# (3, 4, 5)\n"
            "# (6, 7, 8)\n"
            "# (9,)\n\n"
            "# Great for bulk DB inserts:\n"
            "for chunk in batched(all_rows, 1000):\n"
            "    db.executemany(INSERT, chunk)"
        ),
    ),
]


def _run_quiz(questions: list[Question]) -> None:
    correct_count = 0
    total = len(questions)

    print("=" * 62)
    print("  Python Concepts Quiz — features introduced after 2012")
    print("=" * 62)
    print(f"  {total} questions  |  type the number of your answer\n")

    for idx, q in enumerate(questions, 1):
        print(f"── Q{idx}/{total}  [{q.topic}  Python {q.version}] " + "─" * 20)
        print(q.question)
        print()
        for i, choice in enumerate(q.choices, 1):
            print(f"  {i}. {choice}")
        print()

        while True:
            raw = input("Your answer (1–4): ").strip()
            if raw.isdigit() and 1 <= int(raw) <= len(q.choices):
                answer = int(raw) - 1
                break
            print("  Please enter a number between 1 and 4.")

        if answer == q.correct:
            print("\n  ✔  Correct!\n")
            correct_count += 1
        else:
            print(f"\n  ✘  Wrong. The correct answer was: {q.choices[q.correct]}\n")

        print(f"  Explanation: {q.explanation}\n")
        print("  Example:")
        for line in q.code_example.splitlines():
            print(f"    {line}")
        print()
        input("  [Enter to continue]")
        print()

    pct = correct_count / total * 100
    print("=" * 62)
    print(f"  Final score: {correct_count}/{total}  ({pct:.0f}%)")
    if pct == 100:
        print("  Outstanding — you know your modern Python!")
    elif pct >= 70:
        print("  Good work. Review the ones you missed.")
    else:
        print("  Keep studying — run the quiz again to reinforce.")
    print("=" * 62)


def main() -> None:
    parser = argparse.ArgumentParser(description="Python concepts quiz (post-2012)")
    parser.add_argument("--shuffle", action="store_true", help="Randomise question order")
    parser.add_argument(
        "--topic", metavar="NAME",
        help="Only questions for a specific topic (e.g. f-strings, pathlib)",
    )
    args = parser.parse_args()

    questions = list(QUESTIONS)
    if args.topic:
        questions = [q for q in questions if q.topic.lower() == args.topic.lower()]
        if not questions:
            topics = sorted({q.topic for q in QUESTIONS})
            print(f"No questions for topic '{args.topic}'.")
            print("Available topics:", ", ".join(topics))
            raise SystemExit(1)

    if args.shuffle:
        random.shuffle(questions)

    _run_quiz(questions)


if __name__ == "__main__":
    main()
