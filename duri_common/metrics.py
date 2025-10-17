try:
    from prometheus_client import Counter, Gauge
except Exception:
    # 런타임 미탑재 환경에서도 안전
    class _N:
        def labels(self, *_, **__):
            return self

        def inc(self, *_):
            pass

        def set(self, *_):
            pass

    def Counter(*_, **__):
        return _N()

    def Gauge(*_, **__):
        return _N()


def prom_counter(name, desc, labels=()):
    return Counter(name, desc, labels)


def prom_gauge(name, desc, labels=()):
    return Gauge(name, desc, labels)

