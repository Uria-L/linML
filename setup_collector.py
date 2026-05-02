'''
setup_collector.py
example usage:
sudo python3 setup.py --venv-path /venv/path --module-path src.collector.learn_host
'''
#!/usr/bin/env python3

import os
import sys
import subprocess
import argparse
from pathlib import Path


def run(cmd, check=True):
    """Run command, return success."""
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if check and result.returncode != 0:
        print(f"Error: {result.stderr}")
        return False
    return True


def setup(project_root, venv_path, module_path, user="root"):
    """Setup telemetry systemd service."""

    if os.geteuid() != 0:
        print("Error: must run as root (use sudo)")
        return False

    project_root = Path(project_root).resolve()
    venv_path = Path(venv_path).resolve()
    log_dir = Path("/var/log/telemetry")
    python_exe = venv_path / "bin" / "python3"
    service_file = Path("/etc/systemd/system/linML-collector.service")


    # Verify prerequisites
    if not python_exe.exists():
        print(f"Error: python not found at {python_exe}")
        return False

    if service_file.exists():
        print(f"Service already exists at {service_file}")
        response = input("Reconfigure? (y/n): ").strip().lower()
        if response != "y":
            print("Skipping setup")
            return True
        print("Reconfiguring...")


    # Create service file
    service_content = f"""[Unit]
Description=linML Collector Service
After=network.target

[Service]
Type=simple
User={user}
WorkingDirectory={project_root}
Environment=APP_MODE=production
Environment=PYTHONPATH={project_root}
ExecStart=/usr/bin/python3 -m {module_path}
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
"""


    service_file.write_text(service_content)
    print(f"✓ Created {service_file}")

    # Create logrotate config
    logrotate_content = f"""{log_dir}/metrics.csv {{
    daily
    rotate 7
    compress
    delaycompress
    notifempty
    create 0644 {user} {user}
}}
"""

    logrotate_file = Path("/etc/logrotate.d/linML-collector")
    logrotate_file.write_text(logrotate_content)
    print(f"✓ Created {logrotate_file}")

    # Create log directory
    log_dir.mkdir(parents=True, exist_ok=True)
    run(["chown", f"{user}:{user}", str(log_dir)])
    print(f"✓ Created {log_dir}")

    # Enable and start
    run(["systemctl", "daemon-reload"])
    run(["systemctl", "enable", "linML-collector.service"])
    run(["systemctl", "start", "linML-collector.service"])
    print("✓ Service enabled and started")

    # Verify
    result = subprocess.run(
        ["systemctl", "is-active", "linML-collector.service"],
        capture_output=True,
        check=False
    )

    if result.returncode == 0:
        print("✓ Service is running")
        return True

    print("✗ Service failed to start")
    subprocess.run(["journalctl", "-u", "linML-collector.service", "-n", "20"], check=False)
    return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Setup telemetry systemd service")
    parser.add_argument("--project-root", default=".", help="Project root")
    parser.add_argument("--venv-path", required=True, help="Venv path")
    parser.add_argument("--module-path", required=True, help="Module path")
    parser.add_argument("--user", default="root", help="Service user")

    args = parser.parse_args()

    SUCCESS = setup(args.project_root, args.venv_path, args.module_path, args.user)
    sys.exit(0 if SUCCESS else 1)
