#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2018 markf94 <markf94@deX1carbon>
#
# Distributed under terms of the MIT license.

"""
Quick and dirty rewrite of the old QASM files with modern Qiskit
in Python 3.X to regenerate the results for the publication
'Implementing a distance-based classifier with a quantum interference circuit'
by Schuld, Fingerhuth and Petruccione (2017).

This modern rewrite of the quantum assembly code is meant for educational purposes.
"""

from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister
from qiskit import execute, BasicAer

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
        defined `angles` that are required
        to load the test and training vectors.
        """

        # create empty quantum circuit
        qc = QuantumCircuit(self.q, self.c)

        #######################################
        #START of the state preparation routine

        # put the ancilla and the index qubits into uniform superposition
        qc.h(self.ancilla_qubit)
        qc.h(self.index_qubit)

        # loading the test vector (which we wish to classify)
        qc.cx(self.ancilla_qubit, self.data_qubit)
        qc.u3(-angles[0], 0, 0, self.data_qubit)
        qc.cx(self.ancilla_qubit, self.data_qubit)
        qc.u3(angles[0], 0, 0, self.data_qubit)

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
        qc.u3(angles[1], 0, 0, self.data_qubit)
        qc.cx(self.index_qubit, self.data_qubit)
        qc.u3(-angles[1], 0, 0, self.data_qubit)

        qc.ccx(self.ancilla_qubit, self.index_qubit, self.data_qubit)

        qc.cx(self.index_qubit, self.data_qubit)
        qc.u3(-angles[1], 0, 0, self.data_qubit)
        qc.cx(self.index_qubit, self.data_qubit)
        qc.u3(angles[1], 0, 0, self.data_qubit)

        qc.barrier()

        # END of state preparation routine
        ####################################################

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

        # END of the mini distance-based classifier
        #############################################

        return qc

    def simulate(self, quantum_circuit):
        """
        Compile and run the quantum circuit
        on a simulator backend.
        """

        # noisy simulation
        backend_sim = Aer.get_backend('qasm_simulator')

        job_sim = execute(quantum_circuit, backend_sim)

        # retrieve the results from the simulation
        return job_sim.result()

    def get_angles(self, test_vector, training_vectors):
        """
        Return the angles associated with
        the `test_vector` and the `training_vectors`.

        Note: if you want to extend this classifier
        for other test and training vectors you need to
        specify the angles here!
        """
        angles = []

        if test_vector == [-0.549, 0.836]:
            angles.append(4.30417579487669/2)
        elif test_vector == [0.053 , 0.999]:
            angles.append(3.0357101997648965/2)
        else:
            print('No angle defined for this test vector.')

        if training_vectors[0] == [0, 1] and training_vectors[1] == [0.78861006, 0.61489363]:
            angles.append(1.3245021469658966/4)
        else:
            print('No angles defined for these training vectors.')

        return angles

    def interpret_results(self, result_counts):
        """
        Post-selecting only the results where
        the ancilla was measured in the |0> state.
        Then computing the statistics of the class
        qubit.
        """

        total_samples = sum(result_counts.values())

        # define lambda function that retrieves only results where the ancilla is in the |0> state
        post_select = lambda counts: [(state, occurences) for state, occurences in counts.items() if state[-1] == '0']

        # perform the postselection
        postselection = dict(post_select(result_counts))
        postselected_samples = sum(postselection.values())

        print(f'Ancilla post-selection probability was found to be {postselected_samples/total_samples}')

        retrieve_class = lambda binary_class: [occurences for state, occurences in postselection.items() if state[0] == str(binary_class)]

        prob_class0 = sum(retrieve_class(0))/postselected_samples
        prob_class1 = sum(retrieve_class(1))/postselected_samples

        print(f'Probability for class 0 is {prob_class0}')
        print(f'Probability for class 1 is {prob_class1}')

        return prob_class0, prob_class1

    def classify(self, test_vector, training_set):
        """
        Classifies the `test_vector` with the
        distance-based classifier using the `training_vectors`
        as the training set.

        This functions combines all other functions of this class
        in order to execute the quantum classification.
        """

        # extract training vectors
        training_vectors = [tuple_[0] for tuple_ in training_set]

        # initialize the Q and C registers
        self.initialize_registers(num_registers=4)

        # get the angles needed to load the data into the quantum state
        angles = self.get_angles(
                test_vector=test_vector,
                training_vectors=training_vectors
        )

        # create the quantum circuit
        qc = self.create_circuit(angles=angles)

        # simulate and get the results
        result = self.simulate(qc)

        prob_class0, prob_class1 = self.interpret_results(result.get_counts(qc))

        if prob_class0 > prob_class1:
            return 0
        elif prob_class0 < prob_class1:
            return 1
        else:
            return 'inconclusive. 50/50 results'


if __name__ == "__main__":

    # initiate an instance of the distance-based classifier
    classifier = DistanceBasedClassifier()

    x_prime = [-0.549, 0.836] # x' in publication
    x_double_prime = [0.053 , 0.999] # x'' in publication

    # training set must contain tuples: (vector, class)
    training_set = [
        ([0, 1], 0), # class 0 training vector
        ([0.78861006, 0.61489363], 1) # class 1 training vector
    ]

    print(f"Classifying x' = {x_prime} with noisy simulator backend")
    class_result = classifier.classify(test_vector=x_prime, training_set=training_set)
    print(f"Test vector x'' was classified as class {class_result}\n")

    print('===============================================\n')

    print(f"Classifying x'' = {x_double_prime} with noisy simulator backend")
    class_result = classifier.classify(test_vector=x_double_prime, training_set=training_set)
    print(f"Test vector x' was classified as class {class_result}")
