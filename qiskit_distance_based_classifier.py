#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2018 markf94 <markf94@deX1carbon>
#
# Distributed under terms of the MIT license.

"""
Quick and dirty rewrite of the old QASM files with modern Qiskit in Python 3.X to regenerate the results for the publication 'Implementing a distance-based classifier with a quantum interference circuit' by Schuld, Fingerhuth and Petruccione (2017).

This modern rewrite of the quantum assembly code is meant for educational purposes.
"""

from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister
from qiskit import execute, Aer

class DistanceBasedClassifier:

    def initialize_registers(self, num_registers):
        """
        Creates quantum and classical registers
        with `num_registers` qubits each.
        """
        self.q = QuantumRegister(4)
        self.c = ClassicalRegister(4)

        # name the individual qubits for more clarity
        self.ancilla_qubit = self.q[0]
        self.index_qubit = self.q[1]
        self.data_qubit = self.q[2]
        self.class_qubit = self.q[3]

    def create_circuit(self, angles):
        """
        Creating the quantum circuit
        by filling in the gaps with the
        defined `angles`.
        """
        # create empty quantum circuit
        qc = QuantumCircuit(self.q, self.c)

        #######################################
        #START of the state preparation routine

        # put the ancilla and the index qubits into uniform superposition
        qc.h(self.ancilla_qubit)
        qc.h(self.index_qubit)

        # loading the test vector (which we wish to classify)
        # [-0.549, 0.836] -> class 0 (x tilde single prime in the paper)
        qc.cx(self.ancilla_qubit, self.data_qubit)
        qc.u3(-4.30417579487669/2, 0, 0, self.data_qubit)
        qc.cx(self.ancilla_qubit, self.data_qubit)
        qc.u3(4.30417579487669/2, 0, 0, self.data_qubit)

        # barriers make sure that our circuit is being executed the way we want
        # otherwise some gates might be executed before we want to
        qc.barrier()

        # flipping the ancilla qubit > this moves the input vector to the |0> state of the ancilla
        qc.x(self.ancilla_qubit)

        qc.barrier()

        # loading the first training vector
        # [0,1] -> class 0
        # we can load this with a straightforward Toffoli

        qc.ccx(self.ancilla_qubit, self.index_qubit, self.data_qubit)

        qc.barrier()

        # flip the index qubit > moves the first training vector to the |0> state of the index qubit
        qc.x(self.index_qubit)

        qc.barrier()

        # loading the second training vector
        # [0.78861, 0.61489] -> class 1

        qc.ccx(self.ancilla_qubit, self.index_qubit, self.data_qubit)

        qc.cx(self.index_qubit, self.data_qubit)
        qc.u3(1.3245021469658966/4, 0, 0, self.data_qubit)
        qc.cx(self.index_qubit, self.data_qubit)
        qc.u3(-1.3245021469658966/4, 0, 0, self.data_qubit)

        qc.ccx(self.ancilla_qubit, self.index_qubit, self.data_qubit)

        qc.cx(self.index_qubit, self.data_qubit)
        qc.u3(-1.3245021469658966/4, 0, 0, self.data_qubit)
        qc.cx(self.index_qubit, self.data_qubit)
        qc.u3(1.3245021469658966/4, 0, 0, self.data_qubit)

        qc.barrier()

        ####################################################
        # END of state preparation routine

        # at this point we would usually swap the data and class qubit
        # however, we can be lazy and let the Qiskit compiler take care of it

        # flip the class label for training vector #2
        qc.cx(self.index_qubit, self.class_qubit)

        qc.barrier()

        #############################################
        # START of the mini distance-based classifier

        # interfere the input vector with the training vectors
        qc.h(self.ancilla_qubit)

        qc.barrier()

        # Measure all qubits and record the results in the classical registers
        qc.measure(self.q, self.c)

        #############################################
        # START of the mini distance-based classifier

        return qc

    def simulate(self, quantum_circuit):
        """
        Compile and run the quantum circuit
        on a simulator backend.
        """

        backend_sim = Aer.get_backend('qasm_simulator')
        job_sim = execute(quantum_circuit, backend_sim)

        # retrieve the results from the simulation
        return job_sim.result()

    def classify(self, test_vector, training_vectors):
        """
        Classifies the `test_vector` with the
        distance-based classifier using the `training_vectors`
        as the training set.
        """

        self.initialize_registers(num_registers=4)
        qc = self.create_circuit(angles=[])
        result = self.simulate(qc)

        # Show the results
        print(f'simulation: {result}')
        print(result.get_counts(qc))

if __name__ == "__main__":

    classifier = DistanceBasedClassifier()
    classifier.classify(test_vector=[], training_vectors=[[],[]])
