#!/usr/bin/env python
import os
import enum
import click as cl

pacman = {
    "essential": (
        "yay",
        "binutils",
        "make",
        "gcc",
        "pkg-config",
        "fakeroot",

        "python",
        "python-pip"
    ),
    "cli": (
        "fish",
        "htop",
        "gvim",
        "ranger"
    ),
    "social": (
        "discord",
        "telegram-desktop"
    ),
    "ide": (
        "android-studio",
        "pycharm-community-edition",
        "intellij-idea-community-edition",
        "code"
    ),
    "tools": (
        "bitwarden",
        "torbrowser-launcher",
        "brave",
        "etcher",
        "virtualbox"
    )
}

deb = {
    "cli": (
        "fish",
        "htop",
        "vim"
    )
}

packages = {
    "PACMAN": pacman,
    "DEB": deb
}

exit_codes = list()
logfile_path = "nconfig.log"
env_user = os.environ["USER"]
env_home = os.environ["HOME"]


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


def prompt_error(code, indent):
    templ = "Error code {}. See {} for details.".format("{}", logfile_path)
    return prompt(templ, indent, Prompts.Alert, str(code))


def execute(*code):
    for c in code:
        # Write to log file
        os.system("echo -e {} >> {}".format(
            "'\n>>> Executing: {}\n'".format(c),
            logfile_path
        ))
        # Execute code
        exit_code = os.system(c)

        # Show error message
        if exit_code != 0:
            cl.echo(prompt_error(exit_code, 2))
            # Write to log
            os.system("echo -e {} >> {}".format(
                "'\n^^^ Error: Exit code {} '".format(str(exit_code)),
                logfile_path
            ))


def make_backup(directory):
    cl.echo(prompt("Backing up...", 1, Prompts.Info))
    execute(
        "dconf dump / > {}/gnome-settings &>> {}".format(directory, logfile_path),
        "tar czf {}/brave.tar.gz ~/.config/BraveSoftware &>> {}".format(directory, logfile_path)
    )


def restore_backup_fun(backup_path):
    cl.echo(prompt("Restoring backup...", 1, Prompts.Info))
    execute(
        "dconf load / &>> {} < {}/gnome-settings".format(logfile_path, backup_path),
        "tar xf {}/brave.tar.gz -C $HOME/.config/ &>> {}".format(backup_path, logfile_path)
    )


@cl.group()
def cli():
    """CLI for configuring linux."""
    # Clear logfile
    f = open(logfile_path, "w")
    f.write("")
    f.close()


