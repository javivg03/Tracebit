import instaloader

def scrape_profile(username):
    L = instaloader.Instaloader()
    profile = instaloader.Profile.from_username(L.context, username)

    return {
        "username": profile.username,
        "nombre_completo": profile.full_name,
        "biografia": profile.biography,
        "enlace_bio": profile.external_url,
        "seguidores": profile.followers,
        "seguidos": profile.followees,
        "publicaciones": profile.mediacount,
        "verificado": profile.is_verified,
        "privado": profile.is_private,
    }
