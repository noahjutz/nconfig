#!/usr/bin/env python
import os
import click as cl
import prompter as pr

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

logfile_path = "nconfig.log"
env_user = os.environ["USER"]
env_home = os.environ["HOME"]


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
            cl.echo(pr.prompt_error(exit_code, 2, logfile_path))
            # Write to log
            os.system("echo -e {} >> {}".format(
                "'\n^^^ Error: Exit code {} '".format(str(exit_code)),
                logfile_path
            ))


def make_backup(directory):
    cl.echo(pr.prompt("Backing up...", 1, pr.Prompts.Info))
    execute(
        "dconf dump / > {}/gnome-settings &>> {}".format(directory, logfile_path),
        "tar czf {}/brave.tar.gz ~/.config/BraveSoftware &>> {}".format(directory, logfile_path)
    )


def restore_backup_fun(backup_path):
    cl.echo(pr.prompt("Restoring backup...", 1, pr.Prompts.Info))
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
        change_shell = cl.confirm(pr.prompt("Change shell?", 0, pr.Prompts.Question))

        # Dotfiles prompts
        restore_dotfiles = cl.confirm(pr.prompt("Restore dotfiles?", 0, pr.Prompts.Question))
        if restore_dotfiles:
            dotfiles_path = cl.prompt(pr.prompt("Dotfiles repo", 1, pr.Prompts.Question), type=str,
                                      default="https://github.com/noahjutz/dotfiles")

        # Backup prompts
        restore_backup = cl.confirm(pr.prompt("Restore backups?", 0, pr.Prompts.Question))
        if restore_backup:
            backup_path = cl.prompt(pr.prompt("Backup path", 1, pr.Prompts.Question),
                                    type=cl.Path(dir_okay=True, exists=True, readable=True),
                                    default="{}/backup".format(env_home))

        # Package prompts
        install_packages = cl.confirm(pr.prompt("Install packages?", 0, pr.Prompts.Question))
        if install_packages:
            package_manager = \
                cl.prompt(pr.prompt("Package manager", 1, pr.Prompts.Question),
                          type=cl.Choice(choices=packages.keys(), case_sensitive=False))
            package_manager = pacman if package_manager == "PACMAN" else deb

            # Prompt each package group
            groups = {}
            for group in package_manager:
                if group == "essential":
                    continue
                groups[group] = cl.confirm(pr.prompt("Install {} packages?", 2, pr.Prompts.Question, bold_text=group))
                if groups[group]:
                    for package in package_manager[group]:
                        if cl.confirm(pr.prompt("Install {}?", 3, pr.Prompts.Question, bold_text=package)):
                            packages_to_install.append(package)

        cl.echo()

        # User decides to do nothing
        if not restore_dotfiles and not restore_backup and not install_packages and not change_shell:
            cl.echo(pr.prompt("Nothing selected. Starting over.", 0, pr.Prompts.Info))
            cl.echo()
            continue

        # Confirmation screen
        cl.echo(pr.prompt("Confirm your input:", 0, pr.Prompts.Info))

        # Task list
        cl.echo(pr.prompt("Task list:", 1, pr.Prompts.Info))
        if change_shell:
            cl.echo(pr.prompt("Change shell", 2, pr.Prompts.Info))
        if restore_dotfiles:
            cl.echo(pr.prompt("Restore dotfiles", 2, pr.Prompts.Info))
            cl.echo(pr.prompt(dotfiles_path, 3, pr.Prompts.Info))

        if restore_backup:
            cl.echo(pr.prompt("Restore backup", 2, pr.Prompts.Info))
            cl.echo(pr.prompt(backup_path, 3, pr.Prompts.Info))

        if install_packages:
            cl.echo(pr.prompt("Install packages", 2, pr.Prompts.Info))
            for package in packages_to_install:
                cl.echo(pr.prompt(package, 3, pr.Prompts.Info))

        cl.echo()

        # Confirmation prompt
        if cl.confirm(pr.prompt("Start installation?", 0, pr.Prompts.Question)):
            cl.echo()
            break
        else:
            cl.echo()
            cl.echo(pr.prompt("Starting over.", 0, pr.Prompts.Info))
            cl.echo()

    """ install """
    cl.echo(pr.prompt("Starting installation.", 0, pr.Prompts.Info))

    # Restore dotfiles
    if restore_dotfiles:
        cl.echo(pr.prompt("Restoring dotfiles...", 1, pr.Prompts.Info))
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
            cl.echo(pr.prompt("Updating packages...", 1, pr.Prompts.Info))
            execute("sudo pacman -Syu --noconfirm &>> {}".format(logfile_path))

            # Install essential packages
            cl.echo(pr.prompt("Installing essential packages...", 1, pr.Prompts.Info))
            for package in pacman["essential"]:
                cl.echo(pr.prompt("Installing {}...", 2, pr.Prompts.Info, bold_text=package))
                execute("sudo pacman -S --noconfirm {} &>> {}".format(package, logfile_path))

            # Install packages
            cl.echo(pr.prompt("Installing packages...", 1, pr.Prompts.Info))
            for package in packages_to_install:
                cl.echo(pr.prompt("Installing {}...", 2, pr.Prompts.Info, bold_text=package))
                execute("yay -S --answerclean None --answerdiff None --ask no {} ".format(package))

        elif package_manager == deb:
            # Update
            cl.echo(pr.prompt("Updating packages...", 1, pr.Prompts.Info))
            execute(
                "sudo apt-get update &>> {}".format(logfile_path),
                "sudo apt-get upgrade &>> {}".format(logfile_path)
            )

            # Install packages
            cl.echo(pr.prompt("Installing packages...", 1, pr.Prompts.Info))
            for package in packages_to_install:
                cl.echo(pr.prompt("Installing {}...", 2, pr.Prompts.Info, bold_text=package))
                execute("sudo apt install -y {} &>> {}".format(package, logfile_path))

    # Change shell
    if change_shell:
        cl.echo(pr.prompt("Changing shell...", 1, pr.Prompts.Info))
        execute("sudo chsh -s /usr/bin/fish {} &>> {}".format(env_user, logfile_path))

    # Done
    cl.echo(pr.prompt("Installation complete.", 0, pr.Prompts.Info))
    cl.echo(pr.prompt("Please log out for changes to take effect", 0, pr.Prompts.Info))


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
