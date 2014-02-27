# Copyright 2014 Денис Крыськов

EAPI=4

inherit eutils

DESCRIPTION="PolyBench/C: set of C code to benchmark/test code transform tools"
HOMEPAGE=http://www.cse.ohio-state.edu/~pouchet/software/polybench
SRC_URI=$HOMEPAGE/download/$P.tar.gz
doc="README AUTHORS"
DOCS=( $doc )
SLOT=0
KEYWORDS=*
LICENSE=as-is

src_install()
 {
  default
  rm $doc
  insinto "$EPREFIX/usr/share/$P"
  doins -r .
 }
