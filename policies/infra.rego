package swiftdeploy.infra

default allow := false

# The main decision logic
allow if {
    count(violation) == 0
}

# Rule 1: Check Disk Space (Must be > 10GB)
violation contains "Low Disk Space" if {
    input.disk_free_gb < 10
}

# Rule 2: Check CPU Load (Must be < 2.0)
violation contains "High CPU Load" if {
    input.cpu_load > 2.0
}

# Rule 3: Check Memory
violation contains "Low Memory" if {
    input.mem_free_mb < 500
}
