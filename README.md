Prototypical implementation towards automated benchmarking environment for batch processing. 
See the [related master thesis](https://github.com/jnsrnhld/masterthesis-latex) for detailed background information.

### Setup

Follow [this guide](ansible/README.md) to set up the software stack.

### Benchmarks

To run benchmarks, adjust the [benchmark definition](ansible/benchmark-definition.yaml) and run the 
[hibench playbook](ansible/playbooks/hibench.yaml).

### Generic Spark listener

The prototypical implementation for the generic Spark listener can be found [here](listener). 
