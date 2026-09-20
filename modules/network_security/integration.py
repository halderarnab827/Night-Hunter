# NIGHT HUNTER - Network Security Integration

import sys
from pathlib import Path


# ---------------------------------------------------------
# PROJECT ROOT
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ---------------------------------------------------------
# IMPORT NETWORK MODULES
# ---------------------------------------------------------

from modules.network_security import checker
from modules.network_security import pentest
from modules.network_security import stress_test


# ---------------------------------------------------------
# DISPLAY HELPERS
# ---------------------------------------------------------

def show_banner():
    print()
    print("=" * 64)
    print("NIGHT HUNTER - NETWORK SECURITY")
    print("=" * 64)


def show_menu():
    print()
    print("-" * 64)
    print("[1] Network Security Check")
    print("[2] Network Pentest")
    print("[3] Controlled HTTP Stress Test")
    print("[4] Network Information")
    print("[0] Back / Exit")
    print("-" * 64)


# ---------------------------------------------------------
# NETWORK SECURITY CHECK
# ---------------------------------------------------------

def run_security_check():
    print()
    print("=" * 64)
    print("NETWORK SECURITY CHECK")
    print("=" * 64)

    host = input("Enter host or IP: ").strip()

    if not host:
        print("[!] Host cannot be empty.")
        return

    try:
        result = checker.run_network_check(host)

        if result is None:
            print()
            print("[!] Network check returned no result.")
            return

        print()
        print("=" * 64)
        print("NETWORK CHECK COMPLETED")
        print("=" * 64)

        if isinstance(result, dict):

            for key, value in result.items():

                if isinstance(value, list):
                    print()
                    print(f"{key}:")
                    for item in value:
                        print(f"  {item}")

                elif isinstance(value, dict):
                    print()
                    print(f"{key}:")
                    for sub_key, sub_value in value.items():
                        print(f"  {sub_key}: {sub_value}")

                else:
                    print(f"{key}: {value}")

        else:
            print(result)

    except Exception as error:
        print()
        print(f"[!] Network security check failed: {error}")


# ---------------------------------------------------------
# NETWORK PENTEST
# ---------------------------------------------------------

def run_pentest():
    print()
    print("=" * 64)
    print("NETWORK PENTEST")
    print("=" * 64)

    host = input("Enter authorized target host/IP: ").strip()

    if not host:
        print("[!] Host cannot be empty.")
        return

    print()
    print("[*] Starting network pentest...")
    print("[*] Use only on systems you own or are authorized to test.")
    print()

    try:

        if hasattr(pentest, "run_network_pentest"):

            result = pentest.run_network_pentest(host)

        elif hasattr(pentest, "network_pentest"):

            result = pentest.network_pentest(host)

        elif hasattr(pentest, "run_pentest"):

            result = pentest.run_pentest(host)

        else:

            print("[!] Could not find the pentest entry function.")
            print("[!] Check modules/network_security/pentest.py")
            return

        print()
        print("=" * 64)
        print("NETWORK PENTEST COMPLETED")
        print("=" * 64)

        if isinstance(result, dict):

            for key, value in result.items():

                if isinstance(value, list):
                    print()
                    print(f"{key}:")
                    for item in value:
                        print(f"  {item}")

                elif isinstance(value, dict):
                    print()
                    print(f"{key}:")
                    for sub_key, sub_value in value.items():
                        print(f"  {sub_key}: {sub_value}")

                else:
                    print(f"{key}: {value}")

        else:
            print(result)

    except Exception as error:
        print()
        print(f"[!] Network pentest failed: {error}")


# ---------------------------------------------------------
# NETWORK INFORMATION
# ---------------------------------------------------------

def show_network_information():

    print()
    print("=" * 64)
    print("NETWORK INFORMATION")
    print("=" * 64)

    try:

        if hasattr(checker, "get_network_info"):

            information = checker.get_network_info()

        else:

            print("[!] Network information function not found.")
            return

        if not information:
            print("[!] No network information returned.")
            return

        for key, value in information.items():
            print(f"{key}: {value}")

    except Exception as error:
        print()
        print(f"[!] Unable to collect network information: {error}")


# ---------------------------------------------------------
# CONTROLLED STRESS TEST
# ---------------------------------------------------------

def run_stress_test():

    print()
    print("=" * 64)
    print("CONTROLLED HTTP STRESS TEST")
    print("=" * 64)

    print()
    print("[!] Authorized testing only.")
    print("[!] This module is intended for controlled load testing.")
    print()

    target = input("Enter authorized HTTP/HTTPS URL: ").strip()

    if not target:
        print("[!] URL cannot be empty.")
        return

    try:
        workers_input = input(
            "Workers [default 5]: "
        ).strip()

        duration_input = input(
            "Duration in seconds [default 10]: "
        ).strip()

        workers = int(workers_input) if workers_input else 5
        duration = int(duration_input) if duration_input else 10

        if workers < 1:
            print("[!] Workers must be at least 1.")
            return

        if duration < 1:
            print("[!] Duration must be at least 1 second.")
            return

        if workers > 20:
            print("[!] Workers cannot exceed 20.")
            return

        if duration > 300:
            print("[!] Duration cannot exceed 300 seconds.")
            return

        print()
        print("[*] Starting controlled stress test...")
        print()

        # Try common function names used by the stress module.
        if hasattr(stress_test, "run_stress_test"):

            result = stress_test.run_stress_test(
                target,
                duration=duration,
                workers=workers
            )

        elif hasattr(stress_test, "stress_test"):

            result = stress_test.stress_test(
                target,
                duration=duration,
                workers=workers
            )

        else:

            print("[!] Could not find stress-test entry function.")
            print("[!] Check modules/network_security/stress_test.py")
            return

        print()
        print("=" * 64)
        print("STRESS TEST COMPLETED")
        print("=" * 64)

        if result is not None:
            print(result)

    except ValueError:
        print("[!] Workers and duration must be numbers.")

    except Exception as error:
        print()
        print(f"[!] Stress test failed: {error}")


# ---------------------------------------------------------
# MAIN INTEGRATION MENU
# ---------------------------------------------------------

def main():

    while True:

        show_banner()
        show_menu()

        choice = input("Enter choice: ").strip()

        if choice == "1":

            run_security_check()

        elif choice == "2":

            run_pentest()

        elif choice == "3":

            run_stress_test()

        elif choice == "4":

            show_network_information()

        elif choice == "0":

            print()
            print("Returning from Network Security module...")
            break

        else:

            print()
            print("[!] Invalid choice.")

        input("\nPress Enter to continue...")


# ---------------------------------------------------------
# DIRECT EXECUTION
# ---------------------------------------------------------

if __name__ == "__main__":
    main()
    