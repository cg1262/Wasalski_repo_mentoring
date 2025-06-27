# Python - trackowanie wykorzystania zasobów i wykorzystanie wszystkich rdzeni

## Monitoring wykorzystania zasobów

### 1. **Podstawowe informacje o systemie**

#### psutil - kompleksowy monitoring:
```python
import psutil
import os

def get_system_info():
    """Pobierz podstawowe informacje o systemie"""
    # CPU
    cpu_count = psutil.cpu_count(logical=False)  # Fizyczne rdzenie
    cpu_count_logical = psutil.cpu_count(logical=True)  # Logiczne rdzenie
    cpu_freq = psutil.cpu_freq()
    cpu_percent = psutil.cpu_percent(interval=1, percpu=True)
    
    # Memory
    memory = psutil.virtual_memory()
    swap = psutil.swap_memory()
    
    # Disk
    disk = psutil.disk_usage('/')
    
    print(f"=== SYSTEM INFO ===")
    print(f"Physical CPU cores: {cpu_count}")
    print(f"Logical CPU cores: {cpu_count_logical}")
    print(f"CPU frequency: {cpu_freq.current:.2f} MHz")
    print(f"CPU usage per core: {cpu_percent}")
    print(f"Total RAM: {memory.total / (1024**3):.2f} GB")
    print(f"Available RAM: {memory.available / (1024**3):.2f} GB")
    print(f"RAM usage: {memory.percent}%")
    print(f"Disk usage: {disk.percent}%")
    
    return {
        'cpu_cores_physical': cpu_count,
        'cpu_cores_logical': cpu_count_logical,
        'cpu_usage': cpu_percent,
        'memory_total': memory.total,
        'memory_available': memory.available,
        'memory_percent': memory.percent
    }

# Wywołanie
system_info = get_system_info()
```

#### Monitoring konkretnego procesu:
```python
import psutil
import os
import time
import threading
from datetime import datetime

class ProcessMonitor:
    def __init__(self, pid=None):
        self.pid = pid or os.getpid()
        self.process = psutil.Process(self.pid)
        self.monitoring = False
        self.stats = []
    
    def start_monitoring(self, interval=1):
        """Rozpocznij ciągły monitoring"""
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, args=(interval,))
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Zatrzymaj monitoring"""
        self.monitoring = False
        if hasattr(self, 'monitor_thread'):
            self.monitor_thread.join()
    
    def _monitor_loop(self, interval):
        """Pętla monitorująca"""
        while self.monitoring:
            try:
                # Pobierz statystyki
                stats = self.get_current_stats()
                self.stats.append(stats)
                
                # Wyświetl na bieżąco
                print(f"[{stats['timestamp']}] "
                      f"CPU: {stats['cpu_percent']:5.1f}% | "
                      f"Memory: {stats['memory_mb']:6.1f} MB | "
                      f"Threads: {stats['num_threads']:3d}")
                
                time.sleep(interval)
            except psutil.NoSuchProcess:
                print("Process no longer exists")
                break
    
    def get_current_stats(self):
        """Pobierz aktualne statystyki procesu"""
        with self.process.oneshot():  # Optymalizacja - jeden syscall
            memory_info = self.process.memory_info()
            cpu_percent = self.process.cpu_percent()
            num_threads = self.process.num_threads()
            
            return {
                'timestamp': datetime.now().strftime('%H:%M:%S'),
                'pid': self.pid,
                'cpu_percent': cpu_percent,
                'memory_mb': memory_info.rss / (1024 * 1024),  # Resident Set Size
                'memory_vms_mb': memory_info.vms / (1024 * 1024),  # Virtual Memory Size
                'num_threads': num_threads,
                'status': self.process.status()
            }
    
    def get_summary(self):
        """Podsumowanie statystyk"""
        if not self.stats:
            return "Brak danych do analizy"
        
        cpu_values = [s['cpu_percent'] for s in self.stats]
        memory_values = [s['memory_mb'] for s in self.stats]
        
        return {
            'duration_seconds': len(self.stats),
            'cpu_avg': sum(cpu_values) / len(cpu_values),
            'cpu_max': max(cpu_values),
            'memory_avg_mb': sum(memory_values) / len(memory_values),
            'memory_max_mb': max(memory_values),
            'max_threads': max(s['num_threads'] for s in self.stats)
        }

# Przykład użycia
def cpu_intensive_task():
    """Zadanie obciążające CPU"""
    result = 0
    for i in range(10_000_000):
        result += i ** 2
    return result

# Rozpocznij monitoring
monitor = ProcessMonitor()
monitor.start_monitoring(interval=0.5)

# Wykonaj zadanie
print("Starting CPU-intensive task...")
result = cpu_intensive_task()
print(f"Task completed, result: {result}")

# Zatrzymaj monitoring
time.sleep(2)
monitor.stop_monitoring()

# Pokaż podsumowanie
summary = monitor.get_summary()
print("\n=== SUMMARY ===")
for key, value in summary.items():
    print(f"{key}: {value}")
```

