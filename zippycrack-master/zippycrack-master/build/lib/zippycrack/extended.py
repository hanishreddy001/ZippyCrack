import zipfile

def crack_with_generator(zipfilename, password_generator, verbose=False):
    with zipfile.ZipFile(zipfilename) as zf:
        for password in password_generator:
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
