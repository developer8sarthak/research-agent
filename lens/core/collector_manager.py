import concurrent.futures
import traceback
from typing import Dict, List, Callable

def run_collectors(collectors: Dict[str, Callable], query: str, timeout: int = 300):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_name = {
            executor.submit(func, query): name 
            for name, func in collectors.items()
        }
        
        # Track which collectors finished
        finished_collectors = set()
        
        try:
            for future in concurrent.futures.as_completed(future_to_name, timeout=timeout):
                name = future_to_name[future]
                finished_collectors.add(name)
                try:
                    data = future.result()
                    yield {
                        "collector": name,
                        "status": "success",
                        "data": data
                    }
                except Exception as e:
                    yield {
                        "collector": name,
                        "status": "failed",
                        "error": str(e),
                        "traceback": traceback.format_exc()
                    }
        except concurrent.futures.TimeoutError:
            # Handle collectors that didn't finish in time
            for future, name in future_to_name.items():
                if name not in finished_collectors:
                    yield {
                        "collector": name,
                        "status": "failed",
                        "error": "Collector timed out after 5 minutes",
                        "traceback": ""
                    }
