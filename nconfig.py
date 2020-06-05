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
    # TODO
}

packages = {
    "PACMAN": pacman,
    "DEB": deb
}

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


@cl.group()
def cli():
    """CLI for configuring linux."""
    # Clear logfile
    f = open(logfile_path, "w")
    f.write("")


@cli.command()
def auto_install():
    """Configure everything according to passed options"""

    global package_manager
    """ prompts """
    while True:
        packages_to_install = list()
        # Initial prompts
        restore_dotfiles = cl.confirm(prompt("Restore dotfiles?", 0, Prompts.Question))

        # Dotfiles prompts
        if restore_dotfiles:
            dotfiles_path = cl.prompt(prompt("Dotfiles repo", 1, Prompts.Question), type=str,
                                      default="https://github.com/noahjutz/dotfiles")

        restore_backup = cl.confirm(prompt("Restore backups?", 0, Prompts.Question))

        # Backup prompts
        if restore_backup:
            backup_path = cl.prompt(prompt("Backup path", 1, Prompts.Question),
                                    type=cl.Path(dir_okay=True, exists=True, readable=True),
                                    default="{}/backup".format(env_home))

        install_packages = cl.confirm(prompt("Install packages?", 0, Prompts.Question))

        # Package specific prompts
        if install_packages:
            package_manager = \
                cl.prompt(prompt("Package manager", 1, Prompts.Question),
                          type=cl.Choice(choices=packages.keys(), case_sensitive=False))
            package_manager = pacman if package_manager == "PACMAN" else deb

            # Prompt each package group
            groups = {}
            for group in package_manager:
                groups[group] = cl.confirm(prompt("Install {} packages?", 2, Prompts.Question, bold_text=group))
                if groups[group]:
                    for package in package_manager[group]:
                        if cl.confirm(prompt("Install {}?", 3, Prompts.Question, bold_text=package)):
                            packages_to_install.append(package)

        cl.echo()
        # User decides to do nothing
        if not restore_dotfiles and not restore_backup and not install_packages:
            cl.echo(prompt("Nothing selected. Starting over.", 0, Prompts.Info))
            cl.echo()
            continue

        # Confirmation screen
        cl.echo(prompt("Confirm your input:", 0, Prompts.Info))

        # Task list
        cl.echo(prompt("Task list:", 1, Prompts.Info))
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
        os.system("git clone --bare {} $HOME/.cfg &>> {}\n".format(dotfiles_path, logfile_path) +
                  "git --git-dir=$HOME/.cfg/ --work-tree=$HOME checkout -f\n" +
                  "git --git-dir=$HOME/.cfg/ --work-tree=$HOME config --local status.showUntrackedFiles no\n" +
                  "echo \".cfg\" >> .gitignore &>> {}".format(logfile_path))

    # Restore backup
    if restore_backup:
        cl.echo(prompt("Restoring backup...", 1, Prompts.Info))
        os.system("dconf load / &>> {} < {}/gnome-settings\n".format(logfile_path, backup_path) +
                  "tar xf {}/brave.tar.gz -C $HOME/.config/ &>> {}".format(backup_path, logfile_path))

    # Install packages
    if install_packages:
        if package_manager == pacman:
            # Update
            cl.echo(prompt("Updating packages...", 1, Prompts.Info))
            os.system("yay -Syu --answerclean None --answerdiff None --ask no &>> {}".format(logfile_path))
            # Install packages
            cl.echo(prompt("Installing packages...", 1, Prompts.Info))
            for package in packages_to_install:
                cl.echo(prompt("Installing {}...", 2, Prompts.Info, bold_text=package))
                os.system(
                    "yay -S --answerclean None --answerdiff None --ask no {} &>> {}".format(package, logfile_path))
        elif package_manager == deb:
            # Update
            cl.echo(prompt("Updating packages...", 1, Prompts.Info))
            # Install packages
            cl.echo(prompt("Installing packages...", 1, Prompts.Info))

    # Done
    cl.echo(prompt("Installation complete.", 0, Prompts.Info))


@cli.command()
def backup():
    """Back up app settings and push to a server"""
    cl.echo("Backup")


@cli.command()
def restore():
    """Restore app settings"""
    cl.echo("Restore")


if __name__ == '__main__':
    cli()