### 2. **Resource tracking decorator**

#### Decorator do automatycznego trackingu:
```python
import functools
import time
import psutil
import os
from typing import Callable, Any

def track_resources(log_interval: float = 1.0):
    """
    Decorator do trackowania zasobów podczas wykonywania funkcji
    
    Args:
        log_interval: Interwał logowania w sekundach
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            process = psutil.Process(os.getpid())
            
            # Statystyki początkowe
            start_time = time.time()
            start_memory = process.memory_info().rss
            
            # Monitoring w osobnym wątku
            monitor = ProcessMonitor()
            monitor.start_monitoring(interval=log_interval)
            
            try:
                # Wykonaj funkcję
                result = func(*args, **kwargs)
                
                # Statystyki końcowe
                end_time = time.time()
                end_memory = process.memory_info().rss
                duration = end_time - start_time
                memory_diff = (end_memory - start_memory) / (1024 * 1024)  # MB
                
                # Zatrzymaj monitoring
                monitor.stop_monitoring()
                summary = monitor.get_summary()
                
                # Wyświetl raport
                print(f"\n=== RESOURCE USAGE REPORT for {func.__name__} ===")
                print(f"Duration: {duration:.2f} seconds")
                print(f"Memory change: {memory_diff:+.2f} MB")
                print(f"Peak CPU usage: {summary['cpu_max']:.1f}%")
                print(f"Peak memory usage: {summary['memory_max_mb']:.1f} MB")
                print(f"Max threads: {summary['max_threads']}")
                print("=" * 50)
                
                return result
                
            except Exception as e:
                monitor.stop_monitoring()
                raise e
                
        return wrapper
    return decorator

# Przykład użycia
@track_resources(log_interval=0.5)
def matrix_multiplication(size: int):
    """Mnożenie macierzy - CPU intensive"""
    import numpy as np
    
    print(f"Creating {size}x{size} matrices...")
    A = np.random.rand(size, size)
    B = np.random.rand(size, size)
    
    print("Performing matrix multiplication...")
    C = np.dot(A, B)
    
    return C.shape

@track_resources(log_interval=1.0)
def memory_intensive_task():
    """Zadanie zajmujące dużo pamięci"""
    print("Creating large lists...")
    
    # Utwórz duże listy
    big_lists = []
    for i in range(10):
        big_list = [j ** 2 for j in range(1_000_000)]
        big_lists.append(big_list)
        time.sleep(0.5)  # Symuluj pracę
    
    print("Processing data...")
    total = sum(sum(lst) for lst in big_lists)
    
    return total

# Test
if __name__ == "__main__":
    # Test CPU-intensive
    result1 = matrix_multiplication(1000)
    print(f"Matrix result shape: {result1}")
    
    # Test memory-intensive
    result2 = memory_intensive_task()
    print(f"Memory task result: {result2}")
```

