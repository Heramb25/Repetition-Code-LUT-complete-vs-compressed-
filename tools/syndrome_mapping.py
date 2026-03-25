class SyndromeMapper:
    """
    Maps error vectors to syndromes and stores, for each syndrome,
    the minimum-weight correction.

    Expected error vector order:
        [A1M1, A2M1, ..., A(d-1)M1,
         A1M2, A2M2, ..., A(d-1)M2,
         ...,
         A1Mr, A2Mr, ..., A(d-1)Mr,
         D1M, D2M, ..., DdM]
    """

    def __init__(self, distance: int, rounds: int):
        self.distance = distance
        self.rounds = rounds
        self.anc_len = (distance - 1) * rounds
        self.total_len = self.anc_len + distance
        self.syndrome_len = (distance - 1) * (rounds + 1)

    def error_vector_to_syndrome_tuple(self, error_vector):
        e = tuple(int(x) for x in error_vector)
        d = self.distance
        r = self.rounds

        if len(e) != self.total_len:
            raise ValueError(
                f"Error vector length {len(e)} does not match expected length {self.total_len}"
            )

        syndrome = [0] * self.syndrome_len

        # First round detector block
        syndrome[: d - 1] = e[: d - 1]

        # Round-to-round detector blocks
        for j in range(r - 1):
            start = (d - 1) * (j + 1)
            end = start + (d - 1)

            prev_block = syndrome[start - (d - 1): start]
            meas_block = e[start:end]

            syndrome[start:end] = [a ^ b for a, b in zip(prev_block, meas_block)]

        # Final parity-check block
        data_meas = e[self.anc_len:]
        last_anc_block = e[self.anc_len - (d - 1): self.anc_len]

        syndrome[self.anc_len:] = [
            data_meas[i] ^ data_meas[i + 1] ^ last_anc_block[i]
            for i in range(d - 1)
        ]

        return tuple(syndrome)

    def syndrome_tuple_to_int(self, syndrome):
        """
        Convert a syndrome tuple/list of bits into an integer.
        The first bit becomes the most significant bit.
        """
        s_int = 0
        for bit in syndrome:
            s_int = (s_int << 1) | int(bit)
        return s_int

    def error_vector_to_syndrome_int(self, error_vector):
        syndrome = self.error_vector_to_syndrome_tuple(error_vector)
        return self.syndrome_tuple_to_int(syndrome)

    def correction_from_error_vector(self, error_vector):
        return tuple(error_vector[-self.distance:])

    def syndrome_to_min_corrections(self, error_vectors):
        """
        Build dictionary:
            syndrome_int -> one minimum-weight correction tuple

        Tie-breaking rule:
        keep the first encountered minimum-weight correction.
        """
        best = {}

        for e in error_vectors:
            syndrome_int = self.error_vector_to_syndrome_int(e)
            correction = self.correction_from_error_vector(e)
            wt = sum(correction)

            if syndrome_int not in best or wt < best[syndrome_int]["weight"]:
                best[syndrome_int] = {
                    "weight": wt,
                    "correction": correction,
                }

        return {k: v["correction"] for k, v in best.items()}