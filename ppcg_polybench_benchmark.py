#!/usr/bin/python2
# -*- coding: utf-8

# This program is part of ppcg_polybench_test-benchmark
# Copyright Денис Крыськов 2014

import os,sys,subprocess,fnmatch,time

OSe=os.environ.get
run_exe=subprocess.check_output

def find_subdir(d,m):
 l=os.listdir(d)
 for i in l:
  if fnmatch.fnmatch( i, m ):
   j=d+'/'+i
   if os.path.isdir(j):
    return j

def zap_files( d, m ):
 l=os.listdir(d)
 for i in l:
  if fnmatch.fnmatch( i, m ):
   j=d+'/'+i
   if os.path.isfile(j):
    os.unlink(j)

def mask_delete_policy( x ):
 m=0
 if x=='on_success':
  m = 1
 if x=='on_failure':
  m = 2
 if x=='always':
  m = 3
 return m

def log(x):
 o=open(tgt_prefix+'results','ab')
 o.write(x)

def usr_bin( pp ):
 for p in pp:
  usr_bin_subr(p)
 
def usr_bin_subr( x ):
 y=OSe( x.upper() )
 if y==None:
  try:
   y=run_exe(["which", x])
  except:
   log('Failed to find executable '+x),sys.exit(1)
 globals()[x]=y.strip()

all_tools=['ppcg','nvcc','gcc']
#                          nvcc likes space after -I
#Cflags=' -DPOLYBENCH_DUMP_ARRAYS=1 -DPOLYBENCH_USE_C99_PROTO=1 -D%s_DATASET=1 -I i ' 
Cflags=' -DPOLYBENCH_DUMP_ARRAYS=1 -DPOLYBENCH_USE_C99_PROTO=1 -D%s_DATASET=1 ' 
Lflags=None

def get_tgt_prefix(p):
 p=p.strip()
 if p.find( '\\' )!=-1:
  print 'is'
  print 'Backslashes in environment variables defining filenames not supported'
  sys.exit(1)
 if p.find('/')==-1:
  p=os.getcwd()+'/'+p
 return p

strict_compare_result=1
epsilon=float( OSe('EPSILON','0.02') )
DATA_TYPE='double'   # can make it float instead; need to change Cflags for that

# take env variables. Strip bad chars from head or tail of file names,
#  to delete end-of-line coming from *sh/find/locate/head utilities
tgt_prefix=get_tgt_prefix( OSe('TGT_PREFIX','polybench_cuda_test-') )
usr_bin( all_tools )
scratch=OSe('SCRATCH')
if scratch==None:
 import tempfile
 scratch=tempfile.mkdtemp(suffix='ppcg_polybench_test-benchmark')
delete_policy=mask_delete_policy( OSe('DELETE_POLICY','on_success') )
polybench=OSe('POLYBENCH')
if polybench==None:
 polybench=find_subdir('/usr/share','polybench-c-*')
else:
 polybench=polybench.strip()
Cflags += '-I "%s" ' % (polybench+'/utilities/')

def dataset_size_to_list(x):
 x,z=x.strip().split(','),[]
 for y in x:
  if len(y)>1:
   z.append(y)
 return z

dataset_size=dataset_size_to_list( OSe('DATASET_SIZE','STANDARD') )

def check_CC( x ):
 m='Bad compute capability '+x
 try:
  x=int(x)
 except:
  log(m),sys.exit(1)
 if x<10 or x>99:
  log(m),sys.exit(1)
 return 'sm_%d' % x

no_cap=dict()
for x in sys.stdin.readlines():
 for y in x.strip().split(','):
  if len(y)>1:
   no,cap=y.strip().split(' ')
   try:
    no,cap=int(no),check_CC(cap)
   except:
    log('Bad card no '+no),sys.exit(1)
   no_cap[no]=cap
arch_list=no_cap.values()
arch_list_0=arch_list[0]
single_zero_card=len(no_cap)==1 and no_cap.has_key(0)

def loop_on_benchmark_list():
 i=open(polybench+'/utilities/benchmark_list','rb')
 s=time.time()
 while 1:
  t=i.readline()
  if t=='':
   break
  do_test( t[1:].rstrip() )
  # abort after                           99999 tests
  if stat_passed+stat_skipped+stat_failed>99999:
   break
 s=time.time()-s
 global loop_time
 loop_time=s

