from flask import Flask, render_template, request
import time, zipfile, io
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)

def analyze_password(password):
    length = len(password)
    entropy = round(length * 4.7, 2)
    suggestions = []
    if length < 8:
        suggestions.append("Use at least 8 characters.")
    if password.islower() or password.isupper():
        suggestions.append("Mix uppercase and lowercase letters.")
    if password.isalnum():
        suggestions.append("Include symbols for more strength.")
    if not suggestions:
        suggestions.append("Good password strength.")
    if length < 5:
        strength = "Very Weak"
    elif length < 8:
        strength = "Weak"
    elif length < 12:
        strength = "Medium"
    else:
        strength = "Strong"
    return strength, entropy, suggestions

def try_password(zf_bytes, pwd):
    try:
        with zipfile.ZipFile(zf_bytes) as zf:
            zf.extractall(pwd=bytes(pwd, "utf-8"))
        return pwd
    except:
        return None

def crack_zip_multithread(zip_bytes, wordlist_path, threads=4):
    with open(wordlist_path, "r", encoding="utf-8") as wl:
        passwords = [p.strip() for p in wl]

    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = {executor.submit(try_password, io.BytesIO(zip_bytes.getvalue()), pwd): pwd for pwd in passwords}
        for future in futures:
            result = future.result()
            if result:
                executor.shutdown(cancel_futures=True)
                return result
    return None

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if "zipfile" not in request.files:
            return render_template("index.html", error="No file uploaded")
        
        file = request.files["zipfile"]
        if file.filename == "":
            return render_template("index.html", error="No file selected")
        
        start_time = time.time()
        zip_bytes = io.BytesIO(file.read())
        
        password = crack_zip_multithread(zip_bytes, "wordlist.txt", threads=8)
        time_taken = round(time.time() - start_time, 2)

        if password:
            strength, entropy, suggestions = analyze_password(password)
            try:
                with zipfile.ZipFile(zip_bytes) as zf:
                    contents = zf.namelist()
            except:
                contents = ["Unable to read ZIP contents"]
            return render_template(
                "index.html",
                password=password,
                strength=strength,
                entropy=entropy,
                suggestions=suggestions,
                contents=contents,
                time_taken=time_taken
            )
        else:
            return render_template("index.html", error="Password not found in wordlist.")
    
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