## Wykorzystanie wszystkich rdzeni CPU

### 1. **multiprocessing - równoległość na poziomie procesów**

#### Process Pool dla CPU-intensive tasks:
```python
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor, as_completed
import time
import math

def cpu_intensive_function(n):
    """Funkcja intensywnie wykorzystująca CPU"""
    result = 0
    for i in range(n):
        result += math.sqrt(i) * math.sin(i) * math.cos(i)
    return result

def parallel_processing_basic():
    """Podstawowe przetwarzanie równoległe"""
    
    # Dane do przetworzenia
    tasks = [1_000_000] * 8  # 8 zadań po 1M operacji każde
    
    print(f"CPU cores available: {mp.cpu_count()}")
    
    # Sekwencyjne przetwarzanie
    start_time = time.time()
    sequential_results = [cpu_intensive_function(task) for task in tasks]
    sequential_time = time.time() - start_time
    
    # Równoległe przetwarzanie
    start_time = time.time()
    with ProcessPoolExecutor(max_workers=mp.cpu_count()) as executor:
        parallel_results = list(executor.map(cpu_intensive_function, tasks))
    parallel_time = time.time() - start_time
    
    # Wyniki
    print(f"Sequential time: {sequential_time:.2f} seconds")
    print(f"Parallel time: {parallel_time:.2f} seconds")
    print(f"Speedup: {sequential_time / parallel_time:.2f}x")
    print(f"Results match: {sequential_results == parallel_results}")
    
    return sequential_time, parallel_time

def parallel_with_progress():
    """Równoległe przetwarzanie z progress tracking"""
    
    tasks = [500_000 + i * 100_000 for i in range(16)]  # Różne rozmiary zadań
    
    print(f"Processing {len(tasks)} tasks...")
    
    start_time = time.time()
    with ProcessPoolExecutor(max_workers=mp.cpu_count()) as executor:
        # Submit all tasks
        future_to_task = {
            executor.submit(cpu_intensive_function, task): i 
            for i, task in enumerate(tasks)
        }
        
        results = [None] * len(tasks)
        completed = 0
        
        # Process results as they complete
        for future in as_completed(future_to_task):
            task_index = future_to_task[future]
            try:
                result = future.result()
                results[task_index] = result
                completed += 1
                
                elapsed = time.time() - start_time
                print(f"Task {task_index:2d} completed ({completed:2d}/{len(tasks)}) "
                      f"in {elapsed:.1f}s")
                      
            except Exception as exc:
                print(f'Task {task_index} generated an exception: {exc}')
    
    total_time = time.time() - start_time
    print(f"All tasks completed in {total_time:.2f} seconds")
    
    return results

# Uruchom testy
if __name__ == "__main__":
    print("=== Basic Parallel Processing ===")
    parallel_processing_basic()
    
    print("\n=== Parallel Processing with Progress ===")
    parallel_with_progress()
```

