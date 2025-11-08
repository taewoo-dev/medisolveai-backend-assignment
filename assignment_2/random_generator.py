import math
import random

def get_1_or_0() -> int:
    """0 또는 1을 동일한 확률로 반환합니다."""
    value = random.randint(0, 1)
    if value not in (0, 1):
        raise RuntimeError("random.randint(0, 1) returned an invalid value")
    return value


def get_random(n: int) -> int:
    """[0, n] 범위의 정수를 반환합니다.
    실수 입력은 내림(floor)하여 정수로 변환하며, 무한대나 NaN은 허용하지 않습니다.
    """
    if not isinstance(n, int):
        if isinstance(n, float):
            if math.isnan(n) or math.isinf(n):
                raise ValueError("n must be a finite number")
            n = math.floor(n)
        else:
            raise TypeError("n must be an integer or float")

    if n < 0:
        raise ValueError("n must be non-negative")

    if n == 0:
        return 0

    bit_length = n.bit_length()

    while True:
        candidate = 0
        for _ in range(bit_length):
            bit = get_1_or_0()

            candidate = (candidate << 1) | bit

        if candidate <= n:
            if not isinstance(candidate, int):
                raise RuntimeError("Internal error: candidate is not an integer")
            return candidate
