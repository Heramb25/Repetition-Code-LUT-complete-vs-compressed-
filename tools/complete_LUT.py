from itertools import product
from collections import defaultdict


class CompleteLUT:
    """
    Generate and store all measurement patterns, corresponding syndromes,
    and lookup tables for a repetition code with given distance and rounds.

    Optimized version:
    - syndrome keys are stored as integers instead of tuples
    - avoids storing a large numpy syndrome matrix
    - stores only the integer syndrome per measurement
    """

    def __init__(self, distance, rounds):
        self.distance = distance
        self.rounds = rounds
        self.num_measure = (distance - 1) * rounds + distance
        self.syndrome_len = (distance - 1) * (rounds + 1)

        self.measurements = None
        self.syndromes = None   # now stores syndrome integers, not bit arrays

    @staticmethod
    def bits_to_int(bits):
        """
        Convert iterable of bits to integer.
        Example: [1,0,1,1] -> 11
        """
        s_int = 0
        for bit in bits:
            s_int = (s_int << 1) | int(bit)
        return s_int

    def _m_to_s(self):
        """
        Internal helper that computes all possible measurement patterns and
        their corresponding syndromes, then stores them in the class.

        Syndromes are stored as integers instead of tuples/arrays.
        """
        d, r = self.distance, self.rounds

        measurements = list(product([0, 1], repeat=self.num_measure))
        syndrome_ints = []

        for m in measurements:
            s = [0] * self.syndrome_len

            # first block
            s[:d - 1] = m[:d - 1]

            # middle round-to-round syndrome updates
            for j in range(r - 1):
                start = (d - 1) * (j + 1)
                end = start + d - 1
                prev_block = s[start - (d - 1): start]
                meas_block = m[start:end]
                s[start:end] = [a ^ b for a, b in zip(prev_block, meas_block)]

            # final data-measurement-related syndrome block
            list1 = m[self.num_measure - d:self.num_measure - 1]
            list2 = m[self.num_measure - d + 1:self.num_measure]
            list3 = m[self.num_measure - (2 * d - 1):self.num_measure - d]

            c = [a ^ b ^ c_ for a, b, c_ in zip(list1, list2, list3)]
            s[self.num_measure - d:] = c

            syndrome_ints.append(self.bits_to_int(s))

        self.measurements = measurements
        self.syndromes = syndrome_ints

    def _ensure_computed(self):
        """
        Compute measurements and syndromes only once.
        """
        if self.measurements is None or self.syndromes is None:
            self._m_to_s()

    def measurement_lut(self):
        """
        Return a dictionary with integer syndrome as key and all possible full
        measurement combinations producing that syndrome as values.
        """
        self._ensure_computed()
        lut_dict = defaultdict(list)

        for m, s_int in zip(self.measurements, self.syndromes):
            lut_dict[s_int].append(m)

        return lut_dict

    def data_lut(self):
        """
        Return a dictionary with integer syndrome as key and all possible data-qubit
        correction patterns for that syndrome as values.
        """
        self._ensure_computed()
        lut_dict = defaultdict(list)

        for m, s_int in zip(self.measurements, self.syndromes):
            lut_dict[s_int].append(tuple(m[-self.distance:]))

        return lut_dict

    def data_correction_lut(self):
        """
        Return a dictionary with integer syndrome as key and the minimum-weight
        data-qubit correction for that syndrome as value.
        """
        self._ensure_computed()
        lut_dict = {}

        for m, s_int in zip(self.measurements, self.syndromes):
            candidate = tuple(m[-self.distance:])

            if s_int in lut_dict:
                if sum(candidate) < sum(lut_dict[s_int]):
                    lut_dict[s_int] = candidate
            else:
                lut_dict[s_int] = candidate

        return lut_dict