from monitor import SystemMonitor

# ==========================================
# RP2040 Resource Monitor
# ==========================================

def main():

    monitor = SystemMonitor()

    monitor.run()


# ==========================================
# Entry Point
# ==========================================

if __name__ == "__main__":

    main()