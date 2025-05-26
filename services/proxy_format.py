def formatear_proxy_requests(proxy_dict):
    """
    Devuelve el proxy en formato usable por `requests`:
    {
        "http": "http://usuario:contraseña@ip:puerto",
        "https": "http://usuario:contraseña@ip:puerto"
    }
    """
    proxy_url = f"http://{proxy_dict['username']}:{proxy_dict['password']}@{proxy_dict['ip']}:{proxy_dict['port']}"
    return {
        "http": proxy_url,
        "https": proxy_url
    }

def formatear_proxy_playwright(proxy_dict):
    """
    Devuelve el proxy en formato usable por Playwright:
    {
        "server": "http://ip:port",
        "username": "usuario",
        "password": "contraseña"
    }
    """
    return {
        "server": f"http://{proxy_dict['ip']}:{proxy_dict['port']}",
        "username": proxy_dict["username"],
        "password": proxy_dict["password"]
    }
