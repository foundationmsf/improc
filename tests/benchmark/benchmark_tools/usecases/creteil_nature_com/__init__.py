# benchmark_tools.creteil

# Copyright 2019 Fondation Medecins Sans Frontières https://fondation.msf.fr/
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# This file is part of the ASTapp image processing library

from ...interfaces import *
from collections import Mapping
from os import path
import pandas as pd
from collections import defaultdict


class AST_annotation_Creteil_nature_com(AST_annotation):
    def __init__(self, atb_lines):
        self.atb_names = []
        self.diameters = []
        for atb_line in atb_lines:
            gui_id, atb, improc, _, _, _, _, image_name, sirscan, species = atb_line[0:10]
            self.ast_id = image_name
            self.species = species
            self.expert_system_status = []
            self.atb_names.append(atb)
            self.sir_values = None
            self.raw_sir_values = None
            self.diameters.append(sirscan)
            self.sample_type = None
            self.sample_date = None


class Annotations_set_Creteil_nature_com(Annotations_set):

    def __init__(self, annotation_folder):
        one_atb_per_line = path.join(annotation_folder, "results and control HM.csv")
        df = pd.read_csv(one_atb_per_line, sep=',')
        self.atb_lines_dict = {}
        for _, atb_line in df.iterrows():
            gui_id = atb_line[7]
            if not gui_id in self.atb_lines_dict:
                self.atb_lines_dict[gui_id] = []
            self.atb_lines_dict[gui_id].append(atb_line)
        self.ast_ids = self.atb_lines_dict.keys()

    def get_ast(self, guiID):
        try:
            atb_lines = self.atb_lines_dict[guiID]
        except:
            raise KeyError("ID not found")

        return AST_annotation_Creteil_nature_com(atb_lines)

    def get_ast_slice(self, slice_instance):
        out = []
        start = slice_instance.start
        stop = slice_instance.stop
        step = slice_instance.step if (slice_instance.step is not None) else 1
        for i in range(start, stop, step):
            if i in self.ast_ids:
                out.append(self.get_ast(i))
        return out
