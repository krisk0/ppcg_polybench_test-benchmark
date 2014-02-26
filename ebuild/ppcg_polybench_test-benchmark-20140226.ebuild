# Copyright 2014 Денис Крыськов

EAPI=4

inherit eutils

DESCRIPTION="A script to automatically turn polybench code to CUDA via ppcg"
LICENSE=as-is
HOMEPAGE=https://github.com/krisk0/$PN
SRC_URI="$HOMEPAGE/archive/$PV.zip -> $P.zip"
RESTRICT='mirror test'
DOCS=( README.rst sample/all.cards.MINI/runme )
RDEPEND=dev-lang/python
SLOT=0

src_compile()
 {
  local nvcc_exe=''
  [ -n "$NVCC" ] && 
   {
    nvcc_exe="$NVCC"
    [ -x "$nvcc_exe" ] || die "Bad NVCC setting"
   }
  while [ 1 ]; do
   [ -x "$nvcc_exe" ] && break
   nvcc_exe=`which nvcc 2>/dev/null`
   [ -x "$nvcc_exe" ] && break
   nvcc=/opt/cuda/bin/nvcc
   [ -x "$nvcc_exe" ] && break
   einfo "Failed to find nvcc executable."
   die "Please set NVCC=<full name of installed nvcc>"
  done
  "$nvcc_exe" cuda_cardz.c -o cuda_cardz || die
 }

src_install()
 {
  default
  dobin cuda_cardz ppcg_polybench_benchmark.py
 }
