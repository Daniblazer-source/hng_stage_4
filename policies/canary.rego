package swiftdeploy.canary

default allow := false

allow if {
    count(violation) == 0
}

violation contains "High Error Rate" if {
    input.error_rate > 0.01
}

violation contains "High Latency" if {
    input.p99_latency > 0.5
}