#### Zaawansowane zarządzanie procesami:
```python
import multiprocessing as mp
import queue
import time
import signal
import sys

class WorkerProcess(mp.Process):
    """Niestandardowy proces worker"""
    
    def __init__(self, task_queue, result_queue, worker_id):
        super().__init__()
        self.task_queue = task_queue
        self.result_queue = result_queue
        self.worker_id = worker_id
        self.running = True
        
    def run(self):
        """Główna pętla procesu worker"""
        print(f"Worker {self.worker_id} started (PID: {os.getpid()})")
        
        while self.running:
            try:
                # Pobierz zadanie z kolejki (timeout 1 sekunda)
                task = self.task_queue.get(timeout=1)
                
                if task is None:  # Poison pill - sygnał do zakończenia
                    break
                
                # Wykonaj zadanie
                task_id, data = task
                result = self.process_task(task_id, data)
                
                # Wyślij wynik
                self.result_queue.put((task_id, result, self.worker_id))
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Worker {self.worker_id} error: {e}")
                self.result_queue.put((None, f"Error: {e}", self.worker_id))
        
        print(f"Worker {self.worker_id} finished")
    
    def process_task(self, task_id, data):
        """Przetwórz pojedyncze zadanie"""
        # Symuluj pracę
        time.sleep(0.1)
        result = sum(x ** 2 for x in data)
        return result

class MultiProcessingManager:
    """Menedżer procesów roboczych"""
    
    def __init__(self, num_workers=None):
        self.num_workers = num_workers or mp.cpu_count()
        self.task_queue = mp.Queue()
        self.result_queue = mp.Queue()
        self.workers = []
        self.running = False
    
    def start_workers(self):
        """Uruchom procesy robocze"""
        print(f"Starting {self.num_workers} worker processes...")
        
        for i in range(self.num_workers):
            worker = WorkerProcess(
                self.task_queue, 
                self.result_queue, 
                worker_id=i
            )
            worker.start()
            self.workers.append(worker)
        
        self.running = True
    
    def submit_tasks(self, tasks):
        """Dodaj zadania do kolejki"""
        for task_id, data in enumerate(tasks):
            self.task_queue.put((task_id, data))
    
    def get_results(self, expected_count):
        """Pobierz wyniki z kolejki"""
        results = {}
        received = 0
        
        while received < expected_count:
            try:
                task_id, result, worker_id = self.result_queue.get(timeout=5)
                results[task_id] = result
                received += 1
                print(f"Received result {received}/{expected_count} "
                      f"from worker {worker_id}")
                      
            except queue.Empty:
                print("Timeout waiting for results")
                break
        
        return results
    
    def shutdown(self):
        """Zatrzymaj wszystkie procesy"""
        print("Shutting down workers...")
        
        # Wyślij poison pills
        for _ in self.workers:
            self.task_queue.put(None)
        
        # Czekaj na zakończenie
        for worker in self.workers:
            worker.join(timeout=5)
            if worker.is_alive():
                print(f"Force terminating worker {worker.worker_id}")
                worker.terminate()
        
        self.running = False
        print("All workers stopped")

# Przykład użycia
def demonstrate_multiprocessing_manager():
    """Demonstracja niestandardowego managera procesów"""
    
    # Przygotuj dane
    import random
    tasks = [
        [random.randint(1, 100) for _ in range(random.randint(10, 100))]
        for _ in range(20)
    ]
    
    # Utwórz manager
    manager = MultiProcessingManager(num_workers=4)
    
    try:
        # Uruchom workers
        manager.start_workers()
        
        # Wyślij zadania
        print(f"Submitting {len(tasks)} tasks...")
        manager.submit_tasks(tasks)
        
        # Pobierz wyniki
        results = manager.get_results(len(tasks))
        
        print(f"\nProcessed {len(results)} tasks:")
        for task_id, result in sorted(results.items()):
            print(f"Task {task_id:2d}: {result}")
    
    finally:
        # Zawsze zatrzymaj workers
        manager.shutdown()

if __name__ == "__main__":
    demonstrate_multiprocessing_manager()
```

### 2. **concurrent.futures - wysokopoziomowe API**

