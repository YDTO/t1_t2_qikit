import numpy as np
import matplotlib.pyplot as plt

from qiskit import *
from qiskit.providers.aer.noise.errors.standard_errors import thermal_relaxation_error
from qiskit.providers.aer.noise import NoiseModel

from qiskit.ignis.characterization.coherence import T1Fitter, T2StarFitter, T2Fitter
from qiskit.ignis.characterization.coherence import t1_circuits, t2_circuits, t2star_circuits

IBMQ.load_account()

num_of_gates = (np.linspace(10, 300, 50)).astype(int)
gate_time = 0.1

# Note that it is possible to measure several qubits in parallel
qubits = [0, 2]

t1_circs, t1_xdata = t1_circuits(num_of_gates, gate_time, qubits)
t2star_circs, t2star_xdata, osc_freq = t2star_circuits(num_of_gates, gate_time, qubits, nosc=5)
t2echo_circs, t2echo_xdata = t2_circuits(np.floor(num_of_gates/2).astype(int),
                                         gate_time, qubits)
t2cpmg_circs, t2cpmg_xdata = t2_circuits(np.floor(num_of_gates/6).astype(int),
                                         gate_time, qubits,
                                         n_echos=5, phase_alt_echo=True)

# backend = qiskit.Aer.get_backend('qasm_simulator')
provider = IBMQ.get_provider(hub='ibm-q')
device = provider.get_backend('ibmq_santiago')
shots = 400

# Let the simulator simulate the following times for qubits 0 and 2:
t_q0 = 25.0
t_q2 = 15.0

# # Define T1 and T2 noise:
# t1_noise_model = NoiseModel()
# t1_noise_model.add_quantum_error(
#     thermal_relaxation_error(t_q0, 2*t_q0, gate_time),
#     'id', [0])
# t1_noise_model.add_quantum_error(
#     thermal_relaxation_error(t_q2, 2*t_q2, gate_time),
#     'id', [2])
#
# t2_noise_model = NoiseModel()
# t2_noise_model.add_quantum_error(
#     thermal_relaxation_error(np.inf, t_q0, gate_time, 0.5),
#     'id', [0])
# t2_noise_model.add_quantum_error(
#     thermal_relaxation_error(np.inf, t_q2, gate_time, 0.5),
#     'id', [2])

# Run the simulator
t1_backend_result = execute(t1_circs, device, shots=shots).result()
t2star_backend_result = execute(t2star_circs, device, shots=shots).result()
t2echo_backend_result = execute(t2echo_circs, device, shots=shots).result()

# # It is possible to split the circuits into multiple jobs and then give the results to the fitter as a list:
# t2cpmg_backend_result1 = qiskit.execute(t2cpmg_circs[0:5], backend,
#                                         shots=shots, noise_model=t2_noise_model,
#                                         optimization_level=0).result()
# t2cpmg_backend_result2 = qiskit.execute(t2cpmg_circs[5:], backend,
#                                         shots=shots, noise_model=t2_noise_model,
#                                         optimization_level=0).result()


t2star_fit = T2StarFitter(t2star_backend_result, t2star_xdata, qubits,
                          fit_p0=[0.5, t_q0, osc_freq, 0, 0.5],
                          fit_bounds=([-0.5, 0, 0, -np.pi, -0.5],
                                      [1.5, 40, 2*osc_freq, np.pi, 1.5]))

plt.figure(figsize=(15, 6))
for i in range(2):
    ax = plt.subplot(1, 2, i+1)
    t2star_fit.plot(i, ax=ax)
plt.show()