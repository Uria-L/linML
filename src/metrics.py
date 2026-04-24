from collections import deque

class RollingMean:
    def __init__(self, window_seconds):
        self.window = window_seconds
        self.q = deque()
        self.sum = 0.0

    def add(self, value, now):
        self.q.append((now, value))
        self.sum += value

        while self.q and now - self.q[0][0] > self.window:
            _, old = self.q.popleft()
            self.sum -= old

    def mean(self):
        return self.sum / len(self.q) if self.q else 0.0

class RateMetric:
    """For cumulative totals → rate (CPU, IO bytes, Net bytes)"""
    def __init__(self, window_seconds=60):
        self.rolling_mean = RollingMean(window_seconds)
        self.last_total = None
        self.last_ts = None

    def update(self, total, loop_ts):
        ''' update the rate metric '''
        if self.last_ts is None:
            self.last_ts = loop_ts
            self.last_total = total
            return
        dt = loop_ts - self.last_ts
        if dt > 0:

            delta = max(0, total - self.last_total) # if total < last_total, a process likely exited. we treat this as a 0 bytes change
            rate = delta / dt
            self.rolling_mean.add(rate, loop_ts)
        self.last_ts = loop_ts
        self.last_total = total

    def mean(self):
        return self.rolling_mean.mean()


class SampleMetric:
    """For point-in-time values (memory, child count)"""
    def __init__(self, window_seconds=60):
        self.rolling_mean = RollingMean(window_seconds)

    def update(self, value, loop_ts):
        self.rolling_mean.add(value, loop_ts)

    def mean(self):
        return self.rolling_mean.mean()


class CountMetric:
    """For event counts that reset per window"""
    def __init__(self):
        self.count = 0

    def increment(self):
        self.count += 1

    def emit_and_reset(self):
        val = self.count
        self.count = 0
        return val


class StaticValue:
    """For categorical/single values"""
    def __init__(self):
        self.value = None

    def set(self, value):
        self.value = value

    def get(self):
        return self.value
