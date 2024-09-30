import json
from numbers import Number

import uvicorn

ENCODING = 'utf-8'
N_PARAM = 'n'


async def app(scope, receive, send) -> None:
    _type: str = scope['type']
    if not scope['type'] == 'http':
        await send_404(send)
        return

    method: str = scope['method']
    path: str = scope['path']

    if method == 'GET':
        if path == '/factorial':
            query_string = scope['query_string'].decode()
            await get_factorial(query_string, send)
            return
        elif path.startswith('/fibonacci'):
            await get_fibonacci(path, send)
            return
        elif path == '/mean':
            await get_mean(receive, send)
            return

    await send_404(send)


async def get_factorial(query_string: str, send):
    params = dict()
    query_args = query_string.split('&')
    for arg in query_args:
        param = arg.split('=')
        if len(param) == 2:
            key = param[0]
            val = param[1]
            params[key] = val

    if N_PARAM not in params:
        await send_422(send)
        return

    try:
        n = int(params[N_PARAM])
    except ValueError:
        await send_422(send)
        return

    if n < 0:
        await send_400(send)
        return

    factorial = 1
    for i in range(n):
        factorial *= i

    await send_ok(send, factorial)


async def get_fibonacci(path: str, send):
    try:
        params = path.split('/')
        n = int(params[-1])
    except (ValueError, IndexError):
        await send_422(send)
        return

    if n < 0:
        await send_400(send)
        return

    a = 0
    b = 1
    for _ in range(n):
        tmp = a + b
        a = b
        b = tmp

    await send_ok(send, a)


async def get_mean(receive, send):
    rq = await receive()
    body = rq['body']
    if len(body) == 0:
        await send_422(send)
        return

    floats = []
    args = json.loads(body)
    try:
        for arg in args:
            floats.append(float(arg))
    except ValueError:
        await send_422(send)
        return

    if len(floats) == 0:
        await send_400(send)
        return

    mean: float = 0.0
    for f in floats:
        mean += f
    mean /= len(floats)

    await send_ok(send, mean)


async def send_400(send):
    await send_error(send, 400, 'Bad Request')


async def send_404(send):
    await send_error(send, 404, 'Not Found')


async def send_422(send):
    await send_error(send, 422, 'Unprocessable Entity')


async def send_error(send, status: int, message: str):
    error_body = {
        'error': f'{status} {message}'
    }
    await send_body(send, status, error_body)


async def send_ok(send, result: Number):
    ok_body = {
        'result': result
    }
    await send_body(send, 200, ok_body)


async def send_body(send, status: int, body):
    await send({
        'type': 'http.response.start',
        'status': status,
        'headers': [(b'content-type', b'application/json')],
    })
    await send({
        'type': 'http.response.body',
        'body': json.dumps(body).encode(ENCODING),
    })


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
