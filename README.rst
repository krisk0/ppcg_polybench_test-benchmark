ppcg_polybench_test-benchmark
=============================

ppcg meets Polybench in your NVIDIA card, where 

* `ppcg <http://repo.or.cz/w/ppcg.git>`_ is a source-to source compiler 
* `Polybench <http://www.cse.ohio-state.edu/~pouchet/software/polybench>`_ is a collection of structured C code    
* NVIDIA card is a device you got tired of programming directly

By design *ppcg_polybench_test-benchmark* carries no extra depependancies (except Python).
 
System requirements:
--------------------
 1. ppcg tool, Polybench-C test-suite, NVIDIA toolkit, ability to run CUDA executables;
 2. NVIDIA toolchain should include gcc (or at least gcc should be able to link object code created by nvcc);
 3. Python version 2.* (mine is currently 2.7.5).
 4. Core utilities such as *which* and *diff*.
 
What my code does
-----------------
For every test in Polybench-c suite,

1) compiles it into ordinary CPU executable;
2) asks ppcg to automagically convert it;
3) crunches it here and there so it compiles;
4) compile the crunched code to object code with nvcc;
5) link result with gcc (hence requirement 2 is there)
    
How does it all work? Great, sometimes... 26 tests of 30 produce exactly same result on CPU and GPU... for smallest available datasize DATASIZE=MINI. What happens for the rest 4? One segfault and 3 slightly different results. Well, at least I think the difference is slight. Get *.rez* files from *sample/all.cards.MINI* and see for yorself

*diff cholesky_sm_21__MINI.rez cholesky_cpu_MINI.rez*

Quick start
-----------
Compile *cuda_cardz.c*, place two executables *cuda_cardz* and *ppcg_polybench_benchmark.py*, run script *sample/all.cards.MINI/runme*, modify it if needed.
