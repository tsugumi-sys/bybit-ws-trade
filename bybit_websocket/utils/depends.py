from typing import Optional, Callable, Any


def Depends(dependency: Optional[Callable[..., Any]]) -> Any:
    return _Depends(dependency=dependency)


class _Depends:
    def __init__(self, dependency: Optional[Callable[..., Any]]) -> None:
        self.dependency = dependency