import importlib.resources

from pyinfra import host
from pyinfra.facts.files import FindFiles
from pyinfra.operations import apt, files, systemd, server


def deploy_acmetool(
    reload_hook="", email="", domains=[], request_later=False, **pyinfra_args
):
    """Deploy acmetool."""
    apt.packages(
        name="Install acmetool",
        packages=["acmetool"],
        **pyinfra_args,
    )

    files.template(
        src=importlib.resources.files(__package__) / "acmetool.cron.j2",
        dest="/etc/cron.d/acmetool",
        user="root",
        group="root",
        mode="644",
        reload_hook=reload_hook,
        **pyinfra_args,
    )

    files.template(
        src=importlib.resources.files(__package__).joinpath("response-file.yaml.j2"),
        dest="/var/lib/acme/conf/responses",
        user="root",
        group="root",
        mode="644",
        email=email,
        **pyinfra_args,
    )

    service_file = files.put(
        src=importlib.resources.files(__package__)
        .joinpath("acmetool-redirector.service")
        .open("rb"),
        dest="/etc/systemd/system/acmetool-redirector.service",
        user="root",
        group="root",
        mode="644",
        **pyinfra_args,
    )
    systemd.service(
        name="Setup acmetool-redirector service",
        service="acmetool-redirector.service",
        running=True,
        enabled=True,
        restarted=service_file.changed,
        **pyinfra_args,
    )

    old_desired_files = host.get_fact(
        FindFiles,
        path="/var/lib/acme/desired",
        fname=f"{domains[0]}-*",
        **pyinfra_args,
    )
    for file in old_desired_files:
        files.file(
            path=file,
            present=False,
            **pyinfra_args,
        )
    files.template(
        src=importlib.resources.files(__package__).joinpath("desired.yaml.j2"),
        dest=f"/var/lib/acme/desired/{domains[0]}",
        user="root",
        group="root",
        mode="644",
        domains=domains,
        **pyinfra_args,
    )
    if not request_later:
        server.shell(
            name=f"Request certificate for: {' '.join(domains)}",
            commands=["acmetool --batch --xlog.severity=debug reconcile"],
            **pyinfra_args,
        )