def fill_to_(x,a):
 s=len(a)
 if s>=x:
  return a
 return (' '*(x-s))+a

def statistic():
 with open(tgt_prefix+'summary','ab') as o:
  t=0
  for x in 'passed','skipped','failed':
   c=globals()[ 'stat_'+x ]
   t += c
   x_long=fill_to_(7,x)
   o.write( 'Tests '+x_long+': %s\n' % c )
  o.write( 'Tests '+fill_to_(7,'total')+': %s\n\n' % t )
  if len(time_global):
   d,m=dict(),0
   for i in time_global.items():
    j=i[0]
    if j[1]=='|':
     j='gpu'+j
    if j[3] == '|':
     j=' '+j
    d[j]=i[1]
    j=len(j)
    if m<j:
     m=j
   for i in sorted(d.items()):
    o.write( fill_to_(m,i[0])+(' %.2f\n' % i[1]) )
  o.write( 'Total time spent: %.2f\n' % loop_time )

def gcc_compile( i_short, i_long, d ):
 zap_files( '.', i_short+'*' )
 i_c=i_short+'.c'
 #If patches are needed for .c, do them here
 run_exe(['cp',i_long,i_c])
 ff=[i_c]
 f='%s_cpu_%s' % (i_short,d)
 c=gcc+' -O2'+(Cflags % d)+'-I'+os.path.dirname(i_long)+' -o '+f+' '+i_c+polybench_c
 err=run_exe(c+';exit 0;',stderr=subprocess.STDOUT,shell=True)
 global gcc_exe_ext
 if gcc_exe_ext==None:
  gcc_exe_ext=detect_exe_ext_2arg( f+'*', '.c' )
  if gcc_exe_ext != None:
   ff.append( f+gcc_exe_ext )
   return ff,0,None
 else:
  if os.path.isfile(f+gcc_exe_ext):
   ff.append( f+gcc_exe_ext )
   return ff,0,None
 ' small problem or big problem '
 extra_switch=what_else_needed( i_long, err )
 if extra_switch==None:
  return ff,1,None
 c += ' '+gcc_switch(extra_switch)
 err=run_exe(c+';exit 0;',stderr=subprocess.STDOUT,shell=True)
 if gcc_exe_ext == None:
  gcc_exe_ext=detect_exe_ext_2arg( f+'*', '.c' )
  if gcc_exe_ext != None:
   ff.append( f+gcc_exe_ext )
   return ff,0,extra_switch
 if gcc_exe_ext != None and os.path.isfile(f+gcc_exe_ext):
  ff.append( f+gcc_exe_ext )
  return ff,0,extra_switch
 log(c+'\n------ gcc compilation failed with messages\n')
 log(err)
 log('------ end gcc messages\n')
 return ff,2,None

def dont_run_ppcg_again( cflags, c_file, arch, f_pref ):
 ' returns [f1,f2],e where f1 is _kernel.cu and f2 is _host.cu, e is err code '
 f1,f0=f_pref+'_kernel.cu',f_pref+'_host.cu'
 ff=[f1,f0]
 if ppcg_code_is_here( ff, arch ):
  return ff,0
 c=ppcg+cflags+c_file+' --target=cuda'
 err=run_exe(c+';exit 0',stderr=subprocess.STDOUT,shell=True)
 if os.path.getsize( f1 )==0:
  log( 'command '+c+' failed\n' )
  log( 'ppcg gave file '+f1+' of zero length\n' )
  log( err+'\n' )
  return ff,1
 try:
  os.unlink( f1[:-2]+'hu' )
  e=0
 except:
  e=1
  ff=list_files( ff )
 if e==0:
  e=patch_CUDA_c( f0, f1 )
 return ff,e

def ppcg_code_is_here( tgt, arch_new ):
 if arch_list_0==arch_new:
  return 0
 arch_old,arch_new = '_'+arch_list_0+'__','_'+arch_new+'__'
 tgt0,tgt1=tgt[0],tgt[1]
 sou0,sou1=tgt0.replace( arch_new, arch_old ),tgt1.replace( arch_new, arch_old )
 run_exe( ['cp',sou0,tgt0] ),run_exe( ['cp',sou1,tgt1] )
 return 1

