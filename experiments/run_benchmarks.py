from experiments.book_benchmark import benchmark, cache_locality_benchmark, validate_lob


def run_all():
    print("Running benchmark...")
    benchmark.run_benchmarks()
    print("Running cache locality benchmark...")
    cache_locality_benchmark.run_benchmark()
    print("Running order book validation script")
    validate_lob.run_validation()


if __name__ == "__main__":
    run_all()
