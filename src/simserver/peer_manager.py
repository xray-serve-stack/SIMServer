from .peer import Peer


class PeerManager:
    def __init__(self) -> None:
        self._peers: dict[bytes, Peer] = {}

    def add(self, peer: Peer) -> bool:
        if peer.public_key in self._peers:
            return False

        self._peers[peer.public_key] = peer
        return True

    def remove(self, public_key: bytes) -> bool:
        if public_key not in self._peers:
            return False

        del self._peers[public_key]
        return True

    def get(self, public_key: bytes) -> Peer | None:
        return self._peers.get(public_key)

    def is_online(self, public_key: bytes) -> bool:
        return public_key in self._peers

    def list(self) -> list[Peer]:
        return list(self._peers.values())
