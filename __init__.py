"""
@author: Phospholipids
@title: PPWildCard
@nickname: PPWC
@description: This extension offers wildcard prompting works solely in workflow.
"""

import random

def tokenize(prompt: str) -> list[str]:
    tokens = prompt.split(',')

    fin_tokens = []
    for token in tokens:
        token = token.strip()
        if len(token) == 0:
            continue
        fin_tokens.append(token)

    return fin_tokens

def stringize(tokens: list[None | str]) -> str:
    fin_tokens = []
    for token in tokens:
        if token is None:
            continue
        token = token.strip()
        if len(token) == 0:
            continue
        fin_tokens.append(token)
    return ", ".join(fin_tokens)

class PPWCReplace:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "input": ("STRING", {"forceInput": True}),
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
            },
        }

    CATEGORY = "HSKOWildcard"
    DESCRIPTION = "Description here."

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("output",)
    FUNCTION = "sample_and_replace"

    def sample_and_replace(self, input: str, replace: str, wildcard_list: str, seed: int) -> tuple[int]:
        wc_list = wildcard_list.split("\n")

        normalized: list[str | None] = []
        no_weights: list[float] = []

        for wc in wc_list:
            wc = wc.strip()
            weight = 1
            if len(wc) == 0:
                continue
            if wc.startswith("#"):
                # Comment
                continue
            if wc.startswith("|"):
                # Weight row
                idx_weight_end = wc[1:].find("|")
                weight_str = wc[1:idx_weight_end+1]
                weight = float(weight_str)
                wc = wc[idx_weight_end+2:].strip()
            if wc == "NOPROMPT":
                normalized.append(None)
                no_weights.append(weight)
            else:
                normalized.append(wc)
                no_weights.append(weight)

        random.seed(seed)
        choice = random.choices(normalized, weights=no_weights, k=1)[0]

        rep_tokens = tokenize(replace)
        inp_tokens = tokenize(input)

        assert len(rep_tokens) > 0, "Please enter tokens to replace!"

        found_idxes: list[int | None] = [None for _ in rep_tokens]

        for inp_idx, inp_token in enumerate(inp_tokens):
            if inp_token in rep_tokens:
                rep_idx = rep_tokens.index(inp_token)
                if found_idxes[rep_idx] is None:
                    found_idxes[rep_idx] = inp_idx

        if all(found_idx is not None for found_idx in found_idxes):
            injection_idx = min(found_idxes)
            for found_idx in found_idxes:
                inp_tokens[found_idx] = None
            inp_tokens[injection_idx]

            prefix_tokens = inp_tokens[:injection_idx]
            suffix_tokens = inp_tokens[injection_idx + 1:]

            if choice is None:
                result = stringize(prefix_tokens + suffix_tokens)
            else:
                tokens = tokenize(choice)
                result = stringize(prefix_tokens + tokens + suffix_tokens)
            return (result, )
        else:
            # No replacement happened. Passthrough input
            return (input, )

class PPWCTerminate:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
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
        tokens = input.split(',')

        fin_tokens = []
        for token in tokens:
            token = token.strip()
            if token.startswith("__"):
                continue
            fin_tokens.append(token)

        output = ", ".join(fin_tokens)

        return (output, )

NODE_CLASS_MAPPINGS = {"PPWCReplace": PPWCReplace, "PPWCTerminate": PPWCTerminate}

NODE_DISPLAY_NAME_MAPPINGS = {
    "PPWCReplace": "Wildcard replace",
    "PPWCTerminate": "Wildcard termination",
}