#### ThreadPoolExecutor vs ProcessPoolExecutor:
```python
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
import requests
import time
import math

def io_bound_task(url):
    """I/O bound task - pobieranie URL"""
    try:
        response = requests.get(url, timeout=5)
        return len(response.content)
    except:
        return 0

def cpu_bound_task(n):
    """CPU bound task - obliczenia matematyczne"""
    return sum(math.sqrt(i) for i in range(n))

def compare_executors():
    """Porównanie ThreadPoolExecutor vs ProcessPoolExecutor"""
    
    # I/O bound tasks
    urls = [
        'https://httpbin.org/delay/1',
        'https://httpbin.org/delay/1',
        'https://httpbin.org/delay/1',
        'https://httpbin.org/delay/1'
    ]
    
    print("=== I/O Bound Tasks ===")
    
    # Sequential
    start = time.time()
    seq_results = [io_bound_task(url) for url in urls]
    seq_time = time.time() - start
    print(f"Sequential I/O: {seq_time:.2f}s")
    
    # ThreadPoolExecutor
    start = time.time()
    with ThreadPoolExecutor(max_workers=4) as executor:
        thread_results = list(executor.map(io_bound_task, urls))
    thread_time = time.time() - start
    print(f"ThreadPoolExecutor: {thread_time:.2f}s (speedup: {seq_time/thread_time:.1f}x)")
    
    # ProcessPoolExecutor (nie zalecane dla I/O)
    start = time.time()
    with ProcessPoolExecutor(max_workers=4) as executor:
        process_results = list(executor.map(io_bound_task, urls))
    process_time = time.time() - start
    print(f"ProcessPoolExecutor: {process_time:.2f}s (speedup: {seq_time/process_time:.1f}x)")
    
    # CPU bound tasks
    cpu_tasks = [500_000] * 4
    
    print("\n=== CPU Bound Tasks ===")
    
    # Sequential
    start = time.time()
    seq_results = [cpu_bound_task(task) for task in cpu_tasks]
    seq_time = time.time() - start
    print(f"Sequential CPU: {seq_time:.2f}s")
    
    # ThreadPoolExecutor (ograniczone przez GIL)
    start = time.time()
    with ThreadPoolExecutor(max_workers=4) as executor:
        thread_results = list(executor.map(cpu_bound_task, cpu_tasks))
    thread_time = time.time() - start
    print(f"ThreadPoolExecutor: {thread_time:.2f}s (speedup: {seq_time/thread_time:.1f}x)")
    
    # ProcessPoolExecutor (zalecane dla CPU)
    start = time.time()
    with ProcessPoolExecutor(max_workers=4) as executor:
        process_results = list(executor.map(cpu_bound_task, cpu_tasks))
    process_time = time.time() - start
    print(f"ProcessPoolExecutor: {process_time:.2f}s (speedup: {seq_time/process_time:.1f}x)")

if __name__ == "__main__":
    compare_executors()
```

### 3. **Asynchroniczne przetwarzanie z asyncio**

#### Async dla I/O bound tasks:
```python
import asyncio
import aiohttp
import time

async def fetch_url_async(session, url):
    """Asynchroniczne pobieranie URL"""
    try:
        async with session.get(url) as response:
            content = await response.read()
            return len(content)
    except:
        return 0

async def async_io_processing():
    """Asynchroniczne przetwarzanie I/O"""
    
    urls = [
        'https://httpbin.org/delay/1',
        'https://httpbin.org/delay/1', 
        'https://httpbin.org/delay/1',
        'https://httpbin.org/delay/1'
    ] * 3  # 12 zadań total
    
    print(f"Processing {len(urls)} URLs asynchronously...")
    
    start_time = time.time()
    
    async with aiohttp.ClientSession() as session:
        # Utwórz wszystkie tasks
        tasks = [fetch_url_async(session, url) for url in urls]
        
        # Wykonaj wszystkie równocześnie
        results = await asyncio.gather(*tasks)
    
    total_time = time.time() - start_time
    
    print(f"Async processing completed in {total_time:.2f}s")
    print(f"Average per request: {total_time/len(urls):.2f}s")
    print(f"Results: {results}")
    
    return results

# CPU + I/O mieszane
async def mixed_workload():
    """Mieszane obciążenie CPU + I/O"""
    
    async def cpu_task_async(n):
        """CPU task w async wrapper"""
        # Dla CPU-intensive użyj loop.run_in_executor
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, cpu_bound_task, n)
        return result
    
    async def mixed_task(task_id):
        """Mieszane zadanie I/O + CPU"""
        # I/O część
        async with aiohttp.ClientSession() as session:
            io_result = await fetch_url_async(session, 'https://httpbin.org/delay/0.5')
        
        # CPU część
        cpu_result = await cpu_task_async(100_000)
        
        return {
            'task_id': task_id,
            'io_result': io_result,
            'cpu_result': cpu_result
        }
    
    print("Processing mixed workload...")
    start_time = time.time()
    
    # Uruchom 6 mieszanych zadań
    tasks = [mixed_task(i) for i in range(6)]
    results = await asyncio.gather(*tasks)
    
    total_time = time.time() - start_time
    print(f"Mixed workload completed in {total_time:.2f}s")
    
    for result in results:
        print(f"Task {result['task_id']}: "
              f"I/O={result['io_result']}, CPU={result['cpu_result']}")

# Uruchomienie async funkcji
if __name__ == "__main__":
    # Asynchroniczne I/O
    print("=== Async I/O Processing ===")
    asyncio.run(async_io_processing())
    
    print("\n=== Mixed Async Workload ===")
    asyncio.run(mixed_workload())
```

