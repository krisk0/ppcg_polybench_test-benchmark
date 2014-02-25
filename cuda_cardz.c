// This program is part of ppcg_polybench_test-benchmark
// Copyright Денис Крыськов 2014

#include <stdio.h>
#include <stdlib.h>
#include <cuda_runtime_api.h>

int card_found=0;
int cards_count=-1;

void dump(int x,int check_KERNEL_EXEC_TIMEOUT)
 {
  struct cudaDeviceProp p;
  cudaGetDeviceProperties(&p, x);
  if(check_KERNEL_EXEC_TIMEOUT && p.kernelExecTimeoutEnabled)
   return;
  printf("%d %d%d\n", x, p.major, p.minor);
  card_found=1;
 }

void all(int u)
 {
  int i;
  if(cards_count==-1)
   cudaGetDeviceCount(&cards_count);
  if(u==-1)
   for(i=0; i<cards_count; i++)
    dump(i,0);
  else
   if(u<cards_count)
    dump(u,0);
 }

void free_cards()
 {
  int i;
  cudaGetDeviceCount(&cards_count);
  for(i=0; i<cards_count; i++)
   dump(i,1);
 }

void free_or_all()
 {
  free_cards();
  if(card_found)
   return;
  all(-1);
 }

int main(int ac,char** av) 
 {
  if(ac==1)
   {
    free_or_all();
    return 0;
   }
  char* e;
  int u=strtol(av[1], &e, 0);
  if(*e)
   {
    //should be "all" or "free"
    if(!strcmp(av[1],"all"))
     {
      all(-1);
      return 0;
     }
    if(!strcmp(av[1],"free"))
     {
      free_or_all();
      return 0;
     }
    // garbage, ingored
    return 0;
   }
  all(u);
  return 0;
 }
