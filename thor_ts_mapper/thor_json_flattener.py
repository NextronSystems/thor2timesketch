from typing import Any, Dict
from collections import deque
from thor_ts_mapper.logger_config import LoggerConfig

logger = LoggerConfig.get_logger(__name__)

class JSONFlattener:
    DELIMITER = '_'

    @staticmethod
    def _index_to_letter(idx: int) -> str:
        result = ""
        idx += 1
        while idx > 0:
            idx, remainder = divmod(idx - 1, 26)
            result = chr(65 + remainder) + result
        return result

    @staticmethod
    def flatten_jsonl(json_line: Dict[str, Any]) -> Dict[str, Any]:
        if json_line is None:
            logger.warning("Received an empty THOR log as input for flattening.")
            return {}
        #bfs algorithm
        flattened: Dict[str, Any] = {}
        queue = deque([(json_line, "")])
        try:
            while queue:
                current, key_path = queue.popleft()

                if isinstance(current, dict):
                    for key, value in current.items():
                        new_key = f"{key_path}{JSONFlattener.DELIMITER}{key}" if key_path else key
                        queue.append((value, new_key))
                elif isinstance(current, list):
                    for idx, item in enumerate(current):
                        alpha_index = JSONFlattener._index_to_letter(idx)
                        new_key = f"{key_path}{JSONFlattener.DELIMITER}{alpha_index}"
                        queue.append((item, new_key))
                else:
                    flattened[key_path] = current
        except Exception as e:
            logger.error(f"Unexpected error during flattening: {str(e)}")
            return {}

        logger.debug("Successfully flattened JSON: %s", flattened)
        return flattened