from zynvu.contracts import EXECUTORS, Requirements


def allowed_executors(requirements: Requirements) -> list[str]:
    """Deny takes precedence. No fallback can widen this set."""
    return sorted(
        set(requirements.allowed_interface_executors) - set(requirements.denied_interface_executors)
    )


def authorize_executor(executor: str, requirements: Requirements) -> None:
    if executor not in EXECUTORS or executor not in allowed_executors(requirements):
        raise PermissionError(f"Executor bloqueado pela política: {executor}")
