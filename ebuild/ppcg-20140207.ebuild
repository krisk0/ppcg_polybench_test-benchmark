# Copyright 2014 Денис Крыськов

EAPI=4
inherit autotools eutils

DESCRIPTION="Sven Verdoolaege's source-to-source compiler"
LICENSE=MIT
repo=http://repo.or.cz/w       # $repo/@project@.git/snapshot/@commit@.zip
animal=pet                     # project is either pet or $PN
                               #  pet is git name, subdir name, part of distfile name
                                   
HOMEPAGE=$repo/ppcg.git
animal_commit='cfcde32488e76463e2f2b14a310417ac84545feb'
ppcg_commit='263c202d2a3954028073acc2436d97e65c7e976e'

#README says: take version 3.3. So be it
DEPEND="  >=sys-devel/llvm-3.3 
         >=sys-devel/clang-3.3
 dev-libs/libyaml"   # 0.1.5 appears to work

KEYWORDS="amd64 x86" # not sure about theese

SRC_URI="
$repo/$PN.git/snapshot/$ppcg_commit.zip -> $P.zip
$repo/$animal.git/snapshot/$animal_commit.zip -> $PN_$animal-$PV.zip"
S="$WORKDIR/$PN"
SLOT=0
IUSE='no_pet'

# test not supported
RESTRICT='test mirror'  # To test ppcg: 
# 1. Take http://www.cse.ohio-state.edu/~pouchet/software/polybench/
# 2. Buy OpenCL-capable CPU (no, GPU not supported by ppcg test script
#     polybench_test.sh.in -> polybench_test.sh)
# 3. Install software that trusts your CPU to be OpenCL-capable
# 4. ? Convince configure to enable OpenCL and use correct compiler for testing

DOCS=( README $animal.README )

src_unpack()
 {
  default
  einfo "dog, come here"
  mv $WORKDIR/$animal $S || die
  mv $S/$animal/README $S/$animal.README
  use no_pet &&
   {
    cd $S/$animal
    # instruct make not to release any executable here
    sed -i Makefile.am \
     -e 's-EXTRA_PROGRAMS =.*-EXTRA_PROGRAMS =-' \
     -e '/extra_bin_programs/d' \
     -e "s=@extra_noinst_programs@==g" 
    sed -i Makefile.am \
     -e "s:noinst_PROGRAMS = .*:\0 $animal ${animal}_scop_cmp:"
   }
 }

src_configure()
 {
  ./autogen.sh || die
  einfo "test not supported, see comment in ebuild for details"
  # configure uses opencl voodoo to see if your CPU is OpenCL-complaint.
  # If opencl driver comes from NVIDIA then /dev/nvidiactl is opened for 
  #  writing, and emerge fails with sandbox violation. 

  # Allow access to the device, if present

  [ -e /dev/nvidiactl ] && addwrite /dev/nvidiactl
  ./configure --with-isl=system --prefix=/usr || die
 }

src_install()
 {
  default
  use no_pet && einfo "$animal executable not installed due to no_pet USE flag"
  ! use no_pet && einfo "installed both executables: $PN and $animal"
 }
