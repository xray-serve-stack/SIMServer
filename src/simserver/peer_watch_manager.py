class PeerWatchManager:
    def __init__(self) -> None:
        self._following: dict[bytes, set[bytes]] = {}
        self._followers: dict[bytes, set[bytes]] = {}

    def set_following(
        self,
        follower: bytes,
        targets: set[bytes],
    ) -> None:
        current = self._following.get(
            follower,
            set(),
        )

        for target in current - targets:
            followers = self._followers.get(target)

            if followers is not None:
                followers.discard(follower)

                if not followers:
                    self._followers.pop(
                        target,
                        None,
                    )

        for target in targets - current:
            self._followers.setdefault(
                target,
                set(),
            ).add(follower)

        if targets:
            self._following[follower] = set(targets)
        else:
            self._following.pop(
                follower,
                None,
            )

    def disconnect(
        self,
        peer: bytes,
    ) -> set[bytes]:
        # These are the peers that must receive
        # the PEER_OFFLINE event.
        followers = set(
            self._followers.get(
                peer,
                set(),
            )
        )

        # Remove the peer itself from the following graph.
        following = self._following.pop(
            peer,
            set(),
        )

        # The peer is offline, so it must no longer appear
        # as an active follower of the peers it was following.
        for target in following:
            target_followers = self._followers.get(target)

            if target_followers is None:
                continue

            target_followers.discard(peer)

            if not target_followers:
                self._followers.pop(
                    target,
                    None,
                )

        return followers

    def get_following(
        self,
        peer: bytes,
    ) -> set[bytes]:
        return set(
            self._following.get(
                peer,
                set(),
            )
        )

    def get_followers(
        self,
        peer: bytes,
    ) -> set[bytes]:
        return set(
            self._followers.get(
                peer,
                set(),
            )
        )
