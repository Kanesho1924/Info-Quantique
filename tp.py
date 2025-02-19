import os
from dotenv import load_dotenv
from qiskit import QuantumCircuit
from qiskit.quantum_info import SparsePauliOp
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit_ibm_runtime import EstimatorV2 as Estimator
from qiskit_ibm_runtime import QiskitRuntimeService

load_dotenv()

token = os.getenv("IBM_API")
if token is None:
    raise ValueError("La variable d'environnement IBM_API n'est pas définie dans le fichier .env")


qc = QuantumCircuit(2)
qc.h(0)     
qc.cx(0, 1)  
qc.draw("mpl")  

QiskitRuntimeService.save_account(
    token=token,
    channel="ibm_quantum"
)
service = QiskitRuntimeService()

backend = service.least_busy(simulator=False, operational=True)


pm = generate_preset_pass_manager(backend=backend, optimization_level=1)
isa_circuit = pm.run(qc)
isa_circuit.draw("mpl", idle_wires=False)


observables_labels = ["IZ", "IX", "ZI", "XI", "ZZ", "XX"]
observables = [SparsePauliOp(label) for label in observables_labels]

estimator = Estimator(mode=backend)
estimator.options.resilience_level = 1
estimator.options.default_shots = 5000

mapped_observables = [
    observable.apply_layout(isa_circuit.layout) for observable in observables
]


job = estimator.run([(isa_circuit, mapped_observables)])
print(f">>> Job ID: {job.job_id()}")

job_result = job.result()
pub_result = job_result[0]
