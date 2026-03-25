from itertools import combinations


class ErrorVectors:
    def __init__(self, distance: int, rounds: int):
        self.distance = distance
        self.rounds = rounds
        self.length = rounds * (distance - 1) + distance

    def before(self, weight: int):
        if weight < 0 or weight > self.length:
            return

        for pos in combinations(range(self.length), weight):
            vec = [0] * self.length
            for i in pos:
                vec[i] = 1
            yield vec

    def after(self, weight: int):
        if weight < 0 or weight > self.length:
            return
    
        d = self.distance
        r = self.rounds
        length = self.length
    
        for pos in combinations(range(length), weight):
            error_vec = [0] * length
            for i in pos:
                error_vec[i] = 1
    
            solved_vec = [0] * length
    
            # error_vec order:
            # [D1, D2, ..., Dd,
            #  A1M1, A2M1, ..., A(d-1)M1,
            #  A1M2, A2M2, ..., A(d-1)M2,
            #  ...
            #  A1Mr, A2Mr, ..., A(d-1)Mr]
    
            # solved_vec order:
            # [A1M1, A2M1, ..., A(d-1)M1,
            #  A1M2, A2M2, ..., A(d-1)M2,
            #  ...
            #  A1Mr, A2Mr, ..., A(d-1)Mr,
            #  D1M, D2M, ..., DdM]
    
            # Ancilla measurement part (round-major)
            for j in range(r):
                for i in range(d - 1):
                    measured_idx = j * (d - 1) + i
                    raw_after_idx = d + j * (d - 1) + i
    
                    solved_vec[measured_idx] = (
                        error_vec[i]
                        ^ error_vec[i + 1]
                        ^ error_vec[raw_after_idx]
                    )
    
            # Final data measurement part
            solved_vec[length - d:] = error_vec[:d]
    
            yield solved_vec

    def combined_error_vectors(self, max_weight: int, before_prob: float, after_prob: float):
        length = self.length
        final_vectors = []
        seen = set()

        if max_weight < 0:
            return final_vectors

        if before_prob == 0 and after_prob == 0:
            return [[0] * length]

        if before_prob > 0 and after_prob == 0:
            for w in range(max_weight + 1):
                for b in self.before(w):
                    tb = tuple(b)
                    if tb not in seen:
                        seen.add(tb)
                        final_vectors.append(b)
            return final_vectors

        if before_prob == 0 and after_prob > 0:
            for w in range(max_weight + 1):
                after_vecs = list(self.after(w))
                for a in after_vecs:
                    ta = tuple(a)
                    if ta not in seen:
                        seen.add(ta)
                        final_vectors.append(a)
            return final_vectors

        # both active: restore original order
        after_cache = {}
        for w in range(max_weight + 1):
            after_cache[w] = list(self.after(w))

        for k in range(max_weight + 1):
            l_max = max_weight - k

            for b in self.before(k):
                for l in range(l_max + 1):
                    for a in after_cache[l]:
                        x = [bi ^ ai for bi, ai in zip(b, a)]
                        tx = tuple(x)

                        if tx not in seen:
                            seen.add(tx)
                            final_vectors.append(x)

        return final_vectors