def nvcc_compile(i_nick,i,size,arch,hint):
 '''
 compile i into i_nick_ARCH__SIZE using previous gcc experience stored
  in hint
  
 return list of files created and error code (1 if ppcg failed)
 '''
 f_pref='%s_%s__%s' % (i_nick,arch,size)
 c_file=f_pref+'.c'
 # zap_files( '.', f_pref+'*' )
 run_exe(['cp',i_nick+'.c',c_file])
 ff=[c_file]
 cflags=(Cflags+' -I %s ') % (size,os.path.dirname(i))
 f,e=dont_run_ppcg_again( cflags, c_file, arch, f_pref )
 ff += f
 if e:
  return ff,1
 f1,f0=f[0],f[1]
 f1o=f1[:-3]+'.o'
 nvcc_compile_o( nvcc+cflags+' -c '+f1+' -arch='+arch+' -o '+f1o, f1o )
 if not os.path.isfile(f1o):
  return ff,2
 ff.append(f1o)
 global Lflags
 if Lflags == None:
  Lflags=ask_nvcc_for_lflags( f1 )
 c=gcc+cflags+f1o+Lflags+'-xc '+f0+polybench_c+' -o '+f_pref
 e=gcc_switch( hint )
 if e!=None:
  c += ' '+e
 err=run_exe(c+';exit 0;',stderr=subprocess.STDOUT,shell=True)
 f_exe=f_pref+gcc_exe_ext
 if not os.path.isfile( f_exe ):
  log('\n'+c+'\n------ linking failed with messages\n')
  log(err)
  log('------ end of gcc messages\n')
  return ff,2
 ff.append( f_exe )
 return ff,0

def ask_nvcc_for_lflags( i ):
 ' ask nvcc to print -L and -l flags '
 ' could use nvcc -run instead of nvcc -dryrun '
 import shlex   # delay import, for quicker start
 def st(x):
  if len(x)<3:
   return 
  i=0
  if x[0] in "'\"":
   i += 1
  if x[i]=='-':
   return x[i+1]
 a,r=run_exe(nvcc+' -dryrun '+i+' 2>&1 |tail -1;exit 0',shell=True),''
 a=a.replace('#','')
 b,p,l=shlex.shlex(a),None,[]
 for i in b:
  if i != '-' and p=='-':
   l.append( p+i )
  else:
   if len(i)>1:
    l.append(i)
  p=i
 for i in l:
  if st(i) in ('l','L'):
   r += i+' '
 if r=='':
  log( 'a='+a+'\n' )
  log( 'l='+str(l)+'\n' )
  for i in l:
   log( ' substr: '+i+'\n' )
  log( "ask_nvcc_for_lflags() failed, don't know linking flags,"+
       " can't continue\n" ),sys.exit(1)
 return ' '+r+'-lstdc++ '

def patch_CUDA_c( f_main, f_kern ):
 add=crunch_main( f_main )
 if add == None:
  return 2
 crunch_kern( f_kern, add )
 patch_videocard_no( f_main )

def crunch_kern( o, w ):
 '''
 append to o some includes and one subroutine
 
 define CUDA_card_number if necessary
 '''
 with open(o,'ab') as t:
  t.write( '\n'+w['include']+'\n' )
  if not single_zero_card:
   t.write( '\nint CUDA_card_number;\n\n' )
  twice_please=w['head']
  t.write( 'extern "C" '+twice_please[:-1]+';\n\n'+twice_please )
  t.write( crunch_meat( w['tail'] ) )
 run_exe( ['sed','-e','s:#include ".*\.hu"$::','-i',o] )

def crunch_meat( i ):
 '''
  fix DATA_TYPE
  if necessary, insert cudaSetDevice() call
 '''
 i=i.replace('DATA_TYPE',DATA_TYPE)
 if not single_zero_card:
  if i[0] != '{':
   i=i.lstrip()
   if i[0] != '{':
    i='Bad meat start '+i[:100]
    log( i+'\n' )
    return i
  i='{\ncudaSetDevice(CUDA_card_number);\n'+i[1:]
 return i

