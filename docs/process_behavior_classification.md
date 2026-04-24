This document describes the endpoint process behavior classification.

We'll use a supervised classifier on process features to flag malicious vs benign processes.
The 2 main questions we have to answer are:

1. What will be the supervised classifier we choose?
2. What will be the process features?

We choose simple answers, so we can see a prototype working:
1. Isolation forest

2. Each process will have the following features:
CPU_pct_{10s,60s,1h} — mean CPU percent
Mem_mb_{10s,60s,1h} — mean memory MB
IO_read_bytes_{10s,60s,1h} — sum read bytes
IO_write_bytes_{10s,60s,1h} — sum write bytes
Net_out_bytes_{10s,60s,1h} — sum outbound bytes
Net_in_bytes_{10s,60s,1h} — sum inbound bytes
Proc_start_count_{60s,1h} — count of process starts for same binary
Child_count_{60s,1h} — number of child processes spawned
Cmdline_hash_hits_{60s,1h} — top-N cmdline token hash counts
Parent_binary_hash — hashed parent binary (categorical numeric)
Privilege_flag — 0/1 (e.g., elevated/admin)
File_write_count_{60s,1h} — count of distinct files written
Socket_open_count_{60s,1h} — count of open sockets
CPU_slope_{60s} — linear slope of CPU_pct over last 60s
Mem_delta_from_baseline_{1h} — difference vs host 24h baseline
Rare_binary_score — frequency-based rarity (per-host)
Anomaly_score_prev — previous model score (for temporal smoothing)

Important notes:
Normalize per-host, fill missing with zeros or median, and compute rolling aggregates in real time._


