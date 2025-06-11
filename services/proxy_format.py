def formatear_proxy_requests(proxy_dict):
    """
    Devuelve el proxy en formato usable por `requests`, con o sin autenticación.
    """
    if proxy_dict.get("username") and proxy_dict.get("password"):
        proxy_url = f"http://{proxy_dict['username']}:{proxy_dict['password']}@{proxy_dict['ip']}:{proxy_dict['port']}"
    else:
        proxy_url = f"http://{proxy_dict['ip']}:{proxy_dict['port']}"
    return {
        "http": proxy_url,
        "https": proxy_url
    }

def formatear_proxy_playwright(proxy_dict):
    """
    Devuelve el proxy en formato usable por Playwright.
    Si no hay autenticación, no incluye username/password.
    """
    proxy_config = {
        "server": f"http://{proxy_dict['ip']}:{proxy_dict['port']}"
    }
    if proxy_dict.get("username") and proxy_dict.get("password"):
        proxy_config["username"] = proxy_dict["username"]
        proxy_config["password"] = proxy_dict["password"]
    return proxy_config