def crunch_main( i ):
 o=i+'.crunch'
 inside_subr,r,hu_found=0,'',0
 with open(i,'rb') as inp,open(o,'wb') as out:
  while 1:
   c=inp.readline()
   if c=='':
    log( 'CUDA kernel call not found in '+i )
    return
   if hu_found and c.find( 'static' ) != -1:
    inside_subr=1
    subr=c
    continue
   if inside_subr:
    subr += c
    if c == '}\n':
     c=None
     inside_subr=0
     maybe_CUDA( r, subr, out )
     if r.has_key( 'tail' ):
      break
    continue
   ' respect #include <...> added by ppcg, put it later into _kernel.cu '
   if hu_found:
    if c != None:
     out.write( c )
   else:
    if c[-5:] == '.hu"\n':
     hu_found=1
     r=dict( {'include':r} )
     if not single_zero_card:
      out.write( 'extern int CUDA_card_number;\n' )
     continue
    else:
     r += c
  maybe_find_closing_bracket( inp, r )
  while 1:
   c=inp.readline()
   if c=='':
    break
   out.write(c)
 os.unlink(i)   # not needed on Linux
 os.rename(o,i)
 return r

def maybe_find_closing_bracket( f, r ):
 '''
 check {} bracers in r['tail']
 if not enough closin bracers, take them from f and append them to r['tail']
 '''
 c,b=r['tail'],0
 b=bracers_balance(c)
 if b <= 0:
  return
 while b>0:
  i=f.readline()
  b += bracers_balance(i)
  c += i
 r['tail']=c

def bracers_balance(x):
 r=0
 for b in x:
  if b=='{':
   r += 1
  else:
   if b=='}':
    r -= 1
 return r

def maybe_CUDA( result, subr_code, f ):
 '''
  if subroutine calls CUDA kernel, crunch it and return modified version
  
  else put it into f as-is
 '''
 if subr_code.find('<<<') == -1:
  f.write( subr_code )
  return
 in_header=1
 head=tail=ori_header=''
 subr_code=subr_code.split('\n')
 for c in subr_code:
  if in_header:
   head += crunch_header_line(c)
   ori_header += c+'\n'
   if c[-1] == ')':
    in_header=0
    head=prettify_subr_header( head )
    f.write('extern '+head[:-1]+';\n\n'+ori_header )
  else:
   tail += c+'\n'
 f.write( '{\n'+crunched_subr_call(head)+';\n}\n\n' )
 result['head']=head
 result['tail']=tail

def prettify_subr_header( x ):
 x=kill_spaces( x.replace('static','') )
 x=x.replace( 'DATA_TYPE', DATA_TYPE )
 while x.find( ',,' ) > -1:
  x=x.replace( ',,', ',' )
 x=x.replace( ',)', ')' ) 
 for s in '(', ',', ')':
  x=x.replace( s, s+'\n ' )
 x=x.replace('void ','void crunched_')
 return x[:-1]

def crunched_subr_call( h ):
 k,r=h.replace('void ','').split('\n'),''
 for i in k:
  r += strip_parameter_type( i.strip() )
 return ' '+r

def strip_parameter_type( x ):
 b,r=x.find(' '),x
 if b > -1:
  r=x[ b+1: ]
  if x[:b] == DATA_TYPE+'*':
   r='('+DATA_TYPE+'*)'+r
 return r

def crunch_header_line( s ):
 '''
  write each parameter on separate line
  transform DATA_TYPE smth( var, whatever ) into 
   DATA_TYPE* var
 '''
 s=kill_spaces( s )
 if s=='static':
  return ''
 if s=='':
  return ''
 q=s.find('(')
 if q > -1:
  p=s.find('DATA_TYPE')
  if p==-1 or p>q:
   return s[:q+1]+crunch_header_line( s[q+1:] )
 ' either no braces, or 1 or more DATA_TYPE POLYBENCH_xd() voodoo '
 if q > -1:
  s=zap_macro_parameters_in_procedure_def( s )
 if s.find( ',' ) == -1:
  ' lonely void or subroutine name? last parameter?'
  return crunch_procedure_parameter( s )+' '
 s,r=s.split(','),''
 for i in s:
  r += crunch_procedure_parameter( i )+','
 return r

def crunch_procedure_parameter( p ):
 p=p.strip()
 b=p.find( ' ' )
 if b==-1:
  return p
 if p[ :b ] == 'DATA_TYPE':
  try:
   return DATA_TYPE+'* '+p.split(' ')[2]
  except:
   pass
 return p

def kill_spaces(x):
 x=x.strip()
 while x.find('  ') > -1:
  x=x.replace('  ',' ')
 for z in ',','(',')':
  while x.find(z+' ') > -1:
   x=x.replace(z+' ',z)
  while x.find(' '+z) > -1:
   x=x.replace(' '+z,z)
 return x

