FROM alpine as builder
MAINTAINER hidekuno@gmail.com

# setting 
ENV HOME /root
WORKDIR $HOME

RUN apk --update add python3 git sqlite|true
RUN git clone https://github.com/hidekuno/cidr-lite && python3 ${HOME}/cidr-lite/cidr_create_geoip.py >cidr.txt |true
RUN sqlite3 database.cidr '.read /root/cidr-lite/init.sql'

FROM alpine as cidr-lite
MAINTAINER hidekuno@gmail.com

RUN apk --update add python3
COPY --from=builder /root/database.cidr /root/
COPY --from=builder /root/cidr-lite/cidr_create.py /root/
COPY --from=builder /root/cidr-lite/cidr_search.py /root/
