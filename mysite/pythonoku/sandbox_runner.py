"""Минимальный процесс выполнения учебного кода. Запускается только через code_checker."""
import ast
import io
import json
import sys


MAX_CODE_LENGTH = 12_000
MAX_AST_NODES = 2_500
MAX_OUTPUT_LENGTH = 20_000
MAX_RANGE_LENGTH = 100_000

BLOCKED_NODES = (
    ast.Import, ast.ImportFrom, ast.ClassDef, ast.AsyncFunctionDef,
    ast.With, ast.AsyncWith, ast.Global, ast.Nonlocal, ast.Delete,
    ast.Try, ast.Raise, ast.Yield, ast.YieldFrom, ast.Await,
)
BLOCKED_NAMES = {
    'open', 'exec', 'eval', 'compile', '__import__', 'globals', 'locals', 'vars',
    'getattr', 'setattr', 'delattr', 'breakpoint', 'help', 'memoryview', 'exit', 'quit',
}
ALLOWED_ATTRIBUTES = {
    'upper', 'lower', 'casefold', 'count', 'replace', 'split', 'strip', 'lstrip', 'rstrip',
    'startswith', 'endswith', 'isdigit', 'isalpha', 'isalnum', 'append', 'extend', 'insert',
    'remove', 'pop', 'sort', 'reverse', 'index', 'keys', 'values', 'items', 'get', 'copy',
}


class SandboxViolation(Exception):
    pass


def validate_source(source):
    if len(source) > MAX_CODE_LENGTH:
        raise SandboxViolation('Код слишком длинный (максимум 12 000 символов).')
    try:
        tree = ast.parse(source, mode='exec')
    except SyntaxError as error:
        line = error.lineno or 1
        raise SandboxViolation(f'Синтаксическая ошибка в строке {line}: {error.msg}') from error

    nodes = list(ast.walk(tree))
    if len(nodes) > MAX_AST_NODES:
        raise SandboxViolation('Программа слишком большая для учебной проверки.')

    for node in nodes:
        if isinstance(node, BLOCKED_NODES):
            raise SandboxViolation('В этой задаче запрещены импорты, файлы и системные операции.')
        if isinstance(node, ast.Name) and (node.id in BLOCKED_NAMES or node.id.startswith('__')):
            raise SandboxViolation(f'Использование «{node.id}» запрещено в проверяемом коде.')
        if isinstance(node, ast.Attribute):
            if node.attr.startswith('__') or node.attr not in ALLOWED_ATTRIBUTES:
                raise SandboxViolation(f'Метод «{node.attr}» недоступен в учебной среде.')
        if isinstance(node, (ast.FunctionDef, ast.Lambda)):
            decorators = getattr(node, 'decorator_list', [])
            if decorators:
                raise SandboxViolation('Декораторы недоступны в учебной среде.')
    return tree


def limited_range(*args):
    value = range(*args)
    if len(value) > MAX_RANGE_LENGTH:
        raise SandboxViolation('range содержит слишком много значений.')
    return value


def run(payload):
    source = str(payload.get('code', ''))
    input_lines = str(payload.get('input', '')).splitlines()
    input_position = 0
    output = io.StringIO()

    tree = validate_source(source)

    def safe_input(prompt=''):
        nonlocal input_position
        if input_position >= len(input_lines):
            raise EOFError('Программа запросила больше данных, чем дано в тесте.')
        value = input_lines[input_position]
        input_position += 1
        return value

    def safe_print(*values, sep=' ', end='\n', file=None, flush=False):
        if file is not None:
            raise SandboxViolation('Вывод в файл запрещён.')
        output.write(str(sep).join(str(value) for value in values) + str(end))
        if output.tell() > MAX_OUTPUT_LENGTH:
            raise SandboxViolation('Программа вывела слишком много текста.')

    safe_builtins = {
        'input': safe_input, 'print': safe_print, 'int': int, 'float': float, 'str': str,
        'bool': bool, 'len': len, 'min': min, 'max': max, 'abs': abs, 'round': round,
        'sum': sum, 'range': limited_range, 'enumerate': enumerate, 'zip': zip,
        'list': list, 'tuple': tuple, 'dict': dict, 'set': set, 'sorted': sorted,
        'all': all, 'any': any, 'reversed': reversed,
    }
    namespace = {'__builtins__': safe_builtins, '__name__': '__main__'}
    exec(compile(tree, '<solution.py>', 'exec'), namespace, namespace)
    return output.getvalue()


def main():
    try:
        payload = json.loads(sys.stdin.read())
        result = {'ok': True, 'output': run(payload)}
    except SandboxViolation as error:
        result = {'ok': False, 'error': str(error)}
    except Exception as error:
        result = {'ok': False, 'error': f'{type(error).__name__}: {error}'}
    sys.stdout.write(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    main()
