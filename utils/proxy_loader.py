import json

def convert_txt_to_json(txt_path="utils/raw_proxies.txt", json_path="utils/proxies.json"):
    with open(txt_path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]
    proxies = ["http://" + line if not line.startswith("http") else line for line in lines]

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({"proxies": proxies}, f, indent=4)

    print(f"[Loader] {len(proxies)} proxies cargados en '{json_path}'")

if __name__ == "__main__":
    convert_txt_to_json()
