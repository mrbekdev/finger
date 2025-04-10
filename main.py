from Scanner import Scanner

def main():
    scanner = Scanner()
    if scanner.connect_to_device():
        scanner.capture()

    scanner.CloseDevice()

if __name__ == "__main__":
    main()