"""DNS resolver diagnostic check."""

from ..utils.base import BaseCheck, CheckResult, Status
from ..utils.macos import run_command_output


class DNSCheck(BaseCheck):
    """Verify DNS configuration and name resolution."""

    def run(self) -> CheckResult:
        resolvers = run_command_output("scutil --dns | grep nameserver | head -5") or ""
        lookup = run_command_output("dscacheutil -q host -a name apple.com | head -3") or ""

        if not resolvers:
            return CheckResult(
                name="DNS",
                status=Status.FAIL,
                details="No DNS resolvers detected",
                recommendation="Configure DNS servers or renew the network lease",
            )

        if not lookup:
            return CheckResult(
                name="DNS",
                status=Status.WARNING,
                details="Resolvers configured but apple.com did not resolve",
                recommendation="Flush DNS cache and verify network connectivity",
                metadata={"resolvers": resolvers},
            )

        return CheckResult(
            name="DNS",
            status=Status.PASS,
            details="DNS resolution succeeded",
            recommendation="DNS is functioning normally",
            metadata={"resolvers": resolvers, "lookup": lookup},
        )
