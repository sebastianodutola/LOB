import timeit
from collections import deque 

def cache_locality_benchmark(nq):
    setup = f"""
from collections import deque
ne = 1_000_000
qs = [] 
for _ in range({nq}):
    qs.append(deque())
"""

    stmt = f"""
for j in range(ne):
    qs[j % {nq}].append(j)
"""
    return setup, stmt

def run_benchmark():
    nqs = [10, 100, 1000, 10_000, 100_000, 500_000]
    res = []
    print("Benchmarking Cache Locality")
    print("="*70)
    for nq in nqs:
        print(f"benchmarking with number of queues: {nq} ...")
        setup, stmt = cache_locality_benchmark(nq) 
        time = timeit.timeit(setup=setup, stmt=stmt, number=10)
        res.append({
            "number of queues" : nq,
            "total time" : time,
            "avg time / addition" : time / 1_000_000_000
            })

    print("="*70)
    print("Cache Locality Benchmarks")
    print("="*70)
    print(f"{'number of queues':<20}|{'total time':<25}|{'avg time / addition':<20}")
    print("-"*70)
    for res in res:
        print(f"{res['number of queues']:<20}|{res['total time']:<25}|{res['avg time / addition']:<20}")

if __name__ == "__main__":
    run_benchmark()