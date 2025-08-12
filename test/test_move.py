from share import LOGGER
from share.result import Err
from tools.service import get_cfg, move_file, pop_task

if __name__ == "__main__":
    result = pop_task()

    if isinstance(result, Err):
        raise result.error

    task = result.value
    cfg = get_cfg(task).value
    assert cfg is not None

    LOGGER.info(f"{task} {cfg}")

    move_file(task, cfg)
