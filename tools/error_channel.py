import stim
import numpy as np


def b_m_p_insert(cirkit, b_m_p):
    new_cirkit = stim.Circuit()

    for i in range(len(cirkit)):
        if cirkit[i].name == "M" or cirkit[i].name == "MR":
            qubits = [t.value for t in cirkit[i].targets_copy() if t.is_qubit_target]
            if qubits:
                for q in qubits:
                    if b_m_p > np.random.random():
                        new_cirkit.append("X_ERROR", [q], 1)

        new_cirkit.append(cirkit[i])

    return new_cirkit


def a_r_p_insert(cirkit, a_r_p):
    new_cirkit = stim.Circuit()

    for part in cirkit:
        new_cirkit.append(part)

        if part.name in ("R", "MR"):
            qubits = [t.value for t in part.targets_copy() if t.is_qubit_target]
            for q in qubits:
                if np.random.random() < a_r_p:
                    new_cirkit.append("X_ERROR", [q], 1)

    return new_cirkit


def error_channel(distance, rounds, before_measure_flip_probability, after_reset_flip_probability):
    d, r = distance, rounds 
    b_m_p = before_measure_flip_probability
    a_r_p = after_reset_flip_probability
    cirkit = stim.Circuit.generated("repetition_code:memory",distance = d, rounds = r)
    new1 = b_m_p_insert(cirkit, b_m_p)
    new2 = a_r_p_insert(new1, a_r_p)

    return new2