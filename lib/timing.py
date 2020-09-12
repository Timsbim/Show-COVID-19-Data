###
#
# Content:
#
# (I) A rudimentary decorator for the execution time testing of functions. It
# offers two basic modes:
#
# (1) "Embedded" for testing within the normal habitat of the function. In
#     this mode the decorated function returns its original output and the
#     execution time is only reported on the console. This is the default mode,
#     in which all other parameters will be ignored.
#
# (2) Not "embedded": This mode is for direct, explicit testing. The decorated
#     function doesn't return the normal output! Instead, the function returns
#     a testing log dictionary which contains the results of the test. In
#     analogy to timeit the decorator allows for the specification of the
#     number of function calls executed during the test as well as the number
#     of trials conducted during the test (each trial executes the specified
#     number of calls). If the "verbose" flag is true the results are also
#     reported on the console.
#
# (II) A context manager for measuring the execution time of a block of code
#
###
from functools import wraps
from time import time
from contextlib import contextmanager


def embedded_timing(func) -> callable:

    @wraps(func)
    def measuring(*args, **kwargs):
        # Measuring
        start_time = time()
        results = func(*args, **kwargs)
        end_time = time()

        # Console output
        print(f"-> Execution time of {func.__name__} (ms):",
              f"{(end_time - start_time) * 1000:.2f}")

        # Returning the normal output of func
        return results

    return measuring


def direct_timing(calls=1, trials=1, verbose=False) -> callable:

    def repeating(func):
        # Inner "real" decorating

        @wraps(func)
        def measuring(*args, **kwargs):
            # Setting up the testing log dictionary
            log = {
                'name': f"{func.__name__}",
                'trials': trials,
                'calls': calls,
                'time': [],
                'average': None
            }

            # Running the trials
            for trial in range(trials):
                total_time = 0
                for call in range(calls):
                    # Measuring
                    start_time = time()
                    func(*args, **kwargs)
                    end_time = time()
                    total_time += end_time - start_time
                log['time'].append(total_time * 1000 / calls)
            log['average'] = sum(log['time']) / trials

            # Console output if required
            if verbose:
                print(f"Timing function \"{log['name']}\":")
                for trial in range(trials):
                    print(f"-> {trial + 1}. trial: "
                          f"Average execution time (ms) = "
                          f"{log['time'][trial]:.2f}")
                print(f"Average execution time over all trials (ms) = "
                      f"{log['average']:.2f}")

            # Returning the testing log dictionary
            return log

        return measuring

    return repeating


def timing(embedded=True, calls=1, trials=1, verbose=False) -> callable:
    # Outer wrapping for parameter handover

    def repeating(func):
        # Inner "real" decorating

        @wraps(func)
        def measuring(*args, **kwargs):
            # Part for embedded, background testing
            if embedded:
                # Measuring
                start_time = time()
                results = func(*args, **kwargs)
                end_time = time()

                # Console output
                print(f"-> Execution time of {func.__name__} (ms):",
                      f"{(end_time - start_time) * 1000:.2f}")

                # Returning the normal output of func
                return results

            # Part for direct, explicit testing
            # Setting up the testing log dictionary
            log = {
                'name': f"{func.__name__}",
                'trials': trials,
                'calls': calls,
                'time': [],
                'average': None
            }

            # Running the trials
            for trial in range(trials):
                total_time = 0
                for call in range(calls):
                    # Measuring
                    start_time = time()
                    func(*args, **kwargs)
                    end_time = time()
                    total_time += end_time - start_time
                log['time'].append(total_time * 1000 / calls)
            log['average'] = sum(log['time']) / trials

            # Console output if required
            if verbose:
                print(f"Timing function \"{log['name']}\":")
                for trial in range(trials):
                    print(f"-> {trial + 1}. trial: "
                          f"Average execution time (ms) = "
                          f"{log['time'][trial]:.2f}")
                print(f"Average execution time over all trials (ms) = "
                      f"{log['average']:.2f}")

            # Returning the testing log dictionary
            return log

        return measuring

    return repeating


@contextmanager
def block_timer(tag=None):
    try:
        start_time = time()
        yield start_time
    finally:
        duration = (time() - start_time) * 1000
        if tag is not None:
            print(f"-> Execution time of block of code with tag <{tag}>: "
                  f"{duration:.2f} ms")
        else:
            print(f"-> Exectution time of block of code: {duration:.2f} ms")