def zap_macro_parameters_in_procedure_def( s0 ):
 ' replace ( a, b, c, ... ) with space a' 
 r,s='',s0
 while s != '':
  b=s.find('(')
  if b==-1:
   return r + s
  r += s[:b]+' '
  s=s[b+1:]
  b=s.find(')')
  if b==-1:
   return 'no closing brace ) in '+s0
  r += s[:b].split(',')[0]
  s = s[ b+1: ]
 return r

def patch_videocard_no( i ):
 if single_zero_card:
  # use default card no (zero), no need to patch
  return
 # insert into main() one line setting CUDA_card_number to c-l parameter
 # unistd.h appears to define atol()
 s='s|polybench_start_instruments;|\\0\\n  CUDA_card_number=atol(argv[1]);|'
 run_exe( ['sed','-e',s,'-i',i] )

def nvcc_link_hint( hint ):
 ' None or string to be added into nvcc link command-line '
 return gcc_switch( hint )

def nvcc_compile_o( c, f ):
 ' call nvcc to make .o, log error messages on failure '
 err=run_exe(c+';exit 0;',stderr=subprocess.STDOUT,shell=True)
 if not os.path.isfile(f):
  log('\n'+c+'\n------ nvcc compiling failed with messages\n')
  log(err)
  log('------ end nvcc messages\n')

def nvcc_compile_exe( c, f ):
 ' call nvcc to make .o, log error messages on failure '
 global nvcc_exe_ext
 err=run_exe(c+';exit 0;',stderr=subprocess.STDOUT,shell=True)
 if nvcc_exe_ext != None and not os.path.isfile(f+nvcc_exe_ext):
  nvcc_compile_exe_bug(c,err)
  return
 if nvcc_exe_ext == None and not os.path.isfile(f):
  " could it be in f+'.com'?"
  if nvcc_exe_ext==None:
   nvcc_exe_ext=detect_exe_ext( f+'*' )
   if nvcc_exe_ext != None:
    return
  nvcc_compile_exe_bug(c,err)
 nvcc_exe_ext=''
  
def nvcc_compile_exe_bug( c, err ):
 log('\n'+c+'\n------ nvcc linking failed with messages\n')
 log(err)
 log('------ end nvcc messages\n')

def detect_exe_ext( m ):
 l,m_len=os.listdir('.'),len(m)
 for i in l:
  if fnmatch.fnmatch( i, m ):
   if os.path.isfile(i):
    if len(i)<m_len:
     return ''
    return i[ i.rfind('.') ]

def detect_exe_ext_2arg( m, skip ):
 l,m_len=os.listdir('.'),len(m)
 for i in l:
  if fnmatch.fnmatch( i, m ):
   if os.path.isfile(i) and i != skip:
    if len(i)<m_len:
     return ''
    return i[ i.rfind('.') ]

def externC_hu( h ):
 ' parse file. Add extern "C". Return 0 if CUDA code found ' 
 r,e='',1
 with open(h,'rb') as i:
  for j in i.readlines():
   if j[:10]=='__global__':
    j = 'extern "C" '+j
    e=0
   r=r+j
 with open(h,'wb') as o:
  o.write(r)
 return e
 
def save_into_file(h,r):
 try:
  with open(h,'w') as o:
   o.write(r)
   return 1
 except:
  return 0
   
def what_else_needed(c, m):
 r=run_exe(['fgrep','-c','<math.h>',c])
 if r != '0':
  if 0:
   log( os.path.basename(c)+' wants libm?' )
  return dict( {'Libs':'-lm'} )

def gcc_switch( h ):
 try:
  r=h['Libs']
 except:
  return
 return r

