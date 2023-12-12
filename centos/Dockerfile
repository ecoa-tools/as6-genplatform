FROM centos:7
ARG builddir
ARG depsdir=$builddir/deps
ARG binPath=/usr/local/bin
ARG libPath=/lib
# Copy ECOA app binaries
COPY  $builddir/bin/* $binPath/
# Copy dependencies libraries
COPY $builddir/lib/libecoa.so $libPath/
COPY $depsdir/lib/libapr-1.so.0 $libPath/
COPY $depsdir/lib/liblog4cplus-2.0.so.3 $libPath/
RUN mkdir $binPath/logs
RUN chmod -R 777 $binPath/logs
RUN ldconfig
WORKDIR $binPath
CMD ["./platform"]
