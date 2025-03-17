from typing import Any, Optional, Tuple, Union

# Types for encryption modes

class EcbMode:
    def __init__(self, key: bytes, *args: Any, **kwargs: Any) -> None: ...
    def encrypt(self, plaintext: bytes) -> bytes: ...
    def decrypt(self, ciphertext: bytes) -> bytes: ...

class GcmMode:
    def __init__(self, key: bytes, *args: Any, **kwargs: Any) -> None: ...
    def update(self, data: bytes) -> None: ...
    def encrypt_and_digest(self, plaintext: bytes) -> Tuple[bytes, bytes]: ...
    def decrypt(
        self,
        ciphertext: bytes,
        mac_tag: Optional[bytes] = None,
        associated_data: Optional[bytes] = None,
    ) -> bytes: ...

# Module functions

def new(
    key: bytes,
    mode: int = 2,
    iv: Optional[bytes] = None,
    nonce: Optional[bytes] = None,
    mac_len: Optional[int] = None,
    segment_size: Optional[int] = None,
    **kwargs: Any,
) -> Union[EcbMode, GcmMode]: ...

# Constants
MODE_ECB: int
MODE_CBC: int
MODE_CFB: int
MODE_OFB: int
MODE_CTR: int
MODE_GCM: int
block_size: int
key_size: Tuple[int, ...]
