import enum
import click as cl


class Prompts(enum.Enum):
    Question = 0,
    Info = 1,
    Alert = 2


def prompt(text, indent, prompt_type, bold_text=""):
    prefix = ""
    color = ""
    if prompt_type == Prompts.Question:
        prefix = "?"
        color = "magenta"
    elif prompt_type == Prompts.Info:
        prefix = ">"
        color = "blue"
    elif prompt_type == Prompts.Alert:
        prefix = "!"
        color = "red"
    return cl.style(indent * "  " + prefix + " ", bold=True, fg=color) + text.format(
        cl.style(bold_text, bold=True, fg=color))


def prompt_error(code, indent, logfile_path):
    templ = "Error code {}. See {} for details.".format("{}", logfile_path)
    return prompt(templ, indent, Prompts.Alert, str(code))