def do_test(i_tail):
 #log( 'starts do_test, file='+i_tail+'\n' )
 global time_global
 i=polybench+i_tail
 if not os.path.isfile(i):
  print 'not file',i
  test_failed(i_tail,'','source file not found')
  return
 i_base=os.path.basename(i_tail).strip()
 i_base=i_base[:-2]
 for s in dataset_size:
  ff,time_current=[],dict()
  f,e,extra_magic=gcc_compile(i_base,i,s)
  ff += f
  if e:
   test_skipped(i_tail,s,'failed to compile with gcc')
   break
  for c in arch_list:
   f,e=nvcc_compile(i_base,i,s,c,extra_magic)
   ff += f
   if e:
    if e==1:
     test_failed(i_tail,s,'failed to create code with ppcg')
    else:
     test_failed(i_tail,s,'failed to compile code with nvcc')
    break
  if e:
   break
  #log( ' running cpu code, i='+i_base+' size='+s+'\n' )
  cpu_cerr,e,t_gcc=cpu_run(i_base,s)
  if cpu_cerr != None:
   ff.append(cpu_cerr)
  if e:
   test_skipped(i_tail,s,'failed to run CPU code')
   if delete_policy & 2:
    zapf( ff )
   break
  time_stat( time_current, 'cpu', s, t_gcc )
  e_sum=0
  for c in no_cap.items():
   #log( 'Will run code for size='+s+' card no='+str(c[0])+' arch='+c[1]+'\n' )
   #log( 'cpu result is in '+cpu_cerr+'\n' )
   f,e,t_cuda,m=nvcc_run(i_base,s,c[0],c[1],cpu_cerr)
   e_sum += e
   ff += f
   if e:
    if e==1:
     test_failed(i_tail,s,'problem running CUDA executable')
    else:
     test_failed(i_tail,s,'CPU-CUDA result mismatch')
   else:
    time_stat( time_current, str(c[0]), s, t_cuda )
    #log( str(time_current)+'\n\n' )
    test_passed(i_tail,s,time_current,m)
    time_update_global( time_global, time_current )
    time_current=dict()   # no double accounting
  if e_sum==0:
   if delete_policy & 1:
    zapf( ff )
  else:
   if delete_policy & 2:
    zapf( ff )

def cpu_run( i, s ):
 ' return file,error,time '
 n=i+'_cpu_'+s
 nO,f=n+'.rez',None
 c='./'+n+' 2> '+nO
 try:
  t=time.time()
  run_exe(c,shell=True)
  t=time.time()-t
  f,e=nO,0
 except:
  log( 'Failed to run cpu code '+n+', command:\n'+c )
  e,t=1,0
  if os.path.isfile(nO):
   f=nO
 return f,e,t

def nvcc_run(i,s,no,arch,cpu_rez):
 '''
  return file,e,time,mismatch_percent
  if strict_compare_result: set e=2 on result mismatch
   else leave e=0 and set p to non-zero instead
 '''
 n=i+'_'+arch+'__'+s
 gpu_rez,seg_fault=n+'.rez',n+'.segfault'
 if single_zero_card:
  par=''
 else:
  par=' %s' % no
 c='{ ./'+n+par+' ;} 2> '+gpu_rez+' 1>'+seg_fault
 f,p=[gpu_rez,seg_fault],None
 try:
  t=time.time()
  run_exe(c,shell=True)
  t=time.time()-t
  e=0
  # no need to check stdout here
 except:
  log( 'Failed to run cuda code '+n+', command:\n'+c+'\n' )
  for x in f:
   if os.path.getsize(x):
    segfault( x )
  e,t=1,-1
 f=list_files( f )
 if strict_compare_result:
  if e==0 and files_differ( gpu_rez, cpu_rez ):
   e=2
 else:
  if e==0:
   p=diff_statistic( gpu_rez, cpu_rez )
 return f,e,t,p

def segfault( s ):
 with open(s,'rb') as i:
  for j in i.readlines():
   log( j )

def list_files( xx ):
 r=[]
 for x in xx:
  if os.path.isfile(x):
   r.append( x )
 return r

def diff_statistic( x, y ):
 # returns fraction or integer saying how different files are, 1=max differ
 total=diffr=0
 with open(x,'rb') as a,open(y,'rb') as b:
  while 1:
   i,j=a.readline(),b.readline()
   eofA,eofB = i=='',j==''
   if eofA != eofB:
    log( 'file line count mismatch, '+x+' '+y+'\n' )
    return 1
   if eofA:
    return fractions.Fraction( numerator=diffr, denominator=total )
   alpha,betta=lines_differ_statistic( i, j )
   diffr += alpha
   total += betta

