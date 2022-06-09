import csv
import math

import qiskit.providers.aer.noise as noise
from qiskit import IBMQ, Aer, transpile, assemble
from qiskit import execute
from qiskit.circuit import QuantumCircuit
from qiskit.circuit.library import MCMTVChain
from qiskit.visualization import plot_histogram


# Apply H-gates to put qubits in superstate
def initialize_s(qc, qubits):
    for q in qubits:
        qc.h(q)
    return qc


# Construct a diffuser for circuit of n qubits
def diffuser(nqubits):
    qc = QuantumCircuit(nqubits)
    for qubit in range(nqubits):
        qc.h(qubit)
    for qubit in range(nqubits):
        qc.x(qubit)
    qc.h(nqubits - 1)
    qc.mct(list(range(nqubits - 1)), nqubits - 1)
    qc.h(nqubits - 1)
    for qubit in range(nqubits):
        qc.x(qubit)
    for qubit in range(nqubits):
        qc.h(qubit)
    U_s = qc.to_gate()
    U_s.name = "Diffuser"
    return U_s


def execute_circ(n, noise_model=None, basis_gates=None, coupling_map=None):
    qs = list(range(n))
    grover_circuit = QuantumCircuit(n)
    grover_circuit = initialize_s(grover_circuit, qs)
    grover_circuit.append(diffuser(n), qs)
    grover_circuit.measure_all()
    grover_circuit.draw()

    n_seq = round(math.sqrt(math.pow(2, n)))
    result = execute(grover_circuit, Aer.get_backend('qasm_simulator'),
                     noise_model=noise_model,
                     coupling_map=coupling_map,
                     basis_gates=basis_gates, shots=100000).result()
    counts = result.get_counts()
    return counts


def custom_noise(prob, gates, error_function):
    custom_noise = noise.NoiseModel()
    e = error_function(prob, 1)
    custom_noise.add_all_qubit_quantum_error(e, gates)
    custom_basis = custom_noise.basis_gates
    return custom_noise, custom_basis


# Build noise model from backend properties
provider = IBMQ.load_account()
backend = provider.get_backend('ibmq_lima')

real_noise = noise.NoiseModel.from_backend(backend)
real_basis = real_noise.basis_gates
coupling_map = backend.configuration().coupling_map

# build custom noise models
std_err = 3e-3
depolar_h, depolar_basis_h = custom_noise(std_err, 'h', noise.depolarizing_error)
depolar_x, depolar_basis_x = custom_noise(std_err, 'x', noise.depolarizing_error)
ampdamp_h, ampdamp_basis_h = custom_noise(std_err, 'h', noise.amplitude_damping_error)
ampdamp_x, ampdamp_basis_x = custom_noise(std_err, 'x', noise.amplitude_damping_error)
phasedamp_h, phasedamp_basis_h = custom_noise(std_err, 'h', noise.phase_damping_error)
phasedamp_x, phasedamp_basis_x = custom_noise(std_err, 'x', noise.phase_damping_error)

bitcount = [2, 3, 5]
for x in bitcount:
    baseline = execute_circ(x)
    real = execute_circ(x, real_noise, real_basis, coupling_map)
    depolarizing = execute_circ(x, depolar_h, depolar_basis_h)
    amplitude = execute_circ(x, ampdamp_h, ampdamp_basis_h)
    phase = execute_circ(x, phasedamp_h, phasedamp_basis_h)

    with open('test_' + str(x) + '.csv', 'w') as f:
        f.write("Qubit, Baseline, Real, Depolarizing, Amplitude, Phase\n")
        for key in clean.keys():
            f.write("%s, %s, %s, %s, %s, %s\n" % (
                key, baseline[key], real[key], depolarizing[key], amplitude[key], phase[key]))

    legend = ['Without noise', 'With noise', 'Depolarizing', 'Amplification dampening', 'Phase dampening']
    plot_histogram([baseline, real, depolarizing, amplitude, phase],
                   title=str(x) + " qubits",
                   legend=legend,
                   filename=f"{x}qubits.jpg",
                   figsize=(35, 17))

    print(f"{x} qubits, baseline: {baseline}")
    print(f"{x} qubits, real: {real}")
    print(f"{x} qubits, depolarizing: {depolarizing}")
    print(f"{x} qubits, amplification dampening: {amplitude}")
    print(f"{x} qubits, phase dampening: {phase}")