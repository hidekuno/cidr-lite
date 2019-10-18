FROM ubuntu:18.04 as builder
MAINTAINER hidekuno@gmail.com

# setting 
ENV HOME /root
WORKDIR $HOME

RUN apt-get update && apt-get install -y python3 sqlite3 git|true
RUN git clone https://github.com/hidekuno/cidr-lite && python3 ${HOME}/cidr-lite/cidr_create.py >cidr.txt |true
RUN sqlite3 database.cidr '.read /root/cidr-lite/init.sql'

FROM ubuntu:18.04 as cidr-lite
MAINTAINER hidekuno@gmail.com

RUN apt-get update && apt-get -y install python3 sqlite3
COPY --from=builder /root/database.cidr /root/
COPY --from=builder /root/cidr-lite/cidr_create.py /root/
COPY --from=builder /root/cidr-lite/cidr_search.py /root/