def files_differ( x, y ):
 if epsilon>0:
  # consider per-element difference
  with open(x,'rb') as a,open(y,'rb') as b:
   while 1:
    i,j=a.readline(),b.readline()
    eofA,eofB = i=='',j==''
    if eofA != eofB:
     log( 'file line count mismatch, '+x+' '+y+'\n' )
     return 1
    if eofA:
     return 0
    if lines_differ(i,j):
     log('file '+x+' '+y+' differ:\n')
     log(i+'\n'+j+'\n\n')
     return 1
 else:
  # files must be exactly equal
  return os.system('diff '+x+' '+y+' 1>/dev/null')

def lines_differ( x, y ):
 a,b=x.split(' '),y.split(' ')
 if len(a) != len(b):
  return 1
 for ij in zip(a,b):
  x,y=ij[0],ij[1]
  if x==y:
   continue
  x,y=float(x),float(y)
  z=x-y
  if z<-epsilon or z>epsilon:
   return 1
 return 0

def lines_differ_statistic( x, y ):
 total=diffr=0
 a,b=x.split(' '),y.split(' ')
 if len(a) != len(b):
  # should never happen, string format should be same
  return 1,1
 for ij in zip(a,b):
  u,v=ij[0],ij[1]
  if u==v and u=='':
   continue
  s=t=None
  try:
   s,t=float(u),float(v)
  except:
   pass
  total += 1
  if s != t and s==None or t==None:
   diffr += 1
   continue
  if s==None and t==None:
   # garbage, should never happen
   continue
  z=abs(s-t)
  if z>0.01:
   diffr += 1
 return diffr,total

def zapf( ff ):
 for f in ff:
  os.unlink(f)

def more_complaints(m):
 ' dump path to an executable, not more than once '
 global exe_shown
 for i in all_tools:
  if not exe_shown.has_key(i) and m.find(i) != -1:
   log( i+' used: '+globals()[i]+'\n' )
   exe_shown[i]=1
   break
  
def test_failed(i,s,m):
 more_complaints(m)
 if s == '':
  log( i+' failed: '+m+'\n' )
 else:
  log( i+' failed with datasize='+s+': '+m+'\n' )
 global stat_failed
 stat_failed += 1

def test_skipped(i,s,m):
 more_complaints(m)
 log( i+' skipped, datasize='+s+': '+m+'\n' )
 global stat_skipped
 stat_skipped += 1

def time_update_global( t, s ):
 for i in s.items():
  k,v=i
  try:
   t[k] += v
  except:
   t[k] = v

def test_passed(i,s,t,m):
 global stat_passed
 stat_passed += 1
 cpu_time,gpu_time=sum_time(t,'cpu'),dict()
 for c in no_cap.keys():
  k=str(c)
  gpu_time[k]=sum_time(t,k)
 j=i+' passed'
 if cpu_time != None:
  j += ', cpu time %0.2f' % cpu_time
 for c in gpu_time.keys():
  if gpu_time[c] != None:
   j += ', card %s time %0.2f' % (c, gpu_time[c])
 if m:
  j += ' mismatch: %s' % m
 log(j+'\n')
 with open(tgt_prefix+'full_time','ab') as o:
  for x in t.items()[::-1]:
   o.write( i+'|'+x[0]+'|'+('%0.4f\n' % x[1]) )

def sum_time( tt, d ):
 r=None
 for t in tt.items():
  this_d=t[0].split('|')[0]
  if d==this_d:
   try:
    r += t[1]
   except:
    r = t[1]
 return r

def time_stat( tt, d, s, m ):
 tt[d+'|'+s] = m

externC_hi='''
#if defined(__NVCC__)
 extern "C" 
 {
#endif
'''
externC_bye='''
#if defined(__NVCC__)
 }
#endif
'''

def crunch_polybench_h( tn, sn ):
 ' NVIDIA, thank you again for extern "C" problem '
 with open( tn, 'wb' ) as t:
  with open( sn, 'rb' ) as s:
   while 1:
    i=s.readline()
    if i=='':
     break
    if i.find( 'extern void* polybench_alloc_data' ) != -1:
     t.write( externC_hi )
     t.write( i )
     t.write( externC_bye )
    else:
     t.write( i )

stat_passed=stat_skipped=stat_failed=0
exe_shown,time_global=dict(),dict()
gcc_exe_ext=nvcc_exe_ext=None
polybench_c=' "'+polybench+'/utilities/polybench.c"'
try:
 os.makedirs(scratch)
except:
 pass
os.chdir(scratch)
loop_on_benchmark_list()
statistic()
if stat_passed==0:
 sys.exit(1)
