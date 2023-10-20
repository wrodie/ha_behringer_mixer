from .mixer_types import make_mixer


def connect(mixer_type: str, **kwargs):
    """
    Interface entry point. Wraps factory expression and handles errors
    Returns a reference to a mixer
    """
    mixer_class = None
    try:
        mixer_class = make_mixer(mixer_type, **kwargs)
    except ValueError as err:
        raise SystemExit(err) from err
    return mixer_class
