def test_all_admin_templates_compile(app):
    """Catch malformed Jinja syntax before an admin page fails at request time."""
    template_names = app.jinja_env.list_templates()
    assert template_names
    for template_name in template_names:
        app.jinja_env.get_template(template_name)


def test_direction_editor_template_compiles(app):
    template = app.jinja_env.get_template("admin/direction_editor.html")
    assert template.name == "admin/direction_editor.html"


def test_csp_allows_leaflet_draw_sprite_images(app):
    response = app.test_client().get("/privacy")
    policy = response.headers.get("Content-Security-Policy", "")
    img_src = next((directive for directive in policy.split(";") if directive.strip().startswith("img-src ")), "")
    assert "https://cdnjs.cloudflare.com" in img_src


def test_csp_allows_nominatim_landmark_search(app):
    response = app.test_client().get("/privacy")
    policy = response.headers.get("Content-Security-Policy", "")
    connect_src = next((directive for directive in policy.split(";") if directive.strip().startswith("connect-src ")), "")
    assert "https://nominatim.openstreetmap.org" in connect_src