## Praktyczne przykłady zastosowań

### 1. **Data processing pipeline**

```python
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor
import pandas as pd
import numpy as np
import time

def process_data_chunk(chunk_data):
    """Przetwórz fragment danych"""
    chunk_id, data = chunk_data
    
    # Symuluj przetwarzanie danych
    df = pd.DataFrame(data)
    
    # Przykładowe operacje
    df['processed'] = df['value'] * 2
    df['category'] = df['value'].apply(lambda x: 'high' if x > 50 else 'low')
    
    # Agregacje
    summary = {
        'chunk_id': chunk_id,
        'count': len(df),
        'mean': df['value'].mean(),
        'std': df['value'].std(),
        'processed_sum': df['processed'].sum()
    }
    
    return summary

def parallel_data_pipeline():
    """Pipeline przetwarzania danych z wykorzystaniem wszystkich rdzeni"""
    
    # Wygeneruj przykładowe dane
    np.random.seed(42)
    total_size = 1_000_000
    data = {
        'id': range(total_size),
        'value': np.random.normal(50, 20, total_size),
        'category': np.random.choice(['A', 'B', 'C'], total_size)
    }
    
    # Podziel dane na chunki
    chunk_size = total_size // mp.cpu_count()
    chunks = []
    
    for i in range(0, total_size, chunk_size):
        end_idx = min(i + chunk_size, total_size)
        chunk = {
            'id': data['id'][i:end_idx],
            'value': data['value'][i:end_idx],
            'category': data['category'][i:end_idx]
        }
        chunks.append((len(chunks), chunk))
    
    print(f"Processing {total_size} records in {len(chunks)} chunks using {mp.cpu_count()} cores")
    
    # Przetwarzanie równoległe
    start_time = time.time()
    
    with ProcessPoolExecutor(max_workers=mp.cpu_count()) as executor:
        results = list(executor.map(process_data_chunk, chunks))
    
    processing_time = time.time() - start_time
    
    # Agreguj wyniki
    total_count = sum(r['count'] for r in results)
    overall_mean = sum(r['mean'] * r['count'] for r in results) / total_count
    
    print(f"Processing completed in {processing_time:.2f} seconds")
    print(f"Processed {total_count} records")
    print(f"Overall mean: {overall_mean:.2f}")
    print(f"Throughput: {total_count / processing_time:.0f} records/second")
    
    return results

if __name__ == "__main__":
    parallel_data_pipeline()
```

## Best practices i porady

### 1. **Kiedy używać której metody**:

