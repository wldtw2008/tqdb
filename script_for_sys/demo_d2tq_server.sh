#!/bin/bash
tcpserver -v -RHl0 127.0.0.1 4568 /bin/bash -c '(./make_demo_d2tq.sh DEMO1 &) && (./make_demo_d2tq.sh DEMO2 &) && (./make_demo_d2tq.sh DEMO3 &)'  
