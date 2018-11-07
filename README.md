# What is this?

This repo contains the code that was used to generate the results for the publication
'Implementing a distance-based classifier with a quantum interference circuit' by Schuld, Fingerhuth and Petruccione (2017).
The article was published in Europhysics Letters on December 1st 2017 and is an Editor's Choice article.

Article DOI:
https://doi.org/10.1209/0295-5075/119/60002

arXiv link:
https://arxiv.org/pdf/1703.10793.pdf

# How to make use of this repository?

Update Nov. 2018: I've rewritten the old QASM code in Python 3.7 and the newest Qiskit.

The file `qiskit_distance_based_classifier.py` contains the `DistanceBasedClassifier` class which performs the classification
of the two Iris flower datapoints `x'` and `x''` that were used in the original publication.

You can run the code with the following command:

```
$ python3 qiskit_distance_based_classifier.py
```

The printed information should be self-explanatory. Note, that the simulation is performed with the new IBM Aer QASM simulator.

For everyone who wants to dive deeper, the subdirectory `old_qasm_files` contains the old files written in quantum assembly language (QASM), which is the OG programming language used by the online interface
of the IBM Quantum Experience. In order to execute these files you have several options:

a) make an account with the IBM Quantum Experience, start a new Experiment and then simply copy & paste the code from one of the two QASM files into the QASM Editor in the IBM online interface. Then you can either simulate or run the defined quantum circuit on the actual chip.

b) import the QASM file into Qiskit by using the `qiskit.wrapper._wrapper.load_qasm_file` method from Qiskit. For documentation [see here](https://qiskit.org/documentation/_autodoc/qiskit.wrapper._wrapper.html?highlight=load%20qasm#qiskit.wrapper._wrapper.load_qasm_file).

NOTE: These QASM files were specifically written for the ibmqx2 bowtie chip with 5 qubits.

The `old_qasm_files` directory contains the following two files:

- `x0_class0_classification.qasm` Classification of the input vector x' as discussed in the EPL publication.

- `x1_class0_classification.qasm` Classification of the input vector x'' as discussed in the EPL publication.

--------------------------------------------------------------------------------------------------

If you happen to use this code please cite our paper:

Schuld, M., Fingerhuth, M., & Petruccione, F. (2017). Implementing a distance-based classifier with a quantum interference circuit. EPL (Europhysics Letters), 119(6), 60002.

bibTex:
```
@article{schuld2017implementing,
  title={Implementing a distance-based classifier with a quantum interference circuit},
  author={Schuld, Maria and Fingerhuth, Mark and Petruccione, Francesco},
  journal={EPL (Europhysics Letters)},
  volume={119},
  number={6},
  pages={60002},
  year={2017},
  publisher={IOP Publishing}
}
```


*The code is published open-source under a standard MIT License. Feel free to download, modify, use and multiply!*
