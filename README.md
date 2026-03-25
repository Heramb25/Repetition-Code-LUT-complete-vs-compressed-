# Repetition Code LUT: Complete vs Compressed

This repository studies **lookup-table (LUT) decoders for the repetition code** under a phenomenological noise setting, and compares two styles of decoder construction:

- **Complete LUT**: builds the decoder by enumerating **all possible measurement patterns** for a given distance `d` and rounds `r`.
- **Compressed / Limited LUT**: builds the decoder only from **error vectors up to a chosen maximum weight `w`**, making the table much smaller and faster to construct.

The goal is to compare these decoders in terms of:

- logical error rate,
- LUT build time,
- LUT size / number of entries,
- and the effect of compression through `max_weight`.

---

## Repository structure

```text
.
├── Main.ipynb
└── tools/
    ├── complete_LUT.py
    ├── error_channel.py
    ├── error_vec.py
    └── syndrome_mapping.py
```

### `Main.ipynb`
Main notebook that drives the full workflow:
- builds repetition-code circuits for logical `0` and `1` (logical `1` is prepared by applying `X` to all data qubits after reset),
- samples measurements and detector outputs using **Stim**,
- constructs complete and limited LUTs,
- compares decoder performance,
- reports build time, LUT size, and logical error rates,
- and plots the final results.

### `tools/complete_LUT.py`
Defines the **`CompleteLUT`** class.

For fixed `(distance, rounds)`, it enumerates all possible measurement patterns and computes the corresponding syndrome for each one. From this, it can build:
- `measurement_lut()` → syndrome → all compatible measurement patterns
- `data_lut()` → syndrome → all compatible data-bit corrections
- `data_correction_lut()` → syndrome → **one selected correction**

The selected correction is the **minimum-weight correction on data qubits** among all candidates for that syndrome. Syndrome keys are stored as integers to keep the table representation lighter.

### `tools/error_vec.py`
Defines the **`ErrorVectors`** class.

This is the backbone of the **compressed / limited LUT** construction. It generates all possible error vectors up to a chosen `max_weight = w`.

It supports:
- errors before measurement,
- errors after reset,
- and the combined case where both channels are active.

The generated vectors are then used to build only a restricted LUT instead of the full one.

### `tools/syndrome_mapping.py`
Defines the **`SyndromeMapper`** class.

It maps each generated error vector to its syndrome and stores a decoder entry of the form:

```text
syndrome_int -> correction
```

When multiple error vectors lead to the same syndrome, the current implementation keeps **one representative correction**, chosen by **minimum weight on the data-qubit part** of the error vector.

This is simple and useful for compression, but it is **not an optimal decoding rule** in general.

### `tools/error_channel.py`
Contains helper functions for inserting measurement/reset related `X_ERROR`s into a Stim repetition-code circuit.

This file is auxiliary and can be used for custom circuit-level noise experiments, though the main notebook currently uses Stim’s built-in noise parameters directly when generating the circuit.

---

## How the two decoders work

### 1. Complete LUT
The complete LUT assumes that for a given `(d, r)`, we can enumerate **every possible measurement pattern**. Each measurement pattern is converted into a syndrome, and for each syndrome we store one correction.

Because several patterns may map to the same syndrome, the decoder does **not** keep all equivalent corrections in the final decoding table. Instead, it selects the one with the **smallest number of flipped data qubits**.

So in this repository, the complete LUT is **complete in coverage**, but still uses a **naive correction-selection rule**.

### 2. Compressed / Limited LUT
The compressed LUT does not enumerate all measurement patterns. Instead:

1. `error_vec.py` generates all possible error vectors only up to some maximum weight `w`.
2. `syndrome_mapping.py` converts each error vector into a syndrome.
3. If multiple error vectors give the same syndrome, one correction is selected using the same **minimum data-qubit weight** rule.

This means the limited LUT is much smaller, but only covers the subset of syndromes produced by the chosen restricted error set.

---

## Validation idea

The notebook includes `validate_complete_vs_mapper(...)` as a consistency check.

Its purpose is to verify that the syndrome encoding used by `SyndromeMapper` is consistent with the syndrome encoding used in `CompleteLUT`. In practice, this supports checking that when a syndrome appears in both constructions, the corresponding mapping is compatible.

A stronger future validation would be to **directly compare the final correction entries** for every common syndrome between:
- the limited LUT, and
- the complete LUT.

---

## Decoding assumption used in this repo

A key assumption in both decoder constructions is:

> For a given syndrome, choose the correction with **minimum weight on data qubits**.

This makes the implementation simple, but it has an important limitation:

- the chosen correction is only a **representative guess**,
- it is not guaranteed to be the most likely physical error,
- and it ignores richer tie-breaking or probability-based decoding logic.

So the current LUTs should be viewed as:
- a clean framework for comparison,
- a way to study LUT compression,
- and a starting point for FPGA-friendly implementations,

rather than the final form of an optimal decoder.

---

## Current assumptions and limitations

- Noise handling is simplified to the error model used in the notebook / helper scripts.
- The compressed LUT depends strongly on the chosen `max_weight`.
- Missing syndromes in the limited LUT are not learned; they are simply absent from the table, and the notebook currently falls back to zero correction when a syndrome is not found.
- Correction selection is based only on **data-qubit weight**, not on full likelihood.
- The present validation is mainly a **syndrome-consistency check**; it can be extended to compare full correction tables directly.

---

## Possible improvements

Some natural next steps for this project are:

- replace the minimum-data-weight rule with a better tie-breaking / likelihood-based rule,
- directly validate limited LUT entries against the complete LUT for all common syndromes,
- analyze how logical error changes with `max_weight`,
- export the final LUTs in a format better suited for FPGA / hardware implementation,
- and refine the compressed-LUT generation so that it better reflects the actual error statistics.

---

## Requirements

Main dependencies used here:
- `stim`
- `numpy`
- `pandas`
- `matplotlib`

---

## Summary

This repository compares **complete** and **compressed** LUT decoders for repetition codes.

- The **complete LUT** covers all measurement patterns.
- The **compressed LUT** keeps only patterns generated from bounded-weight error vectors.
- Both currently choose corrections using a **minimum data-qubit weight** rule.

The project is useful for understanding the tradeoff between **decoder quality**, **table size**, and **hardware practicality**, while also making clear where the current decoder logic can be improved.