```python
def choose_parallelization_method(task_type, data_size, io_ratio):
    """
    Pomoc w wyborze metody równoległości
    
    Args:
        task_type: 'cpu_bound' lub 'io_bound'
        data_size: rozmiar danych ('small', 'medium', 'large')
        io_ratio: stosunek I/O do CPU (0.0 - 1.0)
    """
    
    recommendations = {
        ('cpu_bound', 'large', 'low'): 'ProcessPoolExecutor - maksymalne wykorzystanie CPU',
        ('cpu_bound', 'medium', 'low'): 'ProcessPoolExecutor - dobra równowaga',
        ('cpu_bound', 'small', 'low'): 'Sequential - overhead większy niż zysk',
        
        ('io_bound', 'large', 'high'): 'asyncio - najwyższa wydajność I/O',
        ('io_bound', 'medium', 'high'): 'ThreadPoolExecutor - prostsza implementacja',
        ('io_bound', 'small', 'high'): 'ThreadPoolExecutor lub asyncio',
        
        ('mixed', 'large', 'medium'): 'asyncio + run_in_executor',
        ('mixed', 'medium', 'medium'): 'ThreadPoolExecutor',
        ('mixed', 'small', 'medium'): 'Sequential z optymalizacjami'
    }
    
    # Klasyfikacja io_ratio
    if io_ratio > 0.7:
        io_level = 'high'
    elif io_ratio > 0.3:
        io_level = 'medium'
    else:
        io_level = 'low'
    
    if task_type == 'cpu_bound' and io_ratio > 0.3:
        task_type = 'mixed'
    
    key = (task_type, data_size, io_level)
    return recommendations.get(key, 'Analiza indywidualna wymagana')

# Przykłady
print("CPU-intensive, duże dane:", 
      choose_parallelization_method('cpu_bound', 'large', 0.1))
print("I/O-intensive, średnie dane:", 
      choose_parallelization_method('io_bound', 'medium', 0.8))
print("Mieszane obciążenie:", 
      choose_parallelization_method('cpu_bound', 'large', 0.5))
```

### 2. **Monitoring w czasie rzeczywistym**:

```python
import threading
import time

class RealTimeMonitor:
    """Monitor zasobów w czasie rzeczywistym"""
    
    def __init__(self):
        self.monitoring = False
        self.stats = []
        
    def start_realtime_monitoring(self):
        """Rozpocznij monitoring w osobnym wątku"""
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
    def stop_monitoring(self):
        self.monitoring = False
        
    def _monitor_loop(self):
        import psutil
        
        while self.monitoring:
            # CPU per core
            cpu_percent = psutil.cpu_percent(percpu=True)
            
            # Memory
            memory = psutil.virtual_memory()
            
            # Active processes
            process_count = len(psutil.pids())
            
            # Current process
            current_process = psutil.Process()
            current_cpu = current_process.cpu_percent()
            current_memory = current_process.memory_info().rss / 1024 / 1024
            
            print(f"\r[{time.strftime('%H:%M:%S')}] "
                  f"CPU: {cpu_percent} | "
                  f"RAM: {memory.percent:4.1f}% | "
                  f"Proc: {process_count:4d} | "
                  f"Self: {current_cpu:5.1f}% CPU, {current_memory:6.1f}MB", 
                  end='', flush=True)
            
            time.sleep(1)

# Przykład użycia w kontekście
def with_monitoring(func):
    """Context manager z monitoringiem"""
    monitor = RealTimeMonitor()
    
    try:
        monitor.start_realtime_monitoring()
        result = func()
        return result
    finally:
        monitor.stop_monitoring()
        print()  # Nowa linia po monitoring

# Test
if __name__ == "__main__":
    def test_function():
        time.sleep(5)
        return "Done"
    
    result = with_monitoring(test_function)
    print(f"Result: {result}")
```

**Kluczowe zasady:**
- ✅ CPU-bound tasks → ProcessPoolExecutor
- ✅ I/O-bound tasks → ThreadPoolExecutor lub asyncio  
- ✅ Monitoruj zasoby podczas rozwoju
- ✅ Testuj wydajność na docelowym sprzęcie
- ✅ Uwzględnij overhead równoległości dla małych zadań