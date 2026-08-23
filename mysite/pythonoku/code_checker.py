"""Запуск тестов учебной задачи в отдельном ограниченном Python-процессе."""
import json
import subprocess
import sys
from pathlib import Path


RUNNER = Path(__file__).with_name('sandbox_runner.py')
TEST_TIMEOUT_SECONDS = 2
MAX_TESTS = 12


def normalize_output(value):
    lines = [line.rstrip() for line in str(value).replace('\r\n', '\n').split('\n')]
    while lines and not lines[0]:
        lines.pop(0)
    while lines and not lines[-1]:
        lines.pop()
    return '\n'.join(lines)


def run_case(code, test_input):
    command = [sys.executable, '-X', 'utf8', '-I', '-S', str(RUNNER)]
    creation_flags = getattr(subprocess, 'CREATE_NO_WINDOW', 0)
    try:
        completed = subprocess.run(
            command,
            input=json.dumps({'code': code, 'input': test_input}, ensure_ascii=False),
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=TEST_TIMEOUT_SECONDS,
            creationflags=creation_flags,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return {'ok': False, 'error': 'Превышено время выполнения (2 секунды). Возможно, в коде бесконечный цикл.'}

    if completed.returncode != 0:
        return {'ok': False, 'error': 'Среда проверки не смогла запустить программу.'}
    try:
        return json.loads(completed.stdout)
    except json.JSONDecodeError:
        return {'ok': False, 'error': 'Программа нарушила формат ответа среды проверки.'}


def check_code(code, tests):
    if not isinstance(code, str) or not code.strip():
        return {'passed': False, 'results': [], 'error': 'Сначала напишите решение.'}
    if not isinstance(tests, list) or not tests:
        return {'passed': False, 'results': [], 'error': 'Учитель ещё не добавил тесты к этой задаче.'}

    results = []
    checker_error = ''
    for index, test in enumerate(tests[:MAX_TESTS], 1):
        test_input = str(test.get('input', ''))
        expected_values = test.get('expected', '')
        if not isinstance(expected_values, list):
            expected_values = [expected_values]
        normalized_expected = [normalize_output(item) for item in expected_values]
        execution = run_case(code, test_input)
        hidden = bool(test.get('hidden', False))

        if execution.get('ok'):
            actual = normalize_output(execution.get('output', ''))
            passed = actual in normalized_expected
            error = ''
        else:
            actual = ''
            passed = False
            error = execution.get('error', 'Неизвестная ошибка выполнения.')
            checker_error = checker_error or error

        results.append({
            'number': index,
            'passed': passed,
            'hidden': hidden,
            'input': None if hidden else test_input,
            'expected': None if hidden else normalize_output(expected_values[0]),
            'actual': None if hidden else actual,
            'error': error,
        })
        if error:
            break

    return {
        'passed': bool(results) and len(results) == min(len(tests), MAX_TESTS) and all(item['passed'] for item in results),
        'results': results,
        'error': checker_error,
    }
