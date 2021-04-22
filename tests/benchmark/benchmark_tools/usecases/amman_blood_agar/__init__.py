# coding: utf8
# benchmark_tools.amman

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
# Author: Ellen Sebastian

from ...interfaces import *
import pandas as pd

FIRST_ATB_NAME_COLUMN_ZERO_BASED = 5


class AST_annotation_Amman_blood_agar(AST_annotation):
    def __init__(self, guiID, df_slice):
        self.ast_id = guiID
        self.species = df_slice['Species']
        self.expert_system_status = []
        self.sample_date = df_slice['Specimen date']
        self.atb_names = df_slice.index[FIRST_ATB_NAME_COLUMN_ZERO_BASED:].tolist()
        self.sir_values = None
        self.raw_sir_values = None
        self.diameters = [float(i) for i in df_slice[FIRST_ATB_NAME_COLUMN_ZERO_BASED:].tolist()]
        self.sample_type = df_slice['Specimen type']


class Annotations_set_Amman_blood_agar(Annotations_set):
    def __init__(self, annotations_file):
        self.file = annotations_file
        self.diam_df = Annotations_set_Amman_blood_agar.read_annotation_file(
            self.file)
        self.atb_names = self.diam_df.keys()[FIRST_ATB_NAME_COLUMN_ZERO_BASED:]
        self.ast_ids = list(self.diam_df.index)

    @staticmethod
    def read_annotation_file(path):
        df = pd.read_csv(path, sep=',', index_col="Picture name")
        return df

    def get_ast(self, guiID):
        try:
            df_slice = self.diam_df.loc[guiID]
        except:
            raise KeyError("ID not found")

        return AST_annotation_Amman_blood_agar(guiID, df_slice)

    def get_ast_slice(self, slice_instance):
        out = []
        start = slice_instance.start
        stop = slice_instance.stop
        step = slice_instance.step if (slice_instance.step is not None) else 1
        for i in range(start, stop, step):
            if i in self.ast_ids:
                out.append(self.get_ast(i))
        return out
