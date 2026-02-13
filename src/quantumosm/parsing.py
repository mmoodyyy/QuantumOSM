from __future__ import annotations

from dataclasses import dataclass
import re


@dataclass(frozen=True)
class FileKey:
    model: str          # "SR" or "LR"
    N: int
    J: float
    h: float
    alpha: float | None # present only for LR
    theta: int
    axis: str           # "X", "Y", "Z"

    def tag(self) -> str:
        if self.alpha is None:
            return f"{self.model}_N{self.N}_J{self.J:g}_h{self.h:g}_theta{self.theta}_axis{self.axis}"
        return f"{self.model}_N{self.N}_J{self.J:g}_h{self.h:g}_a{self.alpha:g}_theta{self.theta}_axis{self.axis}"


_BASE_RE = re.compile(
    r"^(?P<model>SR|LR)_DE_"
    r"N=(?P<N>\d+)_"
    r"J=(?P<J>-?\d+\.\d+)_"
    r"h=(?P<h>\d+\.\d+)_"
    r"(?:(?:alpha)=(?P<alpha>\d+\.\d+)_)?"
    r"theta=(?P<theta>\d+)_"
    r"axis=(?P<axis>[XYZ])$"
)


def parse_base_name(base_name: str) -> FileKey:
    """
    Parse a configuration base-name like:
      LR_DE_N=14_J=-1.00_h=0.20_alpha=1.60_theta=3_axis=Z
    or
      SR_DE_N=14_J=-1.00_h=0.20_theta=3_axis=Z
    """
    m = _BASE_RE.match(base_name)
    if not m:
        raise ValueError(f"Unrecognized base name: {base_name}")

    model = m.group("model")
    N = int(m.group("N"))
    J = float(m.group("J"))
    h = float(m.group("h"))
    alpha_s = m.group("alpha")
    alpha = float(alpha_s) if alpha_s is not None else None
    theta = int(m.group("theta"))
    axis = m.group("axis")
    return FileKey(model=model, N=N, J=J, h=h, alpha=alpha, theta=theta, axis=axis)
