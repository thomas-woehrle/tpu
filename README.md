# tpu

Project creating a General Matrix Multiply (GEMM) unit and corresponding verification framework. A future attempt could be to extend this into a full-out TPU. The project takes inspiration from [Google's TPU](https://arxiv.org/abs/1704.04760). 

See also the Acknowledgements section below.

## Overview 

### src

Here, you can find the hardware designs. They are described using Verilog. The goal is to enable efficient matrix multiplication using systolic arrays. The top-level module is SystolicMatrixMultiplier.v. 

You can find more through explanations in the respective files. 

### tests

Here, you can find the verification of the hardware designs. To this end, [cocotb](https://www.cocotb.org) was employed. 

Tests can be run via the following interface:

`python test_runner.py <path_to_dir_with_verilog_designs> <name_of_module_to_be_tested> (optional:) <parameter_name>=<parameter_value>`

For example:

`python test_runner.py ../src SystolicMatrixMultiplier` or 

`python test_runner.py ../src SystolicMatrixMultiplier N=16 OP_WIDTH=4`

### docs

Here, you can find documentation or additional information regarding the project. 

## Acknowledgments
This project was conducted as part of the “Creation of Deep Learning Methods“ Practical Course at the Technical University Munich. It is loosely based on [prior work](https://github.com/ruzicka02/NN.FPGA) from the same course. Special thanks to Vladimir Golkov and Dirk Stober who provided guidance and supervision throughout the project.