@cli.command()
def auto_install():
    """Configure everything according to passed options"""

    global package_manager
    """ prompts """
    while True:
        packages_to_install = list()
        # Initial prompts
        # Change shell
        change_shell = cl.confirm(prompt("Change shell?", 0, Prompts.Question))

        # Dotfiles prompts
        restore_dotfiles = cl.confirm(prompt("Restore dotfiles?", 0, Prompts.Question))
        if restore_dotfiles:
            dotfiles_path = cl.prompt(prompt("Dotfiles repo", 1, Prompts.Question), type=str,
                                      default="https://github.com/noahjutz/dotfiles")

        # Backup prompts
        restore_backup = cl.confirm(prompt("Restore backups?", 0, Prompts.Question))
        if restore_backup:
            backup_path = cl.prompt(prompt("Backup path", 1, Prompts.Question),
                                    type=cl.Path(dir_okay=True, exists=True, readable=True),
                                    default="{}/backup".format(env_home))

        # Package prompts
        install_packages = cl.confirm(prompt("Install packages?", 0, Prompts.Question))
        if install_packages:
            package_manager = \
                cl.prompt(prompt("Package manager", 1, Prompts.Question),
                          type=cl.Choice(choices=packages.keys(), case_sensitive=False))
            package_manager = pacman if package_manager == "PACMAN" else deb

            # Prompt each package group
            groups = {}
            for group in package_manager:
                if group == "essential":
                    continue
                groups[group] = cl.confirm(prompt("Install {} packages?", 2, Prompts.Question, bold_text=group))
                if groups[group]:
                    for package in package_manager[group]:
                        if cl.confirm(prompt("Install {}?", 3, Prompts.Question, bold_text=package)):
                            packages_to_install.append(package)

        cl.echo()

        # User decides to do nothing
        if not restore_dotfiles and not restore_backup and not install_packages and not change_shell:
            cl.echo(prompt("Nothing selected. Starting over.", 0, Prompts.Info))
            cl.echo()
            continue

        # Confirmation screen
        cl.echo(prompt("Confirm your input:", 0, Prompts.Info))

        # Task list
        cl.echo(prompt("Task list:", 1, Prompts.Info))
        if change_shell:
            cl.echo(prompt("Change shell", 2, Prompts.Info))
        if restore_dotfiles:
            cl.echo(prompt("Restore dotfiles", 2, Prompts.Info))
            cl.echo(prompt(dotfiles_path, 3, Prompts.Info))

        if restore_backup:
            cl.echo(prompt("Restore backup", 2, Prompts.Info))
            cl.echo(prompt(backup_path, 3, Prompts.Info))

        if install_packages:
            cl.echo(prompt("Install packages", 2, Prompts.Info))
            for package in packages_to_install:
                cl.echo(prompt(package, 3, Prompts.Info))

        cl.echo()

        # Confirmation prompt
        if cl.confirm(prompt("Start installation?", 0, Prompts.Question)):
            cl.echo()
            break
        else:
            cl.echo()
            cl.echo(prompt("Starting over.", 0, Prompts.Info))
            cl.echo()

    """ install """
    cl.echo(prompt("Starting installation.", 0, Prompts.Info))

    # Restore dotfiles
    if restore_dotfiles:
        cl.echo(prompt("Restoring dotfiles...", 1, Prompts.Info))
        execute(
            "git clone --bare {} $HOME/.cfg &>> {}".format(dotfiles_path, logfile_path),
            "git --git-dir=$HOME/.cfg/ --work-tree=$HOME checkout -f &>> {}".format(logfile_path),
            "echo \".cfg\" >> .gitignore &>> {}".format(logfile_path)
        )

    # Restore backup
    if restore_backup:
        restore_backup_fun(backup_path)

    # Install packages
    if install_packages:
        if package_manager == pacman:
            # Update
            cl.echo(prompt("Updating packages...", 1, Prompts.Info))
            execute("sudo pacman -Syu --noconfirm &>> {}".format(logfile_path))

            # Install essential packages
            cl.echo(prompt("Installing essential packages...", 1, Prompts.Info))
            for package in pacman["essential"]:
                cl.echo(prompt("Installing {}...", 2, Prompts.Info, bold_text=package))
                execute("sudo pacman -S --noconfirm {} &>> {}".format(package, logfile_path))

            # Install packages
            cl.echo(prompt("Installing packages...", 1, Prompts.Info))
            for package in packages_to_install:
                cl.echo(prompt("Installing {}...", 2, Prompts.Info, bold_text=package))
                execute("yay -S --answerclean None --answerdiff None --ask no {} ".format(package))

        elif package_manager == deb:
            # Update
            cl.echo(prompt("Updating packages...", 1, Prompts.Info))
            execute(
                "sudo apt-get update &>> {}".format(logfile_path),
                "sudo apt-get upgrade &>> {}".format(logfile_path)
            )

            # Install packages
            cl.echo(prompt("Installing packages...", 1, Prompts.Info))
            for package in packages_to_install:
                cl.echo(prompt("Installing {}...", 2, Prompts.Info, bold_text=package))
                execute("sudo apt install -y {} &>> {}".format(package, logfile_path))

    # Change shell
    if change_shell:
        cl.echo(prompt("Changing shell...", 1, Prompts.Info))
        execute("sudo chsh -s /usr/bin/fish {} &>> {}".format(env_user, logfile_path))

    # Done
    cl.echo(prompt("Installation complete.", 0, Prompts.Info))
    cl.echo(prompt("Please log out for changes to take effect", 0, Prompts.Info))


@cli.command()
@cl.option('--directory', default="{}/backup".format(env_home), help='Directory containing backup files',
           type=cl.Path(exists=True, dir_okay=True, readable=True))
def backup(directory):
    """Back up app settings into a directory"""
    make_backup(directory)


@cli.command()
@cl.option('--directory', default="{}/backup".format(env_home), help='Directory containing backup files',
           type=cl.Path(exists=True, dir_okay=True, readable=True))
def restore(directory):
    """Restore app settings"""
    restore_backup_fun(directory)


if __name__ == '__main__':
    cli()
