# Copyright 2014 Денис Крыськов

EAPI=4
inherit autotools eutils

DESCRIPTION="Sven Verdoolaege's source-to-source compiler, with testsuite"
# Test requirements: CUDA device and software
# Test will be skipped if no CUDA-capable device
LICENSE=MIT
repo=http://repo.or.cz/w       # $repo/@project@.git/snapshot/@commit@.zip
animal=pet                     # project is either pet or $PN
                               #  pet is git name, subdir name, part of distfile name
                                   
HOMEPAGE=$repo/ppcg.git
animal_commit='cfcde32488e76463e2f2b14a310417ac84545feb'
ppcg_commit='263c202d2a3954028073acc2436d97e65c7e976e'

IUSE='no_pet test'

#README says: take version 3.3. So be it
DEPEND="  >=sys-devel/llvm-3.3 
         >=sys-devel/clang-3.3
 test? ( dev-util/nvidia-cuda-toolkit app-benchmarks/polybench-c )
 dev-libs/isl
 dev-libs/libyaml"   # 0.1.5 appears to work

KEYWORDS="amd64 x86 amd64-linux x86-linux" # stolen from nvidia-cuda-tookit

SRC_URI="
$repo/$PN.git/snapshot/$ppcg_commit.zip -> $P.zip
$repo/$animal.git/snapshot/$animal_commit.zip -> $PN_$animal-$PV.zip
test? ( http://ge.tt/8E3f0TK1/ppcg_polybench_test-benchmark-20140220.zip )"
S="$WORKDIR/$PN"
SLOT=0
# will access NVIDIA devices, even if portage is not in video group
RESTRICT="userpriv"

src_test()
 {
  local s='No NVIDIA devices, test skipped'
  [ -e /dev/nvidiactl ] || { einfo "$s" ; return; }
  addwrite /dev/nvidiactl
  local x=0
  while [ 1 ] ; do
   [ -e /dev/nvidia$x ] || break
   addwrite /dev/nvidia$x
   x=$((x+1))
  done
  [ $x == 0 ] && { einfo "$s" ; return; }
  cd ppcg_polybench_test-benchmark || die
  nvcc cuda_cardz.c -o cuda_cardz || die
  ./cuda_cardz $CUDA_DEVICE > cuda_cardz.cout
  [ -z $CUDA_DEVICE ] && 
   {
    # no user-selected card, run test on auto-selected CUDA cards
    [ -s cuda_cardz.cout ] ||
     {
      #should never come here
      einfo "$s" ; return
     }
   }
  [ -n $CUDA_DEVICE ] && 
   {
    # detect compute capability of user-selected card, abort on error
    [ -s cuda_cardz.cout ] || die "Card $CUDA_DEVICE is not CUDA-capable"
   }
  # can be one or more cards.        Delete end-of-line
  x=`cut -d' ' -f1 cuda_cardz.cout`; x=`echo $x`
  einfo "Will run test on card $x"
  # DELETE_POLICY: don't delete failed tests results and intermediate files
  cat cuda_cardz.cout | 
   PPCG="$S/ppcg`egrep ^EXEEXT=../polybench_test.sh|cut -d= -f2`" \
   POLYBENCH="`egrep ^DIR= ../polybench_test.sh|cut -d= -f2`" \
   SCRATCH="$S/test.scratch" \
   DELETE_POLICY=on_success \
   TGT_PREFIX="$S/polybench-test-" \
   DATASET_SIZE=MIDDLE \
   ./ppcg_polybench_benchmark.py || die
 }

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
  # if test planned, put polybench tester here, too
  use test && { mv $WORKDIR/ppcg_polybench_test-benchmark $S || die ; }
 }

polybench_whereabouts()
 {
  # any /usr/share/polybench-c-* will do
  for x in /usr/share/polybench-c-* ; do
   echo $x
   return
  done
  die '/usr/share/polybench-c-* not found'
 }

src_configure()
 {
  ./autogen.sh || die
  # configure uses opencl voodoo to see if your CPU is OpenCL-complaint.
  # If opencl driver comes from NVIDIA then /dev/nvidia* devives 
  #  are accessed, and emerge fails with sandbox violation. 

  # Allow access to the devices, if present
  [ -e /dev/nvidiactl ] && addwrite /dev/nvidiactl
  local x=0
  while [ 1 ] ; do
   [ -e /dev/nvidia$x ] || break
   addwrite /dev/nvidia$x
   x=$((x+1))
  done
   
  local polybench
  use test && 
   {
    polybench=`polybench_whereabouts`
    einfo "Using test suite $polybench"
    polybench="--with-polybench=$polybench"
   }
  ./configure --with-isl=system --prefix=/usr $polybench || die
 }

src_install()
 {
  default
  use no_pet && einfo "$animal executable not installed due to no_pet USE flag"
  ! use no_pet && einfo "installed both executables: $PN and $animal"
  use test && [ -f polybench-test-summary ] &&
   dodoc polybench-test-summary
 }
