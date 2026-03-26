"""
Vast.ai PyWorker для ComfyUI WanVideo Serverless.

PyWorker проксирует запросы на API Server (порт 18288),
который выполняет workflow, загружает результаты и возвращает base64/S3 URLs.
"""

from vastai import Worker, WorkerConfig, HandlerConfig, LogActionConfig, BenchmarkConfig

# Monkey-patch aiohttp Application для увеличения лимита тела запроса
# По умолчанию 1MB, нужно ~200MB для base64 видео
import aiohttp.web
_orig_app_init = aiohttp.web.Application.__init__
def _patched_app_init(self, *args, **kwargs):
    kwargs.setdefault("client_max_size", 200 * 1024 * 1024)  # 200MB
    _orig_app_init(self, *args, **kwargs)
aiohttp.web.Application.__init__ = _patched_app_init

MODEL_SERVER_URL = "http://127.0.0.1"
MODEL_SERVER_PORT = 18288
MODEL_LOG_FILE = "/var/log/portal/comfyui.log"
MODEL_HEALTHCHECK_ENDPOINT = "/health"

MODEL_LOAD_LOG_MSG = [
    "To see the GUI go to: ",
]

MODEL_ERROR_LOG_MSGS = [
    "MetadataIncompleteBuffer",
    "Value not in list: ",
    "[ERROR] Provisioning Script failed",
]

MODEL_INFO_LOG_MSGS = [
    "Downloading model",
]

worker_config = WorkerConfig(
    model_server_url=MODEL_SERVER_URL,
    model_server_port=MODEL_SERVER_PORT,
    model_log_file=MODEL_LOG_FILE,
    model_healthcheck_url=MODEL_HEALTHCHECK_ENDPOINT,
    handlers=[
        HandlerConfig(
            route="/generate/sync",
            allow_parallel_requests=False,
            max_queue_time=300.0,
            workload_calculator=lambda payload: 10000.0,
            benchmark_config=BenchmarkConfig(
                generator=lambda: {"workflow_json": {}},
                runs=1,
                concurrency=1,
            ),
        )
    ],
    log_action_config=LogActionConfig(
        on_load=MODEL_LOAD_LOG_MSG,
        on_error=MODEL_ERROR_LOG_MSGS,
        on_info=MODEL_INFO_LOG_MSGS,
    ),
)

if __name__ == "__main__":
    print("vast-pyworker: Starting PyWorker for ComfyUI WanVideo...")
    Worker(worker_config).run()
