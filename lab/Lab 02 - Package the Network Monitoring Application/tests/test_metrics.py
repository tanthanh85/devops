from app.metrics_service import normalize


def test_normalize_nested_values():
    cpu = {"cpu-usage": {"cpu-utilization": {"five-seconds": 17}}}
    memory = {"memory-statistic": [{"used-memory": 30, "total-memory": 100}]}
    assert normalize(cpu, memory) == {"cpu_percent": 17.0, "memory_percent": 30.0}
