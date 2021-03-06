from . import api
from . import jhu
from . import rki
from . import rki_arcgis


def load(name: str, source: str = "rki"):
    if source == "api":
        return api.load(name)

    if source == "jhu":
        return jhu.load(name)

    if source == "rki":
        return rki.load(name)

    if source == "rki_arcgis":
        return rki_arcgis.load(name)

    raise ValueError(f"invalid source {source}")
