def test_all_admin_templates_compile(app):
    """Catch malformed Jinja syntax before an admin page fails at request time."""
    template_names = app.jinja_env.list_templates()
    assert template_names
    for template_name in template_names:
        app.jinja_env.get_template(template_name)


def test_direction_editor_template_compiles(app):
    template = app.jinja_env.get_template("admin/direction_editor.html")
    assert template.name == "admin/direction_editor.html"
