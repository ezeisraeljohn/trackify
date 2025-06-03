from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path


Base_DIR = Path(__file__).resolve().parent.parent
env = Environment(
    loader=FileSystemLoader(str(Base_DIR / "email_templates")),
    autoescape=select_autoescape(["html", "xml"]),
)


def render_email_template(template_name: str, context: dict) -> str:
    """
    Render an email template with the given context.

    :param template_name: Name of the template file (without extension).
    :param context: Context dictionary to render the template.
    :return: Rendered HTML string.
    """
    template = env.get_template(f"{template_name}.html")
    return template.render(context)
