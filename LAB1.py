import random
import time
import multiprocessing

def write_data_to_file(filename, data):
    with open(filename, 'w') as f:
        f.write(' '.join(map(str, data)))

def read_data_from_file(filename):
    with open(filename, 'r') as f:
        return list(map(int, f.read().split()))

def quickselect(arr, k):
    if not arr:
        return None
    pivot = random.choice(arr)
    left = [x for x in arr if x < pivot]
    eq = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]

    if k < len(left):
        return quickselect(left, k)
    elif k < len(left) + len(eq):
        return pivot
    else:
        return quickselect(right, k - len(left) - len(eq))

def partition_chunk(args):
    chunk, pivot = args
    left, eq, right = [], [], []
    for x in chunk:
        if x < pivot:
            left.append(x)
        elif x == pivot:
            eq.append(x)
        else:
            right.append(x)
    return left, eq, right

def parallel_partition(arr, pivot, pool, num_workers):
    """Паралельне розбиття масиву на left, eq, right за одним pivot."""
    chunk_size = max(1, len(arr) // num_workers)
    chunks = [arr[i:i + chunk_size] for i in range(0, len(arr), chunk_size)]
    results = pool.map(partition_chunk, [(chunk, pivot) for chunk in chunks])

    left_all, eq_all, right_all = [], [], []
    for left, eq, right in results:
        left_all.extend(left)
        eq_all.extend(eq)
        right_all.extend(right)
    return left_all, eq_all, right_all

def parallel_quickselect(arr, k, pool, num_workers, depth=0, max_depth=2, threshold=50000):
    """
    Паралельний quickselect з обмеженням глибини max_depth
    та порогом threshold для послідовного алгоритму.
    """
    if len(arr) <= threshold or depth >= max_depth:
        return quickselect(arr, k)
    if not arr:
        return None

    pivot = random.choice(arr)
    left_all, eq_all, right_all = parallel_partition(arr, pivot, pool, num_workers)

    if k < len(left_all):
        return parallel_quickselect(left_all, k, pool, num_workers, depth + 1, max_depth, threshold)
    elif k < len(left_all) + len(eq_all):
        return pivot
    else:
        return parallel_quickselect(right_all, k - len(left_all) - len(eq_all),
                                    pool, num_workers, depth + 1, max_depth, threshold)

def benchmark(func, *args):
    start = time.perf_counter()
    result = func(*args)
    end = time.perf_counter()
    return result, end - start

if __name__ == "__main__":
    # ------------------------------------------------------
    # 1) Приклад із малим обсягом вхідних даних (п.4)
    # ------------------------------------------------------
    small_data = [3, 1, 4, 2, 5]
    k_small = 2
    filename_small = "small_data.txt"

    # Запис і читання для демонстрації
    write_data_to_file(filename_small, small_data)
    data_small_from_file = read_data_from_file(filename_small)

    print("=== Приклад із невеликим обсягом даних ===")
    print(f"Вхідні дані (з файлу): {data_small_from_file}")
    print(f"k = {k_small}")

    # Послідовний алгоритм (невеликі дані)
    seq_result_small = quickselect(data_small_from_file, k_small)
    print(f"Послідовний алгоритм (small): k-й елемент = {seq_result_small}")

    # Паралельний алгоритм (невеликі дані)
    num_workers_small = min(multiprocessing.cpu_count(), len(data_small_from_file))
    with multiprocessing.Pool(num_workers_small) as pool:
        par_result_small = parallel_quickselect(data_small_from_file, k_small, pool, num_workers_small)
    print(f"Паралельний алгоритм (small): k-й елемент = {par_result_small}")

    # Перевірка вручну: відсортуємо data_small_from_file
    sorted_small = sorted(data_small_from_file)
    print(f"Відсортований масив: {sorted_small}")
    print(f"Перевірка вручну: {sorted_small[k_small]} (k-й елемент)\n")

    # ------------------------------------------------------
    # 2) Приклад, який виконується ~5 секунд (п.5)
    #
    # ------------------------------------------------------
    size_5sec = 2 * 10**7 #
    k_5sec = size_5sec // 2
    filename_5sec = "data_5sec.txt"

    # Генеруємо дані
    data_5sec = [random.randint(1, 10**6) for _ in range(size_5sec)]
    write_data_to_file(filename_5sec, data_5sec)
    data_5sec_from_file = read_data_from_file(filename_5sec)

    print("=== Приклад ~5 секунд ===")
    print(f"Розмір масиву: {len(data_5sec_from_file)}")
    print(f"k = {k_5sec}")

    # Послідовний алгоритм
    print("Тестування послідовного алгоритму (5-секундний приклад)...")
    result_seq_5sec, time_seq_5sec = benchmark(quickselect, data_5sec_from_file, k_5sec)
    print(f"Послідовний алгоритм: k-й елемент = {result_seq_5sec}, час = {time_seq_5sec:.4f} сек")

    # Паралельний алгоритм
    print("Тестування паралельного алгоритму (5-секундний приклад)...")
    num_workers_5sec = min(multiprocessing.cpu_count(), len(data_5sec_from_file))
    with multiprocessing.Pool(num_workers_5sec) as pool:
        result_par_5sec, time_par_5sec = benchmark(
            parallel_quickselect,
            data_5sec_from_file,
            k_5sec,
            pool,
            num_workers_5sec,
            0,      # depth
            2,      # max_depth
            50000,  # threshold
        )
    print(f"Паралельний алгоритм: k-й елемент = {result_par_5sec}, час = {time_par_5sec:.4f} сек")
