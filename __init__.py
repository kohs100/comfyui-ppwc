"""
@author: Phospholipids
@title: PPWildCard
@nickname: PPWC
@description: This extension offers wildcard prompting works solely in workflow.
"""

import random

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

    def sample_and_replace(self, input, replace, wildcard_list, seed):
        wc_list = wildcard_list.split("\n")
        normalized = []
        for wc in wc_list:
            wc = wc.strip()
            if len(wc) > 0:
                if wc.startswith("#"):
                    continue
                if wc == "NOPROMPT":
                    normalized.append(None)
                else:
                    normalized.append(wc)

        random.seed(seed)
        choice = random.choice(normalized)

        pos = input.find(replace)
        if pos < 0:
            return (input,)
        else:
            prefix, postfix = input[:pos].strip(), input[pos + len(replace) :].strip()

            if postfix.startswith(","):
                postfix = postfix[1:]
            if prefix.endswith(","):
                prefix = prefix[:-1]

            if choice is None:
                return (f"{prefix}, {postfix}",)
            else:
                return (f"{prefix}, {choice}, {postfix}",)


class PPWCBlock:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "prefix": ("STRING", {"forceInput": True}),
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
    FUNCTION = "sample_and_add"

    def sample_and_add(self, prefix, wildcard_list, seed):
        wc_list = wildcard_list.split("\n")
        normalized = []
        for wc in wc_list:
            wc = wc.strip()
            if len(wc) > 0:
                if wc == "NOPROMPT":
                    normalized.append(None)
                else:
                    normalized.append(wc)

        random.seed(seed)
        choice = random.choice(normalized)
        if choice is None:
            return (prefix,)
        else:
            return (prefix + ", " + choice,)


NODE_CLASS_MAPPINGS = {"PPWCBlock": PPWCBlock, "PPWCReplace": PPWCReplace}

NODE_DISPLAY_NAME_MAPPINGS = {
    "PPWCBlock": "Wildcard block",
    "PPWCReplace": "Wildcard replace",
}
