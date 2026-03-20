"""
@author: Phospholipids
@title: PPWildCard
@nickname: PPWC
@description: This extension offers wildcard prompting works solely in workflow.
"""

import random
from typing import Any, Optional, Callable, Iterable

SINGLETON = object()
class TokenList:
    def __init__(self, tokens: Iterable[str], key: object):
        assert key is SINGLETON, "Init is forbidden"
        self.tokens = list(tokens)

    @staticmethod
    def from_string(prompt: str) -> "TokenList":
        inp_tokens = prompt.split(",")
        tokens: list[str] = []
        for token in inp_tokens:
            token = token.strip()
            if len(token) == 0:
                continue
            tokens.append(token)
        return TokenList(tokens, SINGLETON)

    def filter(self, fn: Callable[[str], bool]) -> "TokenList":
        return TokenList(filter(fn, self.tokens), SINGLETON)

    def is_empty(self):
        return len(self.tokens) == 0

    def to_string(self) -> str:
        return ", ".join(self.tokens)

    def find_all_and_replace(
        self, replace_from: "TokenList", replace_to: Optional["TokenList"]
    ):
        # replace_from 이 비어 있으면 의미가 불명확하므로 no-op 처리
        assert not replace_from.is_empty()

        # replace_from의 각 엔트리가 input의 어느 인덱스를 consume했는지 기록
        consumed_indices: list[int] = [-1 for _ in replace_from.tokens]
        # replace_from의 각 엔트리가 이미 매칭되었는지 추적
        matched: list[bool] = [False for _ in replace_from.tokens]

        # input을 왼쪽부터 스캔하면서, 현재 토큰을 필요로 하는
        # replace_from의 "첫 번째 미매칭 엔트리"에 할당
        for input_idx, input_tok in enumerate(self.tokens):
            for req_idx, req_tok in enumerate(replace_from.tokens):
                if matched[req_idx]:
                    continue
                if input_tok == req_tok:
                    matched[req_idx] = True
                    consumed_indices[req_idx] = input_idx
                    break

        # replace_from의 모든 엔트리가 만족되지 않으면 치환하지 않음
        if not all(matched):
            return

        consumed_index_set = set(consumed_indices)

        res_tokens: list[str] = []
        injected = False

        for input_idx, input_tok in enumerate(self.tokens):
            # consume된 토큰은 결과에서 제거
            if input_idx in consumed_index_set:
                # 가장 첫 consume 지점에서만 replace_to를 삽입
                if not injected and replace_to is not None:
                    res_tokens.extend(replace_to.tokens)
                injected = True
                continue
            res_tokens.append(input_tok)
        self.tokens = res_tokens


class PPWCReplace:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls) -> dict[str, dict[str, Any]]:
        return {
            "required": {
                "replace": (
                    "STRING",
                    {
                        "multiline": False,
                        "dynamicPrompts": False,
                        "tooltip": "Enter a token to replace.",
                    },
                ),
                "wildcard_list": (
                    "STRING",
                    {
                        "multiline": True,
                        "dynamicPrompts": False,
                        "tooltip": "Enter a prompt using wildcard syntax.",
                    },
                ),
                "seed": (
                    "INT",
                    {
                        "default": 0,
                        "min": 0,
                        "max": 0xFFFFFFFFFFFFFFFF,
                        "tooltip": "Determines the random seed to be used for wildcard processing.",
                    },
                ),
                "input": ("STRING", {"forceInput": True}),
            },
        }

    CATEGORY = "HSKOWildcard"
    DESCRIPTION = "Description here."

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("output",)
    FUNCTION = "sample_and_replace"

    def sample_and_replace(
        self, input: str, replace: str, wildcard_list: str, seed: int
    ) -> tuple[str]:
        wc_list = wildcard_list.split("\n")

        replace_rows: list[str | None] = []
        replace_weights: list[float] = []

        for wc in wc_list:
            wc = wc.strip()
            if len(wc) == 0 or wc.startswith("#"):
                continue

            weight = 1
            if wc.startswith("|"):
                # Weight row
                idx_weight_end = wc[1:].find("|")
                weight_str = wc[1 : idx_weight_end + 1]
                weight = float(weight_str)
                wc = wc[idx_weight_end + 2 :].strip()

            # Weight done
            replace_weights.append(weight)
            if wc == "NOPROMPT":
                replace_rows.append(None)
            else:
                replace_rows.append(wc)

        rng = random.Random(seed)
        selected_row = rng.choices(replace_rows, weights=replace_weights, k=1)[0]

        replace_to = None if selected_row is None else TokenList.from_string(selected_row)
        replace_from = TokenList.from_string(replace)
        input_tokens = TokenList.from_string(input)

        assert not replace_from.is_empty(), "Please enter tokens to replace!"

        input_tokens.find_all_and_replace(replace_from, replace_to)

        return (input_tokens.to_string(),)


class PPWCTerminate:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "input": ("STRING", {"forceInput": True}),
            },
        }

    CATEGORY = "HSKOWildcard"
    DESCRIPTION = "Remove all dangling special tokens and normalize prompt."

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("output",)
    FUNCTION = "terminate"

    def terminate(self, input: str) -> tuple[str]:
        output = (
            TokenList.from_string(input)
            .filter(lambda s: not s.startswith("__"))
            .to_string()
        )
        return (output,)


NODE_CLASS_MAPPINGS: dict[str, Any] = {
    "PPWCReplace": PPWCReplace,
    "PPWCTerminate": PPWCTerminate,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "PPWCReplace": "Wildcard replace",
    "PPWCTerminate": "Wildcard termination",
}
