# Import libraries from qiskit
import matplotlib.pyplot as plt
import numpy as np
import math

from qiskit import *
from qiskit.providers.ibmq import least_busy

from qiskit.tools.visualization import plot_histogram


# Initializing circuit: define as 2 qubits
q = QuantumRegister(2, "q")
c = ClassicalRegister(2, "c")

# Create the quantum circuit
qc = QuantumCircuit(q, c)

## Step 1: Apply a Hadarmard gate to all qubits
qc.h(q)

## Step 2: Implement the Oracle circuit for state |11> + Grover diffusion
qc.cz(q[1], q[0])
qc.barrier(q)

qc.h(q)
qc.x(q)
qc.cz(q[1], q[0])
qc.x(q)
qc.h(q)
qc.barrier(q)

## Don't forget about the measurement gates!
qc.measure(q[0], c[0])
qc.measure(q[1], c[1])

## Step 4: Run on backend simulator and print results
simulator = Aer.get_backend("qasm_simulator")
result = execute(qc, backend=simulator, shots=2048).result()
counts = result.get_counts()

print("RESULT: ", counts, "\n")

plot_histogram(counts)
