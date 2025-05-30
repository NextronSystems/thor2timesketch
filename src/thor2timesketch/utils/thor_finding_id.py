import uuid
import base64
from thor2timesketch.constants import PREFIX


class ThorFindingId:
    @staticmethod
    def get_finding_id() -> str:
        raw_data = uuid.uuid4().bytes
        base32 = base64.b32encode(raw_data).decode("ascii")
        id_part = base32.rstrip("=").lower()
        return f"{PREFIX}-{id_part}"
