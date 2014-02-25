ppcg_polybench_test-benchmark
=============================

ppcg meets Polybench in your NVIDIA card

where 

 ppcg is a source-to source compiler found at http://repo.or.cz/w/ppcg.git

 Polybench is a collection of structured C code http://www.cse.ohio-state.edu/~pouchet/software/polybench
 
 NVIDIA card is a device you got tired of programming directly
 
System requirements:
 1. gcc should be able to link object code created by nvcc so you can later run it on your NVIDIA card. Of course, you got CUDA toolkit, drivers are NVIDIA, so you can run CUDA executables.
 2. Python. I guess version 2.5-3.3 should do. #Take 2.7.x to be sure
 
What my code does.

1) For every test in Polybecnch-c suite,
    compiles it into ordinary CPU executable
    asks ppcg to automagically convert it
    crunches it here and there so it compiles
    compile the crunched code to object code with nvcc
    link result with gcc. That's where you need gcc.
    
2) Does it all work? Yep, always... nearly... 26 tests of 30 produce exactly same result on CPU and GPU... for smallest available datasize DATASIZE=MINI. What happens for the rest 4? One segfault and 3 slightly different results:

# diff cholesky_sm_21__MINI.rez cholesky_cpu_MINI.rez 
6c6
< 0.03 0.03 0.03 0.03 0.03 0.03 0.03 0.03 0.03 0.03 0.03 0.03 0.03 0.03 0.03 0.18 0.00 -nan 0.03 0.03 
---
> 0.03 0.03 0.03 0.03 0.03 0.03 0.03 0.03 0.03 0.03 0.03 0.03 0.03 0.03 0.03 0.18 0.00 0.00 0.03 0.03
...

And don't ask me what happens with larger data such as DATASIZE=STANDARD. Just run that yourself.
