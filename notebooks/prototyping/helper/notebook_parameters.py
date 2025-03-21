"""TODO"""

# from __future__ import annotations

# # import json
# import os

# MCS_DATA_DIR_PATH = os.path.join(
#     os.path.dirname(os.path.realpath(__file__)), "..", "..", "..", "mcs_data"
# )


# class NotebookParamPkg:
#     """TODO"""

#     def __init__(self: NotebookParamPkg, param_json_path: str):

#         with open(param_json_path, "r", encoding="utf-8") as json_in:

#             self.configure_scan = self._read_str_json_file(os.path.join())

#     def _read_str_json_file(self: NotebookParamPkg, json_path: str) -> str:
#         """
#         Reads json file as str.

#         :param json_path: path to json
#         :returns: str of json contents
#         """
#         with open(json_path, "r", encoding="utf-8") as json_in:
#             return json_in.read()
