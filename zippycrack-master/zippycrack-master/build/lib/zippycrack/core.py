import zipfile

def crack(zipfilename, wordlist, verbose=False):
    with zipfile.ZipFile(zipfilename) as zf:
        with open(wordlist, 'r', encoding='utf-8') as f:
            for line in f:
                password = line.strip()
                try:
                    zf.extractall(pwd=password.encode('utf-8'))
                    if verbose:
                        print(f"[+] Password found: {password}")
                    return password
                except (RuntimeError, zipfile.BadZipFile, zipfile.LargeZipFile):
                    if verbose:
                        print(f"[-] Tried: {password}")
                    continue
    if verbose:
        print("[!] Password not found.")
    return None
