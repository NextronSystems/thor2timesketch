from typing import Any, Dict
from collections import deque
from thor2timesketch.config.console_config import ConsoleConfig
from thor2timesketch.constants import DELIMITER
from thor2timesketch.exceptions import FlattenJsonError


class JSONFlattener:

    @staticmethod
    def _is_list_of_dicts(value: Any) -> bool:
        return isinstance(value, list) and bool(value) and isinstance(value[0], dict)

    @staticmethod
    def flatten_json(json_line: Dict[str, Any]) -> Dict[str, Any]:
        flattened: Dict[str, Any] = {}
        queue = deque([(json_line, "")])
        try:
            while queue:
                current, path = queue.popleft()
                if isinstance(current, dict):
                    for key, value in current.items():
                        new_key = f"{path}{DELIMITER}{key}" if path else key
                        queue.append((value, new_key))
                elif JSONFlattener._is_list_of_dicts(current):
                    for index, item in enumerate(current, start=1):
                        key = f"{path}{DELIMITER}{index}"
                        flattened[key] = item
                else:
                    flattened[path] = current
        except Exception as e:
            raise FlattenJsonError(f"Error flattening JSON: {e}")
        ConsoleConfig.debug(f"Successfully flattened JSON: '{flattened}'")
        return flattened
