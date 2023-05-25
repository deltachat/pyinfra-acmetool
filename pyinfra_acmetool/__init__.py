import importlib.resources

from pyinfra.operations import apt, files, systemd


def deploy_acmetool(nginx_hook=False):
    """Deploy acmetool."""
    apt.packages(
        name="Install acmetool",
        packages=["acmetool"],
    )

    files.put(
        src=importlib.resources.files(__package__).joinpath("acmetool.cron").open("rb"),
        dest="/etc/cron.d/acmetool",
        user="root",
        group="root",
        mode="644",
    )

    if nginx_hook:
        files.put(
            src=importlib.resources.files(__package__)
            .joinpath("acmetool.hook")
            .open("rb"),
            dest="/usr/lib/acme/hooks/nginx",
            user="root",
            group="root",
            mode="744",
        )

    service_file = files.put(
        src=importlib.resources.files(__package__)
        .joinpath("acmetool-redirector.service")
        .open("rb"),
        dest="/etc/systemd/system/acmetool-redirector.service",
        user="root",
        group="root",
        mode="644",
    )
    systemd.service(
        name="Setup acmetool-redirector service",
        service="acmetool-redirector.service",
        running=True,
        enabled=True,
        restarted=service_file.changed,
    )
