# Copyright 1999-2013 Gentoo Foundation
# Copyright 2014 Денис Крыськов
# Distributed under the terms of the GNU General Public License v2

EAPI=4
inherit autotools eutils

DESCRIPTION="A library for manipulating integer points bounded by affine constraints"
HOMEPAGE=http://freecode.com/projects/isl
ISL_commit='1b3ba3b72c0482fd36bf0b4a1186a259f7bafeed'
SRC_URI="http://repo.or.cz/w/isl.git/snapshot/${ISL_commit}.zip -> 
 isl-$PV.zip"

LICENSE=MIT
SLOT=0
KEYWORDS="amd64 arm hppa mips x86 amd64-fbsd x86-fbsd"
IUSE="static-libs exe_please" # exe_please: install some executables

RDEPEND="dev-libs/gmp"
DEPEND="${RDEPEND} 
       dev-texlive/texlive-latex" # /usr/bin/pdflatex builds manual.pdf

S="$WORKDIR/$PN"

DOCS=( ChangeLog AUTHORS doc/manual.pdf README )

src_prepare() 
 {
	 #patch ${PN}-0.07-gdb-autoload-dir.patch no longer works
  sed -e 's:$(DESTDIR)$(libdir):$(DESTDIR)usr/share/gdb/auto-load$(libdir):g' \
   -i Makefile.am
  use exe_please && sed -e s=noinst_PROGRAMS=bin_PROGRAMS=g -i Makefile.am
  eautoreconf || die
 }

src_configure() {
	econf $(use_enable static-libs static)
}

src_compile()
 {
  default
  emake -C doc manual.pdf
 }

src_install()
 {
  default
  prune_libtool_files
 }
